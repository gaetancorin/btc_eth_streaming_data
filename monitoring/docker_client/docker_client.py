from prometheus_client import start_http_server, Gauge
import docker
import time
from datetime import datetime

# Connexion au daemon Docker via TCP sur Windows (Local)
client = docker.DockerClient(base_url="tcp://host.docker.internal:2375")
# Connexion au daemon Docker via TCP sur Windows (Dans container)
# client = docker.DockerClient(base_url="tcp://localhost:2375")

# Gauge Prometheus pour exposer les conteneurs
container_names = Gauge('docker_container_info', 'Docker container names', ['id', 'name', 'status'])

cpu_gauge = Gauge(
    'docker_container_cpu_percent',
    'CPU usage percentage per container',
    ['id', 'name']
)
total_cpu_gauge = Gauge('docker_total_cpu_percent', 'Total CPU usage percentage for all running containers')

memory_gauge = Gauge(
    'docker_container_memory_bytes',
    'Memory usage in bytes per container',
    ['id', 'name']
)
total_memory_used_gauge = Gauge('docker_total_used_memory_bytes', 'Total memory usage in bytes for all running containers')
total_memory_available_gauge = Gauge(
    'docker_total_memory_available_bytes',
    'Total memory available on the Docker host'
)

def update_metrics():
    containers = client.containers.list(all=True)
    container_names.clear()

    # Récupérer l'état du container: 1=Running, 0=Exited
    for c in containers:
        value = 1 if c.status == "running" else 0
        container_names.labels(id=c.short_id, name=c.name, status=c.status).set(value)

    # Récupérer la consommation CPU par conteneur
    total_cpu = 0.0
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

                cpu_percent = 0.0
                if system_delta > 0 and cpu_delta > 0:
                    # Nombres de coeurs CPUs dédiés aux serveur (ex:6)
                    cpu_cores = len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                    # Calcul du % d'utilisation CPU du conteneur par rapport au serveur global.
                    #Multiplier par le nombres de coeurs CPU pour avoir un ratio 600% pour 6 coeurs par ex
                    cpu_percent = (cpu_delta / system_delta) * cpu_cores * 100.0

                    cpu_gauge.labels(id=c.short_id, name=c.name).set(cpu_percent)
                    total_cpu += cpu_percent
            except Exception as e:
                cpu_gauge.labels(id=c.short_id, name=c.name).set(0)
        else:
            cpu_gauge.remove(c.short_id, c.name)
    total_cpu_gauge.set(total_cpu)


    # Récupérer la consommation mémoire par conteneur
    total_memory = 0.0
    for c in containers:
        if c.status == "running":
            try:
                stats = c.stats(stream=False)
                # Mémoire
                memory = stats["memory_stats"]["usage"]
                memory_gauge.labels(id=c.short_id, name=c.name).set(memory)
                total_memory += memory
            except Exception as e:
                # Si erreur, mettre les metrics à -1
                memory_gauge.labels(id=c.short_id, name=c.name).set(-1)
        else:
            memory_gauge.remove(c.short_id, c.name)
    total_memory_used_gauge.set(total_memory)

    if containers:
        try:
            stats = containers[0].stats(stream=False)
            total_memory_available = stats["memory_stats"]["limit"]
            total_memory_available_gauge.set(total_memory_available)
        except Exception as e:
            total_memory_available_gauge.set(-1)

def start_prometheus_client():
    # Serveur HTTP Prometheus sur le port 8000
    start_http_server(8000)
    print("Serving metrics on http://localhost:8000/metrics")
    try:
        while True:
            update_metrics()
            time.sleep(10)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alive")
    except KeyboardInterrupt:
        print("End prometheus_client")


if __name__ == '__main__':
    start_prometheus_client()
