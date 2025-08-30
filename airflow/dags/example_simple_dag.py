from airflow.sdk import dag, task
from datetime import datetime
import logging

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None
)
def example_simple_dag():
    @task
    def my_task():
        logging.info(f"THE TASK IS RUNNING !")
        return 'sucess'

    my_task()
example_simple_dag()