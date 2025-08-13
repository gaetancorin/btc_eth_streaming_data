from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def dire_bonjour():
    print("👋 Bonjour depuis mon premier DAG appelé first_dag !")

default_args = {
    'owner': 'moi',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='old_dag_syntax',  # Ce nom doit être unique
    default_args=default_args,
    description='Mon premier DAG fait main',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['début'],
) as dag:

    tache_bonjour = PythonOperator(
        task_id='dire_bonjour',
        python_callable=dire_bonjour,
    )

    tache_bonjour