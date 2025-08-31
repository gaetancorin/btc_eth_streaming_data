from airflow.sdk import dag, task
from datetime import datetime
import logging
from airflow.sdk import get_current_context
from airflow.utils.trigger_rule import TriggerRule
from utils.failure_context import get_failure_context
from utils.email_alert import test_email_sending

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None
)
def testing_mail_when_task_fail():

    @task
    def my_task():
        logging.info(f"THE TASK IS RUNNING !")
        return 'sucess'

    @task
    def always_fail():
        #return "ok"
        raise Exception("❌ This task fails on purpose!")

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def when_fail(t1, t2):
        logging.info(f"t1={t1}")
        logging.info(f"t2={t2}")

        # context = get_current_context()
        # logging.info(f"PRINT DAG PARAMETER:\n {context}")
        # ti = context["ti"]
        # dag_id = ti.dag_id
        # task_id = ti.task_id
        # logging.info(f"PRINT PARAMETER:\n {dag_id}.{task_id}")

        # get_failure_context()
        # test_email_sending()

    t1 = my_task()
    t2 = always_fail()
    [t1, t2] >> when_fail(t1, t2)

testing_mail_when_task_fail()
