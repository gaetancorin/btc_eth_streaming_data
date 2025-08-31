import logging
from airflow.sdk import get_current_context

def get_failure_context():
    logging.info("INSIDE FAILURE CONTEXT")
    # context = get_current_context()
    # ti = context["ti"]
    # dag_id = ti.dag_id
    # task_id = ti.task_id
    # run_id = ti.run_id
    # try_number = ti.try_number
    # map_index = ti.map_index
    # logging.error(
    #     f"❌ Failure detected!\n"
    #     f"Dag: {dag_id}, Task: {task_id}, Run: {run_id}, Try: {try_number}, Map Index: {map_index}"
    # )