from airflow.sdk import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

@dag(
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False  # not recover old launch
)
def spark_even_sum_manual():

    spark_even_sum_task = SparkSubmitOperator(
        task_id="spark_even_sum_manual",
        conn_id="sparkmanual",
        application="/opt/airflow/dags/spark_files/even_sum.py",  # script PySpark
        name="spark_even_sum_manual",
        verbose=True
    )

spark_even_sum_manual()