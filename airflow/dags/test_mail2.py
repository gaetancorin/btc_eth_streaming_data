from airflow.sdk import dag, task
from datetime import datetime
from airflow.providers.smtp.operators.smtp import EmailOperator

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False
)
def test_email2():

    @task
    def send_test_email():
        EmailOperator(
            task_id="send_test_email",
            to="gaetan.corin@menaps.com",
            html_content="Content of email",
            subject="Test Airflow SMTP",
            conn_id="my_email"
        )  # Airflow exécutera automatiquement ce task

    send_test_email()

test_email2()