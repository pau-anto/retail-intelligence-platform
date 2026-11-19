# TP3 - Retail Intelligence Platform

Traitement en PySpark, en mode local, de deux tables du jeu de données TPCx-BB : `store_sales` (ventes en magasin) et `item` (produits). Les données brutes sont nettoyées (Silver), les lignes invalides isolées (quarantaine), puis agrégées en jeux analytiques (Gold), le tout enregistré en Parquet et contrôlé.

## 1. Prérequis et versions observées

| Élément | Version observée |
| --- | --- |
| Système | Linux (`Linux-7.0.0-43-generic-x86_64-with-glibc2.43`) |
| Python | 3.14.4, environnement virtuel `.venv` |
| PySpark / Spark | 4.3.0 |
| Java | OpenJDK 21.0.13 |
| Interface | Jupyter dans VS Code (noyau : interpréteur du `.venv`, paquet `ipykernel`) |
| Mode Spark | `local[*]` |

Détail et preuves : `docs/UC06_fiche_environnement.md` (`P01_environnement.png`).

Installation de l'environnement (à adapter) :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyspark==4.3.0 ipykernel
```

Dans VS Code, choisir l'interpréteur `.venv/bin/python` comme noyau du notebook.

## 2. Emplacement des données

Les dossiers `data/` et `outputs/` ne sont pas versionnés dans le dépôt (volumineux). Pour reproduire les résultats, placer les fichiers sources dans `data/raw/data/` puis lancer les notebooks dans l'ordre de la section 4.

Les chemins sont relatifs au dossier du projet (`TP/J3`).

| Zone | Dossier | Contenu |
| --- | --- | --- |
| Brut (`raw`) | `data/raw/data/store_sales/store_sales.dat`, `data/raw/data/item/item.dat`, `data/raw/data/date_dim/` | Fichiers `.dat` pipe-délimités, sans en-tête, jamais modifiés |
| Silver | `data/silver/store_sales`, `data/silver/item` | Données nettoyées, Parquet |
| Quarantaine | `data/quarantine/store_sales`, `data/quarantine/item` | Lignes invalides (0 ligne dans ce TP) |
| Gold | `data/gold/ca_par_categorie`, `ca_par_produit`, `ca_par_mois`, `ca_par_annee` | Agrégats, Parquet |
| Sorties de test | `outputs/` | Test d'écriture Parquet de 100 lignes (non versionné) |

## 3. Paramètres

Définis en tête de chaque notebook :

| Paramètre | Valeur | Rôle |
| --- | --- | --- |
| `master` | `local[*]` | Spark en local, tous les cœurs |
| `base` | `~/Documents/IPSSI/DataLake Warehouse Lakehouse/TP/J3/data` | Racine des données, à adapter à chaque poste |
| Chemins | `"file://" + os.path.expanduser(...)` | Force la lecture sur le système de fichiers local |
| Séparateur | `\|`, sans en-tête, `inferSchema` activé | Lecture des fichiers `.dat` |
| Écriture | `mode("overwrite")`, Parquet | Uniquement sur des dossiers de sortie dédiés |

Les chemins sont préfixés par `file://` car la variable d'environnement `HADOOP_CONF_DIR` fait résoudre les chemins sans schéma vers HDFS, ce qui provoquait une erreur. Détail : documentation de l'erreur de lecture HDFS vs local (`TP3_documentation.md`).

## 4. Ordre d'exécution

| Étape | Notebook | Entrées | Sorties |
| --- | --- | --- | --- |
| 1. Environnement | `scripts/test_spark.py` et notebook de vérification de l'environnement | – | Preuves : versions, session Spark, chemin des données (`P01`) |
| 2. Exploration | `notebooks/UC06_script_exploration.ipynb` | `data/raw/data/` | Schémas, comptages, anomalies : `docs/data-dictionary/UC06_inventaire_sources.md`, `UC06_questions_technique_exploration.md` |
| 3. Nettoyage | `notebooks/UC06_script_traitement.ipynb` | `data/raw/data/` | `data/silver/`, `data/quarantine/` |
| 4. Transformation | `notebooks/UC06_script_transformation.ipynb` | `data/silver/` | `data/gold/` |
| 5. Contrôles qualité | `notebooks/UC06_controles_qualite.ipynb` | `data/silver/`, `quarantine/`, `gold/` | Résultats affichés, preuves `P06` à `P11` |

Chaque notebook se lance de haut en bas (« Run All »). Les étapes 3, 4 et 5 doivent être exécutées dans cet ordre : chacune lit les sorties de la précédente.

## 5. Sorties produites

| Jeu | Lignes | Format | Description |
| --- | --- | --- | --- |
| `silver/store_sales` | 667 579 | Parquet | Ventes nettoyées, avec `date_vente`, `vente_a_perte`, `prix_nul`, `ligne_id` |
| `silver/item` | 17 820 | Parquet | Produits nettoyés, avec `cout_superieur_prix` |
| `quarantine/store_sales`, `quarantine/item` | 0 | Parquet | Lignes invalides |
| `gold/ca_par_categorie` | 9 | Parquet | CA, quantité et nombre de lignes par catégorie |
| `gold/ca_par_produit` | 17 820 | Parquet | CA et quantité par produit |
| `gold/ca_par_mois` | 60 | Parquet | CA et quantité par année et mois |
| `gold/ca_par_annee` | 5 | Parquet | CA par année |

## 6. Contrôles disponibles

`notebooks/UC06_controles_qualite.ipynb` vérifie, sur les fichiers relus : présence et taille, schéma et nombre de lignes, complétude, unicité, cohérence des valeurs, intégrité référentielle ventes/produits, volumes (Silver + quarantaine = entrée) et cohérence Gold/Silver. Résultats et anomalies : `docs/quality/UC06_rapport_qualite.md`.

## 7. Documentation

| Document | Dossier |
| --- | --- |
| `UC06_fiche_environnement.md` | `docs/` |
| `UC06_inventaire_sources.md`, `UC06_questions_technique_exploration.md`, `UC06_silver_documentation.md`, `UC06_gold_documentation.md` | `docs/data-dictionary/` |
| `UC06_regles_nettoyage.md`, `UC06_transformations.md`, `UC06_comparaison_formats.md` | `docs/transformations/` |
| `UC06_rapport_qualite.md` | `docs/quality/` |
| Captures `PXX_*.png` | `preuves/` |

Le sens des colonnes provient de la spécification TPCx-BB v1.7.0 (annexe B), fournie par le formateur.

## 8. Limites connues

- Les colonnes dont le sens n'était pas utilisé dans les analyses gardent un nom `_cN` dans Silver (17 pour `store_sales`, 16 pour `item`). Leur nom TPCx-BB est dans `silver_documentation.md`.
- La correspondance `_cN` / nom TPCx-BB repose sur l'ordre des colonnes, confirmé par deux calculs (`montant = quantité × prix de vente`, `profit = net payé − coût de gros × quantité`).
- `silver/store_sales` est écrit en 200 petits fichiers (comportement par défaut de Spark en local).
- Seules les ventes en magasin sont traitées (pas de ventes web, de retours ni de stocks).
- Le montant des ventes est calculé avant coupons. Le profit est négatif sur 74,3 % des lignes (à discuter avec le formateur) : aucune marge n'est agrégée.
- L'année 2005 est incomplète (ventes jusqu'au 13 décembre).
- 14 lignes quasi identiques sur ticket, produit et promotion sont conservées, non inspectées.
- Les fichiers Parquet n'offrent pas les garanties transactionnelles d'un format de table Lakehouse.
