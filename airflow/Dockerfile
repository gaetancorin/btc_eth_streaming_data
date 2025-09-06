FROM apache/airflow:3.0.3

USER root

# Install Java and define JAVA_HOME for spark
RUN apt update && \
    apt-get install -y openjdk-17-jdk-headless && \
    apt-get install -y ant && \
    apt-get clean;

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow

# Install Spark provider + PySpark
RUN pip install --no-cache-dir apache-airflow-providers-apache-spark==5.3.2 pyspark==4.0.0