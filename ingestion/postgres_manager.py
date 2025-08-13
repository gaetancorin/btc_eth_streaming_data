import psycopg2
import os
from dotenv import load_dotenv
import traceback
import sys

load_dotenv()

class PostgresManager:

    def __init__(self):
        self.connect_params = {
            "host": os.getenv("HOST"),
            "port": int(os.getenv("PORT")),
            "dbname": os.getenv("DBNAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
        }
        self.connect = None
        self._ensure_connexion()

    def _ensure_connexion(self):
        if self.connect is None or self.connect.closed != 0:
            self.connect = psycopg2.connect(**self.connect_params)
            print("Connect to PostGreSQL")

    def write_on_db(self, table_name, price, date):
        try:
            self._ensure_connexion()
            cursor = self.connect.cursor()
            insert_query = f"""
                INSERT INTO {table_name} (price, recorded_utc_at)
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (price, date))
            self.connect.commit()

            print(f"Data insert successfully on {table_name}")
            cursor.close()
            return True
        except Exception:
            print("ERROR on postgres_manager/write_on_db", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None

# for testing
# postgres = PostgresManager()
# postgres.write_on_db("btc_usd", 29350.4521, datetime.now(timezone.utc))