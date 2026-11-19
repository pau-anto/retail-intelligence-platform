# Fiche d'environnement – TP3 Retail Intelligence Platform

Date des relevés : 2026-11-18

## 1. Versions observées

| Élément | Valeur observée | Commande / source |
| --- | --- | --- |
| Système | Linux 7.0.0-43-generic, x86_64, glibc 2.43 | `platform.platform()` |
| Python | 3.14.4 | `sys.version` |
| Environnement virtuel | `/home/pauline/project_retail-intelligence/.venv` | `sys.executable`, `VIRTUAL_ENV` |
| PySpark | 4.3.0 | `pyspark.__version__` |
| Java | OpenJDK 21.0.13 (Ubuntu build 21.0.13.0.3+1) | `java -version` |

## 2. Mode d'exécution

| Élément | Valeur |
| --- | --- |
| Mode Spark | Local, `local[*]` (tous les cœurs de la machine) |
| Nom de l'application | `TP3-Retail-Intelligence` |
| Interface de travail | Jupyter dans VS Code |
| Notebook | `Notebook_TP3.ipynb` |
| Cluster / HDFS | Non utilisé |

Note : `HADOOP_CONF_DIR` pointe vers `/opt/hadoop/etc/hadoop`. Pour éviter que Spark cherche les fichiers dans HDFS, les chemins sont préfixés par `file://` (voir la documentation de l'erreur HDFS vs local).

## 3. Chemins utilisés

| Rôle | Chemin |
| --- | --- |
| Projet | `~/Documents/IPSSI/DataLake Warehouse Lakehouse/TP/J3/` |
| Données sources (lecture seule) | À COMPLÉTER, par exemple `.../J3/data/raw/` |
| Résultats de test (écriture) | À COMPLÉTER, par exemple `.../J3/outputs/` |
| Notebook | `.../J3/notebooks/Notebook_TP3.ipynb` |
| Preuves | `.../J3/preuves/` |

Les résultats de test sont écrits dans un répertoire distinct des données sources, pour ne pas modifier les fichiers originaux.

## 4. Vérifications attendues

| Vérification | Résultat | Preuve |
| --- | --- | --- |
| Lancer un notebook | OK | `preuves/01_preuve_environnement_spark.png` |
| Initialiser une session Spark | OK, Spark 4.3.0, `local[*]` | `preuves/01_preuve_environnement_spark.png` |
| Lire un fichier de test | À COMPLÉTER | À COMPLÉTER |
| Afficher un schéma | À COMPLÉTER | À COMPLÉTER |
| Écrire un résultat de test dans un répertoire autorisé | À COMPLÉTER | À COMPLÉTER |

## 5. Preuve d'exécution

![Preuve d'environnement](../preuves/01_preuve_environnement_spark.png)
