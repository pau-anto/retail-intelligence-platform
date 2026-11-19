# Retail Intelligence Platform

Projet de la semaine « Architectures Data Lake, Data Warehouse et Lakehouse »
(IPSSI, Mastère Développement, Data & IA, 5e année).

Fil rouge : une enseigne de distribution veut une plateforme analytique
construite sur le jeu synthétique TPCx-BB (version 1.7.0).

Auteure : Pauline Antognelli

## Avancement

| Jour | Thème | Use cases | Dossier | État |
| --- | --- | --- | --- | --- |
| J1 | Besoin métier, exploration, architecture | UC-01, UC-02 | [J1_Retail_Intelligence](J1_Retail_Intelligence/) | terminé |
| J2 | Hadoop, HDFS, NiFi | UC-03, UC-04 | [J2_Hadoop_HDFS_NiFi](J2_Hadoop_HDFS_NiFi/) | terminé (approfondissement NiFi non réalisé) |
| J3 | Transformation, qualité des données et Data Lakehouse | UC-06 | [J3_PySpark_Silver_Gold](J3_PySpark_Silver_Gold/) | partie obligatoire terminée |

## Fil conducteur

1. **J1 : cadrer et choisir.** Le besoin métier est analysé, les sources TPCx-BB sont explorées et une architecture cible est retenue : un Data Lake organisé en zones Bronze, Silver et Gold sur HDFS, en format Parquet, avec une couche Gold de tables prêtes pour les indicateurs.
2. **J2 : stocker et ingérer.** Hadoop et HDFS sont installés en pseudo-distribué, l'arborescence `/retail-lake` est créée, puis `store_sales.dat` est déposé à la main (UC-03) et par un flux NiFi (UC-04), avec contrôle d'intégrité par empreinte SHA-256.
3. **J3 : transformer et contrôler.** Les tables `store_sales` et `item` sont nettoyées (Silver), agrégées (Gold) et contrôlées avec PySpark.

## Jour 1 : cadrage métier et architecture

Dossier : [J1_Retail_Intelligence](J1_Retail_Intelligence/)

| Use case | Livrables |
| --- | --- |
| UC-01 : analyser le besoin métier et explorer les sources | [Cadrage métier](J1_Retail_Intelligence/docs/UC01/UC01_cadrage_metier.pdf), [questions décisionnelles](J1_Retail_Intelligence/docs/UC01/UC01_questions_decisionnelles.pdf), inventaire des sources, dictionnaire des indicateurs, qualification des données, limites et hypothèses (versions modifiables dans [`sources/`](J1_Retail_Intelligence/sources/)) |
| UC-02 : concevoir et justifier une architecture Data | [Comparaison des architectures](J1_Retail_Intelligence/docs/UC02/UC02_comparaison_architectures.pdf), [positionnement des composants](J1_Retail_Intelligence/docs/UC02/UC02_positionnement_composants.pdf), [passage du local à Azure](J1_Retail_Intelligence/docs/UC02/UC02_local_vers_azure.pdf), [gouvernance](J1_Retail_Intelligence/docs/UC02/UC02_gouvernance.pdf), [architecture cible](J1_Retail_Intelligence/docs/UC02/UC02_architecture_cible.pdf) |

Choix retenu : Data Lake Bronze, Silver et Gold sur HDFS au format Parquet, avec une couche Gold de tables prêtes pour les indicateurs. Le Lakehouse est jugé intéressant plus tard, le Data Warehouse seul ne conserve pas le brut.

## Jour 2 : Hadoop, HDFS et NiFi

Dossier : [J2_Hadoop_HDFS_NiFi](J2_Hadoop_HDFS_NiFi/). Le [README du Jour 2](J2_Hadoop_HDFS_NiFi/README.md) explique la reproduction.

| Résultat | Valeur |
| --- | --- |
| Environnement | Hadoop 3.5.0 (HDFS pseudo-distribué), NiFi 2.12.0 |
| Arborescence HDFS | `/retail-lake` avec zones `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` |
| Fichier déposé | `store_sales.dat`, 92 764 700 octets, déposé manuellement puis par NiFi |
| Contrôle d'intégrité | Même empreinte SHA-256 pour les deux dépôts |
| Documentation | Fiches Hadoop, HDFS et NiFi, schéma du flux, provenance, tableau des erreurs et corrections |

## Jour 3 : PySpark, Silver et Gold

Dossier : [J3_PySpark_Silver_Gold](J3_PySpark_Silver_Gold/). Le [README du Jour 3](J3_PySpark_Silver_Gold/README.md) explique les prérequis, l'ordre d'exécution et les sorties.

Traitement en PySpark (mode local) de deux tables, `store_sales` et `item` : nettoyage (Silver), mise à l'écart des lignes invalides (quarantaine), agrégations du chiffre d'affaires (Gold), écriture en Parquet et contrôles qualité. Le traitement du Jour 3 travaille sur le système de fichiers local, pas sur HDFS.

| Résultat | Valeur |
| --- | --- |
| Lignes de ventes traitées | 667 579 (aucune perdue) |
| Produits | 17 820 |
| Jeux Gold | CA par catégorie, par produit, par mois, par année |
| Contrôles qualité | Complétude, unicité, types, cohérence, volumes, intégrité référentielle |

Documents principaux :
- [Inventaire des sources](J3_PySpark_Silver_Gold/docs/data-dictionary/UC06_inventaire_sources.md)
- [Règles de nettoyage](J3_PySpark_Silver_Gold/docs/transformations/UC06_regles_nettoyage.md)
- [Documentation Silver](J3_PySpark_Silver_Gold/docs/data-dictionary/UC06_silver_documentation.md) et [Gold](J3_PySpark_Silver_Gold/docs/data-dictionary/UC06_gold_documentation.md)
- [Rapport qualité](J3_PySpark_Silver_Gold/docs/quality/UC06_rapport_qualite.md)

## Organisation du dépôt

```
retail-intelligence-platform/
├── J1_Retail_Intelligence/    docs, sources, preuves : cadrage métier et architecture
├── J2_Hadoop_HDFS_NiFi/       docs, preuves, tests HDFS
├── J3_PySpark_Silver_Gold/    notebooks, docs, preuves, scripts
└── README.md
```

## Données

Les données du jeu TPCx-BB (zones brute, Silver et Gold) ne sont pas versionnées : elles sont volumineuses et se régénèrent avec les notebooks. Les dossiers `data/` et `outputs/` sont exclus par le `.gitignore`.

## Conventions

- Dossiers de jour : `J<n>_<thème>`.
- Documents d'un use case : préfixe `UC<nn>_`.
- Preuves : `PXX_description.png`, numérotées dans l'ordre de réalisation.
