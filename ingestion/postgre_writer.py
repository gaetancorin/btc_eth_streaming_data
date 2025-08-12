import psycopg2
from datetime import datetime, timezone

connect_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "crypto_db",
    "user": "admin",
    "password": "password"
}
connect = psycopg2.connect(**connect_params)
cursor = connect.cursor()

# Example of data to insert
prix_btc = 29350.4521
date_enregistrement = datetime.now(timezone.utc)


insert_query = """
    INSERT INTO btc_usd (price, recorded_utc_at)
    VALUES (%s, %s)
"""
cursor.execute(insert_query, (prix_btc, date_enregistrement))
connect.commit()

print("Data insert successfully on btc_usd.")

if connect:
    cursor.close()
    connect.close()