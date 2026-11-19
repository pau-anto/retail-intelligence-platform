from pyspark.sql import SparkSession

# Création d'une session Spark en mode local
spark = (
    SparkSession.builder
    .appName("Test-Retail-Intelligence")
    .master("local[*]")
    .getOrCreate()
)

# Afficher la version de Spark
print("Version Spark :", spark.version)

# Créer un petit jeu de données de test
donnees = [
    ("Magasin A", 1200.0),
    ("Magasin B", 850.0),
    ("Magasin C", 1600.0),
]

colonnes = ["magasin", "chiffre_affaires"]

df = spark.createDataFrame(donnees, colonnes)

# Afficher les données
df.show()

# Arrêter proprement la session
spark.stop()