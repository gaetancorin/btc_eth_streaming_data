from airflow.sdk import dag, task
from airflow.providers.apache.spark.hooks.spark_connect import SparkConnectHook
from pyspark.sql import SparkSession
from datetime import datetime

@dag(
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False
)
def example_spark_even_sum():

    @task
    def run_even_sum():
        # Récupérer la connexion Airflow
        hook = SparkConnectHook(conn_id="my_spark")
        conn = hook.get_connection(conn_id="my_spark")

        # Afficher les infos pour debug
        print(f"Host: {conn.host}")
        print(f"Port: {conn.port}")
        print(f"Extra: {conn.extra_dejson}")

        # Construire l’URL Spark
        master_url = f"spark://{conn.host}:{conn.port}"
        deploy_mode = conn.extra_dejson.get("deploy-mode", "client")

        # Créer une SparkSession
        spark = SparkSession.builder \
            .master(master_url) \
            .appName("EvenSum") \
            .config("spark.submit.deployMode", deploy_mode) \
            .getOrCreate()

        # Exemple simple (somme des pairs)
        data = [(i,) for i in range(1, 1000001)]
        df = spark.createDataFrame(data, ["number"])
        even_sum = df.filter(df["number"] % 2 == 0).groupBy().sum("number")
        even_sum.show()

        spark.stop()

    run_even_sum()

example_spark_even_sum()
