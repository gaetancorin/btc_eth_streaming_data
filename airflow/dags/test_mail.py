from airflow.sdk import dag, task
from datetime import datetime
from airflow.providers.smtp.operators.smtp import EmailOperator

@dag(
    start_date=datetime(2024, 1, 1),
    #schedule="* * * * *",  # each minute
    schedule=None,
    catchup=False  # not recover old launch
)
def test_email():

    @task
    def test_email_sending():
        email_task = EmailOperator(
            conn_id= "my_email",
            task_id="send_test_email",
            to="gaetan.corin@menaps.com",
            html_content="content of email",
            subject = "Test Airflow SMTP",
        )
        email_task.execute(context={})
        return 1

    test_email_sending()

test_email()