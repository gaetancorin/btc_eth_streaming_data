import threading
from datetime import datetime
from yfinance import WebSocket

ws_global_eth = None

def handle_message(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'price' in msg:
        print(f"[{now}] Prix ETH : {msg['price']}")

def run_ws():
    global ws_global_eth
    ws_global_eth = WebSocket(url='wss://streamer.finance.yahoo.com/?version=2', verbose=True)
    ws_global_eth.subscribe(["ETH-USD"])
    ws_global_eth.listen(handle_message)

# Thread WebSocket
ws_thread = threading.Thread(target=run_ws)
ws_thread.start()

# Boucle d'attente pour bloquer le main thread
try:
    while ws_thread.is_alive():
        ws_thread.join(timeout=1)
except KeyboardInterrupt:
    print("end")
