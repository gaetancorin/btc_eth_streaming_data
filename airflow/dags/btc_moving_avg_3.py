from airflow.sdk import dag, task
from datetime import datetime
import pandas as pd
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *", # each minutes
    catchup=False # not recover old launch
)
def btc_moving_avg_3():

    @task
    def extract_data():
        hook = PostgresHook(postgres_conn_id="my_postgres")
        sql = """
            SELECT *
            FROM btc_usd
            WHERE recorded_utc_at > NOW() - INTERVAL '10 minutes'
            ORDER BY recorded_utc_at;
        """
        df = hook.get_pandas_df(sql)
        logging.info(f"Extracted {len(df)} rows")
        df['recorded_utc_at'] = df['recorded_utc_at'].astype(str)
        return df.to_dict()

    # @task
    # def transform_data(raw_data: dict):
    #     df = pd.DataFrame(raw_data)
    #
    #     if df.empty:
    #         print("No new data to process")
    #         return df.to_dict()
    #
    #     # calcul des moyennes mobiles
    #     df["ma3"] = df["value"].rolling(window=3).mean()
    #     df["ma5"] = df["value"].rolling(window=5).mean()
    #
    #     print(df.tail())
    #     return df.to_dict()
    #
    # @task
    # def load_data(transformed: dict):
    #     df = pd.DataFrame(transformed)
    #     if df.empty:
    #         print("Nothing to load")
    #         return
    #
    #     hook = PostgresHook(postgres_conn_id="my_postgres")
    #     conn = hook.get_conn()
    #     cur = conn.cursor()
    #
    #     for _, row in df.iterrows():
    #         cur.execute("""
    #             INSERT INTO btc_eth_moving_avg(timestamp, value, ma3, ma5)
    #             VALUES (%s, %s, %s, %s)
    #             ON CONFLICT (timestamp) DO NOTHING;
    #         """, (row["timestamp"], row["value"], row["ma3"], row["ma5"]))
    #
    #     conn.commit()
    #     cur.close()
    #     conn.close()
    #     print(f"Loaded {len(df)} rows into btc_eth_moving_avg")

    # flow du DAG
    raw_data = extract_data()
    # transformed = transform_data(raw_data)
    # load_data(transformed)

btc_moving_avg_3()