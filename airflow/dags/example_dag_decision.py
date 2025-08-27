from airflow.sdk import dag, task
from datetime import datetime
import random

@dag(schedule='@daily', start_date=datetime(2024, 1, 1), catchup=False)
def example_dag_decision():

    @task
    def check_api():
        print("API is reachable.")
        return True

    @task
    def extract_data():
        data = [random.randint(0, 10) for _ in range(5)]
        print(f"Extracted data: {data}")
        return data

    @task
    def clean_data(raw_data: list[int]):
        cleaned = [x for x in raw_data if x > 2]
        print(f"Cleaned data: {cleaned}")
        return cleaned

    @task.branch
    def decide_storage_strategy(cleaned_data: list[int]):
        if len(cleaned_data) >= 3:
            return "store_to_dwh"
        return "store_locally"

    @task.bash
    def store_to_dwh():
        return "echo 'Sending to Data Warehouse'"

    @task.bash
    def store_locally():
        return "echo 'Storing locally'"

    # DAG flow
    raw_data = extract_data()
    cleaned = clean_data(raw_data)
    decision = decide_storage_strategy(cleaned)
    check_api() >> decision >> [store_to_dwh(), store_locally()]

example_dag_decision()