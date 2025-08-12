import psycopg2
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresManager:

    def __init__(self):
        connect_params = {
            "host": os.getenv("HOST"),
            "port": int(os.getenv("PORT")),
            "dbname": os.getenv("DBNAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
        }
        self.connect = psycopg2.connect(**connect_params)

    def write_on_db(self, table_name, price, date):
        cursor = self.connect.cursor()

        insert_query = f"""
            INSERT INTO {table_name} (price, recorded_utc_at)
            VALUES (%s, %s)
        """
        cursor.execute(insert_query, (price, date))
        self.connect.commit()

        print(f"Data insert successfully on {table_name}")

        cursor.close()

# for testing
# postgres = PostgresManager()
# postgres.write_on_db("btc_usd", 29350.4521, datetime.now(timezone.utc))