import threading
from datetime import datetime, timezone
from yfinance import WebSocket
from postgres_manager import PostgresManager
import utils as utils
import time

postgres_manager = None
ws_global = None
last_data = {}

def handle_message(msg):
    if 'price' in msg:
        id = msg['id'].lower().replace("-", "_")
        price = msg['price']
        date = datetime.now(timezone.utc)
        print(f"[{date.strftime('%Y-%m-%d %H:%M:%S%z')}] Price {id} : {price}")

        # data is valide if new data have more than 30 secondes compare to old data
        if id not in last_data or utils.compare_utc_date(last_data[id], date) > 30:
            last_data[id] = date
            date = date.replace(second=0, microsecond=0)
            result = postgres_manager.write_on_db(table_name=id, price=price, date=date)
            if not result:
                print("COULD NOT save data in PostgreSQL, so save data in CSV")
                utils.save_waiting_data_into_csv(table_name=id, price=price, date=date)
                utils.send_mail_alert_if_two_rows(table_name=id)
        else:
            print(f"Not Inserted: Duplicate value for {id} in the same minute.")


def run_ws():
    global ws_global
    while True:
        try:
            ws_global = WebSocket(url='wss://streamer.finance.yahoo.com/?version=2', verbose=True)
            ws_global.subscribe(["BTC-USD", "ETH-USD"])
            ws_global.listen(handle_message)
        except Exception as e:
            print(f"⚠️ WebSocket Yfinance fail : {e}")
            print("⏳ Websocket Yfinance try reconnect in 5 secondes...")
            time.sleep(5)

def start_ingestion():
    global postgres_manager
    postgres_manager = PostgresManager()

    # Thread WebSocket
    ws_thread = threading.Thread(target=run_ws)
    ws_thread.start()

    # Boucle d'attente pour bloquer le main thread
    try:
        while ws_thread.is_alive():
            ws_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("end BTC and ETH Thread")

if __name__ == "__main__":
    start_ingestion()
