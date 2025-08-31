from airflow.sdk import dag, task
from datetime import datetime
import logging
from airflow.sdk import get_current_context
from airflow.utils.trigger_rule import TriggerRule

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None
)
def print_dag_parameters_if_task_fail():

    @task
    def my_task():
        logging.info(f"THE TASK IS RUNNING !")
        return 'sucess'

    @task
    def always_fail():
        #return "ok"
        raise Exception("❌ This task fails on purpose!")

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def watcher(t1, t2):
        logging.info(f"t1={t1}")
        logging.info(f"t2={t2}")
        context = get_current_context()
        logging.info(f"PRINT DAG PARAMETER:\n {context}")
        ti = context["ti"]
        dag_id = ti.dag_id
        task_id = ti.task_id
        run_id = ti.run_id
        try_number = ti.try_number
        map_index = ti.map_index
        logging.info(f"PRINT PARAMETER:\n {dag_id}.{task_id}, Run: {run_id}, Try: {try_number}, Map Index: {map_index}")

    t1 = my_task()
    t2 = always_fail()
    [t1, t2] >> watcher(t1, t2)

print_dag_parameters_if_task_fail()