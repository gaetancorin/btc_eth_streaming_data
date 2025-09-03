# orchestrator.ps1

Write-Output "GO CREATE ALL CONTAINERS FOR PROJECT !"

# 1. Postgres -> create postgres_streaming_default network
cd postgres
docker-compose -p postgres_streaming up -d --build
cd ..

# 2. Spark
cd spark
docker-compose -p spark_streaming up -d --build
cd ..

# 3. Mailhog
cd mailhog
docker-compose -p mailhog_streaming up -d --build
cd ..

# 4. Airflow
cd airflow
docker-compose -p airflow_streaming up -d --build
cd ..

# 5. Ingestion
Write-Output "CREATE INGESTION CONTAINER"
cd ingestion
docker build -t ingestion_streaming .
docker run -d --name ingestion_streaming ingestion_streaming
cd ..

Write-Output "ALL CONTAINERS CREATED SUCESSFULLY"