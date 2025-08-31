import logging
import logging
from airflow.sdk import get_current_context
from utils.failure_tasks_email import send_failure_tasks_email
# Documentation says do not use relative path
# https://airflow.apache.org/docs/apache-airflow/3.0.3/administration-and-deployment/modules_management.html#don-t-use-relative-imports

def notify_failure_tasks(tasks_dict: dict):
    tasks_to_show = {}
    for task_name, task_result in tasks_dict.items():
        task_result = "FAILED" if task_result is None else "SUCCESS"
        logging.info(f"TASK {task_name} = {task_result}")
        tasks_to_show[task_name] = task_result
    dag_id, run_id, dag_run_url = get_failure_tasks_context()
    send_failure_tasks_email(dag_id, run_id, dag_run_url, tasks_to_show)

def get_failure_tasks_context():
    context = get_current_context()
    ti = context["ti"]
    dag_id = ti.dag_id.upper()
    logging.info(f"dag_id: {dag_id}")
    run_id = ti.run_id
    logging.info(f"run_id: {run_id}")
    dag_run_url = ti.log_url.split("/tasks/")[0]
    logging.info(f"dag_run_url: {dag_run_url}")
    return dag_id, run_id, dag_run_url