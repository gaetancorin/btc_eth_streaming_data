import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

smtp_user = os.getenv("SMTP_USER") # sender email (prod only with gmail)
smtp_pass = os.getenv("SMTP_PASS") # sender password application (prod only with gmail)

smtp_server = os.getenv("SMTP_SERVER") # receiver SMTP server
smtp_port = int(os.getenv("SMTP_PORT")) # receiver SMTP port (587=TLS, 465=SSL, 25=not secure)
receiver = os.getenv("RECEIVER") # receiver email

def get_parameter():
    print("Value of smtp_user:", smtp_user)
    print("Value of smtp_pass:", smtp_pass)
    print("Value of smtp_server:", smtp_server)
    print("Value of smtp_port:", smtp_port)
    print("Value of receiver:", receiver)

def send_failure_tasks_email(dag_id, run_id, dag_run_url, tasks_to_show):
    tasks_html = ""
    for task_name, task_result in tasks_to_show.items():
        if task_result == "SUCCESS":
            tasks_html += f"<li>Task {task_name}  : {task_result} ✅</li>"
        else:
            tasks_html += f"<li>Task {task_name}  : {task_result} ❌</li>"

    sender = smtp_user
    # Create message
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"🚨Rapport d'erreur de task(s)🚨 : {dag_id}"
    body = f"""\
    <html>
      <body>
        <p>
        Task(s) échouée(s) sur le DAG:  <b>{dag_id}</b> 😬😱😭<br>
        </p>
        <p>
        Liste des tasks:
        {tasks_html}
        </p>
        <p>
        URL du Run: <a href="{dag_run_url}">{dag_run_url}</a> 🧐<br>
        </p>
        ID du Run: {run_id}<br>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        if smtp_port == 587:
            server.starttls()  # securise TLS
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, receiver, msg.as_string())
        else:
            # when testing with mailhog, no need to connect sender(with user password)
            server.sendmail(receiver, receiver, msg.as_string())
    print("✅ Email send successfully at", receiver)
