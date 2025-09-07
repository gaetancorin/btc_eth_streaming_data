from prometheus_client import start_http_server, Gauge
import docker
import time

# Connexion au daemon Docker via TCP sur Windows
client = docker.DockerClient(base_url="tcp://localhost:2375")

# Gauge Prometheus pour exposer les conteneurs
container_names = Gauge('docker_container_info', 'Docker container names', ['id', 'name', 'status'])

def update_metrics():
    containers = client.containers.list(all=True)
    container_names.clear()
    container_names.collect()
    for c in containers:
        value = 1 if c.status == "running" else 0
        container_names.labels(id=c.short_id, name=c.name, status=c.status).set(value)

if __name__ == '__main__':
    # Serveur HTTP Prometheus sur le port 8000
    start_http_server(8000)
    print("Serving metrics on http://localhost:8000/metrics")
    while True:
        update_metrics()
        time.sleep(3)
