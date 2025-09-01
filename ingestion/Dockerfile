FROM python:3.11

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "btc_eth_ws_listener.py"]


