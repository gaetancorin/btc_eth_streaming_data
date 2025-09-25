# BTC & ETH Streaming Data

This project streams BTC/USD and ETH/USD data in real-time using a websocket-based ingestion system built with the Yfinance library.

The collected data is stored in **PostgreSQL**, while **Airflow** orchestrates the computation of technical indicators on a **Spark** cluster.

Monitoring is handled with **Python**, **Prometheus**, and **Grafana**, and an **email alert system** ensures notifications for the ingestion pipeline, Airflow workflows, and Grafana dashboards.

The **CI/CD** pipeline with GitHub Actions builds containers and runs unit tests on every commit. Emails are sent to Mailhog in development and to Gmail in production.

### Tech Stack
- **Python**
- **PostgreSQL**
- **Airflow**
- **Spark**
- **Prometheus**
- **Grafana**
- **Mailhog**
- **Github Action**

### Architecture
![Global Architecture](./_documentation/global_architecture.png)

### Data pipelines
There is two data pipeline into this project.

- The first is BTC/USD and ETH/USD data

![Pipeline Data](./_documentation/pipeline_data.png)

- The second is monitoring data

![Pipeline Monitoring](./_documentation/pipeline_monitoring.png)
