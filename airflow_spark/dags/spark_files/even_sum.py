from pyspark.sql import SparkSession
from pyspark.sql.functions import col

if __name__ == "__main__":
    spark = SparkSession.builder.appName("EvenSumTest").getOrCreate()

    # Créer un DataFrame avec les nombres de 1 à 1_000_000
    data = [(i,) for i in range(1, 1000001)]
    df = spark.createDataFrame(data, ["number"])

    # Filtrer les nombres pairs(0,2,4,6,...) et calculer la somme(0+2+4+6+...)
    even_sum = df.filter(col("number") % 2 == 0).groupBy().sum("number")
    even_sum.show()  # Affiche le résultat dans les logs Spark

    spark.stop()