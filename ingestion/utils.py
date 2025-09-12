import os
import csv
from datetime import datetime, timezone
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
smtp_user = os.getenv("SMTP_USER") # sender email (prod only, with gmail)
smtp_pass = os.getenv("SMTP_PASS") # sender password application (prod only, with gmail)

smtp_server = os.getenv("SMTP_SERVER") # receiver SMTP server
smtp_port = int(os.getenv("SMTP_PORT")) # receiver SMTP port (587=TLS, 465=SSL, 25=not secure)
receiver = os.getenv("RECEIVER") # receiver email

def compare_utc_date(date_before, new_date):
    diff_seconds = abs((new_date - date_before).total_seconds())
    return diff_seconds


def save_waiting_data_into_csv(table_name, price, date):
    os.makedirs("waiting_data_store", exist_ok=True)
    filepath = os.path.join("waiting_data_store", table_name+".csv")
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([price, date])
    print(f"DATA SAVE into {filepath}")


def send_mail_alert_if_two_rows(table_name):
    filepath = os.path.join("waiting_data_store", table_name + ".csv")
    row_count = len(pd.read_csv(filepath, header=None))
    print(f"CSV Data {table_name} Rows count :", row_count)
    if row_count == 2:
        print("Send email alert")
        email_sender(table_name)


def email_sender(table_name):
    try:
        sender = smtp_user

        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = f"🚒 Data Ingestion Failure {table_name.upper()}🚒"
        body = f"""\
            <html>
              <body>
                <p>😭 Data Ingestion failed 😭<br><br>
                The new data for the <b>{table_name.upper()}</b> Postgres table could not be ingested at 
                {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}.<br><br>
                It has been saved to a CSV file and will be loaded into the table once the Postgres issue is resolved.
                </p>
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
            # when testing with mailhog, no need to connect sender (user password)
            else:
                server.sendmail(receiver, receiver, msg.as_string())
        print("✅ Send Email alert successfully at", receiver)
        return True
    except Exception as e:
        print(f"❌  FAIL TO SEND EMAIL ALERT : {e}")
        return False
