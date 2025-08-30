from airflow.sdk import dag, task
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

smtp_user = os.getenv("SMTP_USER") # sender email
smtp_pass = os.getenv("SMTP_PASS") # sender password application

smtp_server = os.getenv("SMTP_SERVER") # receiver SMTP server
smtp_port = int(os.getenv("SMTP_PORT")) # receiver SMTP port (587=TLS, 465=SSL, 25=not secure)
receiver = os.getenv("RECEIVER") # receiver email

@dag(
    start_date=datetime(2024, 1, 1),
    #schedule="* * * * *",  # each minute
    schedule=None,
    catchup=False  # not recover old launch
)
def test_function_email():
    @task
    def get_parameter():
        print("Value of smtp_user:", smtp_user)
        print("Value of smtp_pass:", smtp_pass)
        print("Value of smtp_server:", smtp_server)
        print("Value of smtp_port:", smtp_port)
        print("Value of receiver:", receiver)

    @task
    def test_email_sending():
        sender = smtp_user

        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "✅ Test SMTP Python"
        title = "Bonjour Gaetan,\n\nCeci est un test SMTP envoyé en Python."
        body = """\
        <html>
          <body>
            <p>Bonjour Gaetan,<br><br>
               Ceci est un <b>test SMTP</b> envoyé en Python. 🚀<br>
            </p>
          </body>
        </html>
        """
        msg.attach(MIMEText(title, "plain"))
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_port == 587:
                server.starttls()  # securise TLS
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email send successfully at", receiver)

    get_parameter()
    test_email_sending()

test_function_email()