# clean-orchestrator.ps1

Write-Output "STOPPING AND REMOVING ALL CONTAINERS AND VOLUMES FOR PROJECT"

# 1. Airflow
docker-compose -p airflow_streaming -f airflow/docker-compose.yaml down -v

# 2. Spark
docker-compose -p spark_streaming -f spark/docker-compose.yaml down -v

# 3. Mailhog
docker-compose -p mailhog_streaming -f mailhog/docker-compose.yaml down -v

# 4. Ingestion
docker rm -f ingestion_streaming 2>$null
docker image rm ingestion_streaming -f 2>$null

# 5. Postgres (remove network too)
docker-compose -p postgres_streaming -f postgres/docker-compose.yaml down -v

Write-Output "DONE CLEANING ALL CONTAINERS AND VOLUMES"