from airflow.sdk import dag, task
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *", # each minutes
    catchup=False # not recover old launch
)
def eth_avg_indicator():

    @task
    def extract_data():
        hook = PostgresHook(postgres_conn_id="my_postgres")
        sql = """
            SELECT *
            FROM eth_usd
            WHERE datetime_utc > NOW() - INTERVAL '6 minutes'
            ORDER BY datetime_utc;
        """
        df = hook.get_pandas_df(sql)
        logging.info(f"Extracted {len(df)} rows")
        logging.info(f"\n {df}")
        df['datetime_utc'] = df['datetime_utc'].astype(str)
        return df

    @task
    def transform_data(df: pd.DataFrame):
        if df.empty:
            print("No new data to process")
            return df
        # calcul des moyennes mobiles
        df["price_avg_3m"] = df["price"].rolling(window=3).mean()
        df["price_avg_5m"] = df["price"].rolling(window=5).mean()

        df = df.replace({np.nan: None})
        logging.info(f"Average calculated on 3 and 5 minutes:\n {df}")
        return df

    @task
    def load_data(df: pd.DataFrame):
        if df.empty or df.dropna(subset=["price_avg_3m"]).empty:
            logging.info("DF empty, Nothing to load")
            return
        hook = PostgresHook(postgres_conn_id="my_postgres")
        conn = hook.get_conn()
        cur = conn.cursor()

        last_row = df.iloc[[-1]]
        for _, row in last_row.iterrows():
            cur.execute("""
                INSERT INTO eth_usd_avg_indicator(eth_usd_id, price_avg_3m, price_avg_5m, datetime_utc)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (datetime_utc) DO NOTHING;
            """, (row["id"], row["price_avg_3m"], row["price_avg_5m"], row["datetime_utc"]))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Postgres table eth_usd_avg_indicator loaded row :\n{last_row}")

    # flow du DAG
    df = extract_data()
    transformed_df = transform_data(df)
    load_data(transformed_df)

eth_avg_indicator()