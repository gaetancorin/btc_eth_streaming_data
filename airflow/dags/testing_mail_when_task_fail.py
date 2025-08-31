from airflow.sdk import DAG, task
from datetime import datetime
import logging
from airflow.sdk import get_current_context
from airflow.utils.trigger_rule import TriggerRule
from utils.failure_context import get_failure_context
from utils.email_alert import test_email_sending

with DAG(
    dag_id="testing_mail_when_task_fail",
    start_date=datetime(2024, 1, 1),
    schedule=None
) as dag:

    @task
    def my_task():
        logging.info(f"THE TASK IS RUNNING !")
        return 'sucess'

    @task
    def always_fail():
        #return "ok"
        raise Exception("❌ This task fails on purpose!")

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def when_fail():

        # context = get_current_context()
        # logging.info(f"PRINT DAG PARAMETER:\n {context}")
        # ti = context["ti"]
        # dag_id = ti.dag_id
        # task_id = ti.task_id
        # logging.info(f"PRINT PARAMETER:\n {dag_id}.{task_id}")

        get_failure_context()
        test_email_sending()


    my_task()
    always_fail()
    list(dag.tasks) >> when_fail()
