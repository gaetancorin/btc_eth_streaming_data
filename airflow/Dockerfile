FROM apache/airflow:3.0.3

USER root

# Install Java for spark
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         openjdk-17-jdk-headless \
#         ca-certificates \
#         apt-transport-https \
#         curl \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Install OpenJDK-17
RUN apt update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Définir JAVA_HOME pour Spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
RUN export JAVA_HOME
# ENV PATH="$JAVA_HOME/bin:$PATH"

# Vérify Java
RUN java -version

USER airflow

# Install Spark provider + PySpark
RUN pip install --no-cache-dir apache-airflow-providers-apache-spark pyspark