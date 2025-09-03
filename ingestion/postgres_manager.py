import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import traceback
import sys
import pandas as pd

load_dotenv()

class PostgresManager:

    def __init__(self):
        self.connect_params = {
            "host": os.getenv("PG_HOST"),
            "port": int(os.getenv("PG_PORT")),
            "dbname": os.getenv("PG_DBNAME"),
            "user": os.getenv("PG_USER"),
            "password": os.getenv("PG_PASSWORD"),
        }
        self.connect = None
        try:
            self._ensure_connection()
        except Exception:
            print("ERROR on postgres_manager/__init__")
            traceback.print_exc(file=sys.stderr)

    def _ensure_connection(self):
        if self.connect is None or self.connect.closed != 0:
            self.connect = psycopg2.connect(**self.connect_params)
            print("Connect to PostGreSQL")
            # if connection was recover
            if self.connect.closed == 0:
                # and waiting csv data
                if os.path.exists("waiting_data_store") and os.listdir("waiting_data_store"):
                    print("LOAD WAITING CSV DATA INTO POSTGRES")
                    self.write_waiting_datas_on_db()

    def write_on_db(self, table_name, price, date):
        try:
            date = date.replace(second=0, microsecond=0)
            self._ensure_connection()
            cursor = self.connect.cursor()
            insert_query = f"""
                INSERT INTO {table_name} (price, datetime_utc)
                VALUES (%s, %s)
                ON CONFLICT (datetime_utc) DO NOTHING
            """
            cursor.execute(insert_query, (price, date))
            self.connect.commit()

            print(f"Data insert successfully on {table_name}")
            cursor.close()
            return True
        except Exception:
            print("ERROR on postgres_manager/write_on_db")
            traceback.print_exc(file=sys.stderr)
            return None

    def write_waiting_datas_on_db(self):
        if not os.path.exists("waiting_data_store"):
            return None
        files_names = os.listdir("waiting_data_store")
        for file_name in files_names:
            file_path = os.path.join("waiting_data_store", file_name)
            file_name = file_name.split('.')[0]
            try:
                df = pd.read_csv(file_path, header=None, names=["price", "date"])
                tuples = [tuple(x) for x in df.to_numpy()]
                cursor = self.connect.cursor()
                query = f"""
                    INSERT INTO {file_name} (price, datetime_utc)
                    VALUES %s
                    ON CONFLICT (datetime_utc) DO NOTHING
                """
                execute_values(cursor, query, tuples)
                self.connect.commit()
                cursor.close()
                print(f"{file_name.upper()} WAITING DATA LOADING SUCESSFULLY INTO POSTGRES")
                os.remove(file_path)
                if not os.listdir("waiting_data_store"):
                    os.rmdir("waiting_data_store")
                print(f"File {file_path} deleted successfully")
            except Exception as e:
                print(f"ERROR while loading waiting data {file_name.upper()} into Postgres: {e}")
                traceback.print_exc(file=sys.stderr)
