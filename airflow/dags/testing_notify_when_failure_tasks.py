from airflow.sdk import dag, task
from datetime import datetime
import logging
from airflow.utils.trigger_rule import TriggerRule
from utils.failure_tasks_manager import notify_failure_tasks

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None
)
def testing_notify_when_failure_tasks():

    @task
    def my_task():
        logging.info(f"THE TASK IS RUNNING !")
        return 'sucess'

    @task
    def always_fail():
        #return "ok"
        raise Exception("❌ This task fails on purpose!")

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def task_fail_notifier(tasks_dict: dict):
        notify_failure_tasks(tasks_dict)

    t1 = my_task()
    t2 = always_fail()
    [t1, t2] >> task_fail_notifier({"my_task": t1, "always_fail": t2})

testing_notify_when_failure_tasks()
