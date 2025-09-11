# orchestrator.ps1

Write-Output "GO CREATE ALL CONTAINERS FOR PROJECT !"

# Postgres -> create postgres_streaming_default network
cd postgres
docker-compose -p postgres_streaming up -d --build
cd ..

# Monitoring (Python ->Prometheus->Grafana)
cd monitoring
docker-compose -p monitoring_streaming up -d --build
cd ..

# Spark
cd spark
docker-compose -p spark_streaming up -d --build
cd ..

# Mailhog
cd mailhog
docker-compose -p mailhog_streaming up -d --build
cd ..

# Airflow
cd airflow
docker-compose -p airflow_streaming up -d --build
cd ..

# Ingestion
Write-Output "CREATE INGESTION CONTAINER"
cd ingestion
docker build -t ingestion_streaming .
docker run -d --name ingestion_streaming --network postgres_streaming_default ingestion_streaming
cd ..

Write-Output "ALL CONTAINERS CREATED SUCESSFULLY"