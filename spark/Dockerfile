FROM apache/spark:4.0.0

USER root
# Python3.12 obligatoire pour Spark car Airflow3 est en 3.12 et spark et pyspark(airflow) doivent avoir la meme version python pour communiquer
# Apache ne gere pas nativement Python3.12, donc installation et compilation manuelle

# Installer dépendances pour compilation
RUN apt-get update && apt-get install -y wget build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libffi-dev \
    libbz2-dev liblzma-dev xz-utils

# Télécharger, compiler et installer Python 3.12
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar xvf Python-3.12.0.tgz && cd Python-3.12.0 && \
    ./configure --enable-optimizations && make -j$(nproc) && make altinstall && \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python3

USER spark