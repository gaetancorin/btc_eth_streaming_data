from airflow.sdk import dag, task
from airflow.providers.apache.spark.hooks.spark_connect import SparkConnectHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyspark.sql import SparkSession, functions
from datetime import datetime
import logging
from airflow.utils.trigger_rule import TriggerRule
from utils.failure_tasks_manager import notify_failure_tasks
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *",  # each minute
    #schedule=None,
    catchup=False,
    is_paused_upon_creation=False
)
def spark_btc_eth_gap_avg_5m_indicator():

    @task
    def extract_btc_eth_data_on_postgres():
        # --- Connect Postgres to Airflow---
        pg_hook = PostgresHook(postgres_conn_id="my_postgres")

        # --- Download BTC and ETH from Postgres ---
        btc_df = pg_hook.get_pandas_df("""
                   SELECT *
                   FROM btc_usd
                   WHERE datetime_utc > NOW() - INTERVAL '6 minutes'
                   ORDER BY datetime_utc;
               """)
        logging.info(f"5 last values into BTC_USD postgres\n{btc_df}")
        eth_df = pg_hook.get_pandas_df("""
                   SELECT *
                   FROM eth_usd
                   WHERE datetime_utc > NOW() - INTERVAL '6 minutes'
                   ORDER BY datetime_utc;
               """)
        logging.info(f"5 last values into ETH_USD postgres\n{eth_df}")
        btc_df["datetime_utc"] = btc_df["datetime_utc"].astype(str)
        eth_df["datetime_utc"] = eth_df["datetime_utc"].astype(str)
        if btc_df.empty and eth_df.empty:
            logging.error("NO NEW BTC/ETH DATA TO PROCESS")
            return {"btc_data": None,"eth_data": None}
        return {
            "btc_data": btc_df.to_dict(orient="list"),
            "eth_data": eth_df.to_dict(orient="list")
        }

    @task
    def merge_btc_eth_on_datetime(btc_eth_data):
        btc_df = pd.DataFrame(btc_eth_data["btc_data"])
        eth_df = pd.DataFrame(btc_eth_data["eth_data"])
        if btc_df.empty or eth_df.empty:
            logging.error("MISSING BTC or ETH DATA TO PROCESS")
            return None
        # --- Merge BTC and ETH at the same datetime ---
        btc_df = btc_df[["price", "datetime_utc"]].rename(columns={"price": "btc_price"})
        eth_df = eth_df[["price", "datetime_utc"]].rename(columns={"price": "eth_price"})
        btc_eth_merged = pd.merge(btc_df, eth_df, on="datetime_utc", how="inner")
        logging.info(f"BTC_ETH_MERGED\n{btc_eth_merged}")
        if btc_eth_merged.empty:
            logging.info("no Common Datetimes between BTC and ETH")
            return
        return btc_eth_merged

    @task
    def calculate_btc_eth_gap_and_avg_with_spark(btc_eth_merged):
        if btc_eth_merged is None:
            logging.error("NO NEW BTC/ETH DATA WITH SAME DATETIME TO PROCESS")
            return None
        # --- Connect Spark to Airflow ---
        hook = SparkConnectHook(conn_id="my_spark")
        conn = hook.get_connection(conn_id="my_spark")
        master_url = f"spark://{conn.host}:{conn.port}"
        deploy_mode = conn.extra_dejson.get("deploy-mode", "client")
        spark = SparkSession.builder \
            .master(master_url) \
            .appName("BTC_ETH_gap_and_avg") \
            .config("spark.submit.deployMode", deploy_mode) \
            .getOrCreate()

        # --- Convert DF Pandas -> Spark ---
        btc_eth_sdf = spark.createDataFrame(btc_eth_merged)
        btc_eth_sdf.show(truncate=False)

        # --- MAP: calculate GAP with BTC - ETH differences ---
        gap_btc_eth_sdf = btc_eth_sdf.withColumn("gap_btc_eth", functions.col("btc_price") - functions.col("eth_price"))
        gap_btc_eth_sdf = gap_btc_eth_sdf.withColumn("gap_btc_eth", functions.round(functions.col("gap_btc_eth"), 4))
        logging.info(f"Calculate GAP with BTC - ETH differences")
        gap_btc_eth_sdf.show(truncate=False)

        # --- REDUCE: calculate AVERAGE of GAPS(the last 5 BTC-ETH differences) ---
        avg_gap_5m_value = gap_btc_eth_sdf.agg(functions.avg("gap_btc_eth").alias("avg_gap_btc_eth_5m")).collect()[0]
        avg_gap_5m_value = float(avg_gap_5m_value["avg_gap_btc_eth_5m"])
        avg_gap_5m_value = round(avg_gap_5m_value, 4)
        logging.info(f"Average of GAPS btc_eth over last 5 rows: {avg_gap_5m_value}")

        # --- Keep last row, add avg of BTC-ETH differences ---
        last_row = gap_btc_eth_sdf.orderBy(functions.desc("datetime_utc")).limit(1)
        last_row_with_avg = last_row.withColumn("avg_gap_btc_eth_5m", functions.lit(avg_gap_5m_value))
        logging.info(f"Last row with AVG of BTC-ETH GAP 5 min")
        last_row_with_avg.show(truncate=False)

        last_row_with_avg = last_row_with_avg.toPandas()
        logging.info(last_row_with_avg)
        spark.stop()
        return last_row_with_avg

    @task
    def load_row_to_postgres(df_last_row_with_avg):
        if df_last_row_with_avg is None:
            logging.error("NO DATA RECEIVE")
            return None
        # --- Connect Postgres to Airflow---
        pg_hook = PostgresHook(postgres_conn_id="my_postgres")
        pg_conn = pg_hook.get_conn()
        cur = pg_conn.cursor()

        # --- Load Pandas row into Postgres  ---
        for _, row in df_last_row_with_avg.iterrows():
            cur.execute("""
                        INSERT INTO btc_eth_gap_avg_5m_indicator(btc_eth_gap_avg_5m, datetime_utc)
                        VALUES (%s, %s)
                        ON CONFLICT (datetime_utc) DO NOTHING;
                    """, (row["avg_gap_btc_eth_5m"],  row["datetime_utc"]))
        pg_conn.commit()
        cur.close()
        pg_conn.close()
        logging.info(f"Postgres table btc_eth_gap_avg_5m_indicator loaded row :\n{df_last_row_with_avg}")
        return "done"

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def task_fail_notifier(tasks_dict: dict):
        notify_failure_tasks(tasks_dict)


    btc_eth_data = extract_btc_eth_data_on_postgres()
    btc_eth_merged = merge_btc_eth_on_datetime(btc_eth_data)
    df_last_row_with_avg = calculate_btc_eth_gap_and_avg_with_spark(btc_eth_merged)
    t4 = load_row_to_postgres(df_last_row_with_avg)


    [btc_eth_data, btc_eth_merged, df_last_row_with_avg, t4] >> task_fail_notifier(
        {"extract_btc_eth_data_on_postgres": btc_eth_data, "merge_btc_eth_on_datetime": btc_eth_merged, "calculate_btc_eth_gap_and_avg_with_spark": df_last_row_with_avg, "load_row_to_postgres": t4})

spark_btc_eth_gap_avg_5m_indicator()