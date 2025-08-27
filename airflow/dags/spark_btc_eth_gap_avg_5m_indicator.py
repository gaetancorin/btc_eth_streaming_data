from airflow.sdk import dag, task
from airflow.providers.apache.spark.hooks.spark_connect import SparkConnectHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyspark.sql import SparkSession, functions
from datetime import datetime
import pandas as pd
import logging

@dag(
    start_date=datetime(2025, 1, 1),
    # schedule="* * * * *",  # chaque minute
    schedule=None,
    catchup=False
)
def spark_btc_eth_gap_avg_5m_indicator():

    @task
    def compute_with_spark():
        # --- Connect Spark to Airflow ---
        hook = SparkConnectHook(conn_id="my_spark")
        conn = hook.get_connection(conn_id="my_spark")

        master_url = f"spark://{conn.host}:{conn.port}"
        deploy_mode = conn.extra_dejson.get("deploy-mode", "client")

        spark = SparkSession.builder \
            .master(master_url) \
            .appName("BTC_ETH_Diff_MapReduce") \
            .config("spark.submit.deployMode", deploy_mode) \
            .getOrCreate()

        # --- Connect Postgres to Airflow---
        pg_hook = PostgresHook(postgres_conn_id="my_postgres")
        pg_conn = pg_hook.get_conn()
        cur = pg_conn.cursor()

        # --- Download BTC and ETH from Postgres ---
        btc_df = pg_hook.get_pandas_df("""
            SELECT *
            FROM btc_usd
            WHERE datetime_utc > NOW() - INTERVAL '5 minutes'
            ORDER BY datetime_utc;
        """)
        print(f"5 last values into BTC_USD postgres\n{btc_df}")
        eth_df = pg_hook.get_pandas_df("""
            SELECT *
            FROM eth_usd
            WHERE datetime_utc > NOW() - INTERVAL '5 minutes'
            ORDER BY datetime_utc;
        """)
        print(f"5 last values into ETH_USD postgres\n{eth_df}")

        if btc_df.empty and eth_df.empty:
            logging.info("No new BTC/ETH data to process")
            return

        # --- Merge BTC and ETH at the same datetime ---
        btc_df = btc_df[["price", "datetime_utc"]].rename(columns={"price":"btc_price"})
        eth_df = eth_df[["price", "datetime_utc"]].rename(columns={"price": "eth_price"})
        btc_eth_merged = pd.merge(btc_df, eth_df, on="datetime_utc", how="inner")
        print(f"BTC_ETH_MERGED\n{btc_eth_merged}")
        if btc_eth_merged.empty:
            logging.info("no Common Datetimes between BTC and ETH")
            return

        # --- Convert Pandas -> Spark ---
        btc_eth_sdf = spark.createDataFrame(btc_eth_merged)
        btc_eth_sdf.show()

        # --- MAP: calculate BTC - ETH differences ---
        btc_eth_sdf = btc_eth_sdf.withColumn("diff_btc_eth", functions.col("btc_price") - functions.col("eth_price"))
        btc_eth_sdf = btc_eth_sdf.withColumn("diff_btc_eth",functions.round(functions.col("diff_btc_eth"), 4))
        print(f"Calculate BTC - ETH differences")
        btc_eth_sdf.show()

        # --- REDUCE: calculate average of the last 5 BTC-ETH differences ---
        avg_diff = btc_eth_sdf.agg(functions.avg("diff_btc_eth").alias("avg_diff_btc_eth_5m")).collect()[0]
        avg_diff = float(avg_diff["avg_diff_btc_eth_5m"])
        avg_diff = round(avg_diff, 4)
        print(f"Average diff_btc_eth over last 5 rows: {avg_diff}")

        # --- Keep last row, add avg of BTC-ETH differences ---
        last_row = btc_eth_sdf.orderBy(functions.desc("datetime_utc")).limit(1)
        last_row_with_avg = last_row.withColumn("avg_diff_btc_eth_5m", functions.lit(avg_diff))
        last_row_with_avg.show()
        print(f"Last row with avg of BTC-ETH differences\n{last_row_with_avg}")

        # --- Load into Postgres with a Spark Dataframe ---
        rows = last_row_with_avg.collect()
        for row in rows:
            cur.execute("""
                INSERT INTO btc_eth_gap_avg_5m_indicator(btc_eth_gap_avg_5m, datetime_utc)
                VALUES (%s, %s)
                ON CONFLICT (datetime_utc) DO NOTHING;
            """, (float(row["avg_diff_btc_eth_5m"]), row["datetime_utc"]))
        print("SUCCESS Load row into postgres table btc_eth_gap_avg_5m_indicator")

        pg_conn.commit()
        cur.close()
        pg_conn.close()
        spark.stop()

    compute_with_spark()

spark_btc_eth_gap_avg_5m_indicator()