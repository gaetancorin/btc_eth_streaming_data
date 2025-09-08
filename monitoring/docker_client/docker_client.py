from prometheus_client import start_http_server, Gauge
import docker
import time
from datetime import datetime

# Connexion au daemon Docker via TCP sur Windows (Local)
client = docker.DockerClient(base_url="tcp://host.docker.internal:2375")
# Connexion au daemon Docker via TCP sur Windows (Dans container)
# client = docker.DockerClient(base_url="tcp://localhost:2375")

container_state_gauge = Gauge(
    'docker_container_state',
    'State of Docker containers (1=running, 0=not running)',
    ['id', 'name', 'status'])

container_cpu_used_gauge = Gauge(
    'docker_container_cpu_percent',
    'CPU usage percentage per container',
    ['id', 'name']
)
total_cpu_used_gauge = Gauge(
    'docker_total_cpu_used_percent',
    'Total CPU usage percentage for all running containers'
)
total_cpu_available_gauge = Gauge(
    'docker_total_cpu_available_percent',
    'Total available CPU percentage on the Docker host (100% * nb_cores)'
)

container_memory_used_gauge = Gauge(
    'docker_container_memory_used_mb',
    'Memory usage in megabytes per container',
    ['id', 'name']
)
total_memory_used_gauge = Gauge(
    'docker_total_memory_used_mb',
    'Total memory usage in megabytes for all running containers'
)
total_memory_available_gauge = Gauge(
    'docker_total_memory_available_mb',
    'Total memory available in megabytes on the Docker host'
)

def update_metrics():
    containers = client.containers.list(all=True)
    container_state_gauge.clear()

    # Récupérer l'état du container: 1=Running, 0=Exited
    for c in containers:
        state = 1 if c.status == "running" else 0
        container_state_gauge.labels(id=c.short_id, name=c.name, status=c.status).set(state)

    # Récupérer la consommation CPU par conteneur
    total_cpu_used = 0.0
    for c in containers:
        if c.status == "running":
            try:
                stats = c.stats(stream=False)
                # CPU %
                # Données CPU du conteneur au moment présent
                current_cpu = stats["cpu_stats"]["cpu_usage"]["total_usage"]
                # Données CPU du conteneur lors de la mesure précédente (precpu = previous cpu)
                last_cpu = stats["precpu_stats"]["cpu_usage"]["total_usage"]
                # Différence = consommation CPU du conteneur entre les deux mesures
                cpu_delta = current_cpu - last_cpu

                # Données CPU totales du serveur global (tous les processus, tous les conteneurs) au moment présent
                current_system_cpu = stats["cpu_stats"]["system_cpu_usage"]
                # Données CPU totales du serveur global lors de la mesure précédente
                last_system_cpu = stats["precpu_stats"]["system_cpu_usage"]
                # Différence = consommation CPU du serveur global entre les deux mesures
                system_delta = current_system_cpu - last_system_cpu

                container_cpu_percent_used = 0.0
                if system_delta > 0 and cpu_delta > 0:
                    # Nombres de coeurs CPUs dédiés aux serveur (ex:6)
                    cpu_cores = int(stats["cpu_stats"]["online_cpus"])
                    # Calcul du % d'utilisation CPU du conteneur par rapport au serveur global.
                    #Multiplier par le nombres de coeurs CPU pour avoir un ratio 600% pour 6 coeurs par ex
                    container_cpu_percent_used = (cpu_delta / system_delta) * cpu_cores * 100.0
                    # arrondis x.xx %
                    container_cpu_percent_used = round(container_cpu_percent_used, 2)
                    container_cpu_used_gauge.labels(id=c.short_id, name=c.name).set(container_cpu_percent_used)
                    total_cpu_used += container_cpu_percent_used
            except Exception as e:
                container_cpu_used_gauge.labels(id=c.short_id, name=c.name).set(0)
        else:
            container_cpu_used_gauge.remove(c.short_id, c.name)
    total_cpu_used_gauge.set(total_cpu_used)


    # Récupérer la consommation mémoire par conteneur
    total_memory_used = 0.0
    for c in containers:
        if c.status == "running":
            try:
                stats = c.stats(stream=False)
                # Mémoire
                container_memory_used_bytes = stats["memory_stats"]["usage"]
                container_memory_used_mb = container_memory_used_bytes / (1024 * 1024)
                container_memory_used_mb = round(container_memory_used_mb, 2)
                container_memory_used_gauge.labels(id=c.short_id, name=c.name).set(container_memory_used_mb)
                total_memory_used += container_memory_used_mb
            except Exception as e:
                # Si erreur, mettre les metrics à -1
                container_memory_used_gauge.labels(id=c.short_id, name=c.name).set(-1)
        else:
            container_memory_used_gauge.remove(c.short_id, c.name)
    total_memory_used_gauge.set(total_memory_used)

    # Récupérer la capacité de % de cpu et de mémoire dédiés a Docker
    if containers:
        stats = containers[0].stats(stream=False)
        try:
            total_cpu_available = int(stats["cpu_stats"]["online_cpus"]) *100
            total_cpu_available_gauge.set(total_cpu_available)
        except Exception as e:
            total_cpu_available_gauge.set(-1)
        try:
            total_memory_available_bytes = stats["memory_stats"]["limit"]

            total_memory_available_mb = total_memory_available_bytes / (1024 * 1024)
            total_memory_available_mb = round(total_memory_available_mb, 2)
            total_memory_available_gauge.set(total_memory_available_mb)
        except Exception as e:
            total_memory_available_gauge.set(-1)

def start_prometheus_client():
    # Serveur HTTP Prometheus sur le port 8000
    start_http_server(8000)
    print("Serving metrics on http://localhost:8000/metrics")
    try:
        while True:
            update_metrics()
            time.sleep(1)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alive")
    except KeyboardInterrupt:
        print("End prometheus_client")


if __name__ == '__main__':
    start_prometheus_client()
