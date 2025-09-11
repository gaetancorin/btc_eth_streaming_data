# clean-orchestrator.ps1

Write-Output "STOPPING AND REMOVING ALL CONTAINERS AND VOLUMES FOR PROJECT"

# Ingestion
docker rm -f ingestion_streaming 2>$null
docker image rm ingestion_streaming -f 2>$null

# Airflow
docker-compose -p airflow_streaming -f airflow/docker-compose.yaml down -v

# Mailhog
docker-compose -p mailhog_streaming -f mailhog/docker-compose.yaml down -v

# Spark
docker-compose -p spark_streaming -f spark/docker-compose.yaml down -v

# Postgres (remove network too)
docker-compose -p postgres_streaming -f postgres/docker-compose.yaml down -v

# Monitoring (Python ->Prometheus->Grafana)
docker-compose -p monitoring_streaming -f monitoring/docker-compose.yaml down -v

Write-Output "DONE CLEANING ALL CONTAINERS AND VOLUMES"