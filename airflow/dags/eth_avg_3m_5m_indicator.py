from airflow.sdk import dag, task
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
from utils.failure_tasks_manager import notify_failure_tasks

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *", # each minutes
    #schedule=None,
    catchup=False, # not recover old launch
    is_paused_upon_creation=False
)
def eth_avg_3m_5m_indicator():

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
            logging.error("NO NEW DATA TO PROCESS")
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
            logging.error("DF EMPTY, NOTHING TO LOAD")
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
        logging.info(f"Postgres table eth_usd_avg_indicator loaded row :\n{last_row}")

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def task_fail_notifier(tasks_dict: dict):
        notify_failure_tasks(tasks_dict)
        raise Exception("✅ TASK FAIL NOTIFIER EXECUTED SUCESSFULLY !\n ✅ But need to raising Exception to force Red DAG failure")

    # flow du DAG
    df = extract_data()
    transformed_df = transform_data(df)
    t3 = load_data(transformed_df)

    [df, transformed_df, t3] >> task_fail_notifier({"extract_data": df, "transform_data": transformed_df, "load_data": t3})

eth_avg_3m_5m_indicator()