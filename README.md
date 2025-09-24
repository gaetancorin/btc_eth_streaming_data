# btc_eth_streaming_data 

This project collects BTC/USD and ETH/USD data using an ingestion system built with the **Yfinance** library.

The data is stored in **PostgreSQL**, and technical indicators are computed via **Airflow** connected to a **Spark** cluster.

Monitoring is implemented using **Python**, **Prometheus**, and **Grafana**, and an **email alert system** is set up for the ingestion pipeline, Airflow workflows, and Grafana dashboards.

### Tech stack
- Python
- PostgreSQL
- Airflow
- Spark
- Prometheus
- Grafana

![Global_architecture](.\_documentation\global_architecture.png)


