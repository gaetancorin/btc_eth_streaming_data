import threading
from datetime import datetime, timezone
from yfinance import WebSocket
from postgres_manager import PostgresManager
import utils as utils

postgres_manager = PostgresManager()
ws_global = None
last_data = {}

def handle_message(msg):
    if 'price' in msg:
        id = msg['id'].lower().replace("-", "_")
        price = msg['price']
        date = datetime.now(timezone.utc)
        print(f"[{date.strftime('%Y-%m-%d %H:%M:%S%z')}] Price {id} : {price}")

        if id not in last_data or utils.compare_utc_date(last_data[id], date) > 30:
            last_data[id] = date
            result = postgres_manager.write_on_db(table_name=id, price=price, date=date)
            if not result:
                print("fail to save data in PostgreSQL, so save data in CSV")
        else:
            print(f"NOT INSERTED: Duplicate value for {id} in the same minute.")

def run_ws():
    global ws_global
    ws_global = WebSocket(url='wss://streamer.finance.yahoo.com/?version=2', verbose=True)
    ws_global.subscribe(["BTC-USD", "ETH-USD"])
    ws_global.listen(handle_message)

# Thread WebSocket
ws_thread = threading.Thread(target=run_ws)
ws_thread.start()

# Boucle d'attente pour bloquer le main thread
try:
    while ws_thread.is_alive():
        ws_thread.join(timeout=1)
except KeyboardInterrupt:
    print("end BTC and ETH Thread")
