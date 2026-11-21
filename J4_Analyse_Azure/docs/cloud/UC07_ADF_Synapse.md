# UC-07 – Azure Data Factory, Synapse Analytics, Spark pools et SQL

## 1. Qui fait quoi : répartition des responsabilités

| Composant | Responsabilité | Dans notre projet |
|---|---|---|
| **ADLS Gen2** | **Stocker** les données (zones bronze, silver, gold) et gérer les accès | **Déployé** (compte `stretailj4pa`) |
| **Azure Data Factory** | **Intégrer, déplacer et orchestrer** : copier les données depuis les sources vers le lac, enchaîner et planifier les traitements | Étudié, non déployé |
| **Azure Synapse Analytics** | **Analyser et traiter** : environnement qui regroupe entrepôt SQL, traitement Spark et pipelines | Étudié, non déployé |
| **Spark** (pools Synapse) | **Calculer** de façon distribuée sur les fichiers du lac | Utilisé **en local** (PySpark) ; pool Synapse non déployé |

Règle simple : le stockage ne calcule pas, l'orchestrateur ne stocke pas, le moteur ne planifie pas.

## 2. Azure Data Factory (ADF)

- **Rôle** : service d'intégration de données géré et sans serveur à gérer, qui propose plus de 90 connecteurs prêts à l'emploi pour collecter des données de sources variées.
- **Éléments de base** : *pipelines* (enchaînement d'étapes), *activités* (une étape : copier, transformer, exécuter), *jeux de données* et *services liés* (description des sources et destinations et de la connexion), *déclencheurs* (planification ou événement), *Integration Runtime* (l'environnement qui exécute les déplacements).
- **Dans notre architecture** : copier les fichiers TPCx-BB vers `bronze/tpcxbb/`, enregistrer l'empreinte dans le manifeste, puis lancer les traitements bronze → silver → gold.
- **Sécurité** : l'accès au lac se ferait par une **identité managée** de la fabrique de données, avec des ACL limitées (voir étape 5), sans clé de compte.
- **Pourquoi non déployé** : le sujet n'exige pas de pipeline ; l'ingestion des fichiers du projet a été faite en local (Jour 2).

## 3. Azure Synapse Analytics

- **Rôle** : service d'analyse organisé en **espace de travail**, pour le stockage relationnel en entrepôt, l'ingénierie big data et la préparation des données, sous une même limite de sécurité, de développement et de supervision. Les différents moteurs peuvent travailler sur un même compte ADLS.
- **Composants** :
  - **Pipelines Synapse** : capacités d'intégration issues d'Azure Data Factory.
  - **Pools Spark** et **pools SQL** : voir ci-dessous.
  - **Synapse Studio** : interface web de l'espace de travail.
- **Dans notre architecture** : lire les jeux Silver, produire les jeux Gold avec Spark, et les interroger en SQL.

### 3.1 Synapse Studio
Interface web unique de l'espace de travail. Elle regroupe, par grandes sections : la **navigation dans les données** (comptes de stockage et bases), le **développement** (scripts SQL, notebooks, définitions de jobs Spark), l'**intégration** (pipelines), la **supervision** (exécutions, erreurs) et la **gestion** (pools, droits, connexions). Pour notre projet, elle servirait à explorer `gold/` et à exécuter des requêtes sans installer d'outil local.

### 3.2 Pools Spark
- **Rôle** : moteur de traitement distribué dans Synapse, utilisé via des **notebooks** ou des **définitions de jobs Spark**. Ces objets existent dans Synapse et pas dans Azure Data Factory.
- **Dans notre architecture** : exécuter les transformations bronze → silver → gold que nous avons écrites en PySpark local au Jour 3, avec des chemins `abfss://…` au lieu de `file://…`.
- **Transposition** : le code PySpark change peu ; ce sont les chemins d'accès et l'authentification qui changent.
- **Coût** : un pool Spark est facturé pendant qu'il tourne, d'où la nécessité de l'arrêter ; non déployé ici.

### 3.3 Capacités SQL et exploration des données
| Pool SQL | Principe | Usage possible |
|---|---|---|
| **Serverless** | Interroge directement les fichiers du lac (Parquet, CSV) sans infrastructure à provisionner ; des contrôles permettent de plafonner les dépenses par jour, semaine et mois | Explorer `gold/ca_par_mois` ou `silver/store_sales` avec une requête SQL |
| **Dédié** | Entrepôt de données provisionné, pour de gros volumes et des performances prévisibles | Non pertinent pour 667 579 lignes ; facturé tant qu'il est actif |

Les deux types de pools diffèrent par leurs objets de base de données, leur langage, leur sécurité, leurs outils, l'accès aux données et leurs formats : le choix dépend du besoin.

## 4. Data Factory ou pipelines Synapse ?

Les pipelines Synapse reprennent les capacités d'Azure Data Factory, avec des différences de fonctionnalités entre les deux.

| | Azure Data Factory | Synapse (pipelines) |
|---|---|---|
| Orchestration et copie de données | Oui | Oui |
| Notebooks et jobs Spark, procédures stockées sur pool SQL | Non | Oui |
| Usage typique | Intégration seule, plusieurs projets | Intégration dans un espace d'analyse complet |

Pour ce projet : ADF suffirait pour l'ingestion ; Synapse apporte en plus Spark, SQL et un point d'entrée unique d'analyse.

## 5. Correspondance avec ce qui a été fait

| Fonction | Ce qui a été utilisé | Équivalent Azure étudié |
|---|---|---|
| Stockage des zones | Dossiers locaux (Jour 3) puis **ADLS Gen2 réel** (étape 4) | ADLS Gen2 |
| Ingestion et orchestration | Scripts exécutés à la main | Azure Data Factory (ou pipelines Synapse) |
| Traitement | PySpark local | Pool Spark Synapse |
| Exploration SQL | Spark local et notebook | Pool SQL serverless |
| Analyse et visualisation | Notebook UC-08 (pandas, matplotlib) | Synapse Studio, notebooks |

## 6. Précautions de coût et d'architecture
- Un pool SQL **dédié** et un pool **Spark** actif génèrent des coûts : ce sont les premiers éléments à surveiller ou à éviter sur un abonnement étudiant.
- Le SQL serverless est facturé selon l'usage, et l'on peut plafonner ses dépenses.
- Surveiller le coût avec l'analyse de coûts de l'abonnement, qui s'affiche avec un délai.

## 7. Limites
- Étude documentaire : aucun de ces services n'a été déployé ni testé.
- Les capacités et fonctionnalités exactes évoluent ; elles sont à vérifier dans la documentation Microsoft avant tout déploiement.
- Les coûts ne sont pas chiffrés ici.

## Sources
- Microsoft Learn, *Data integration in Azure Synapse Analytics versus Azure Data Factory*, et le module *Orchestrate data integration with Azure Synapse pipelines*.
- Microsoft Learn, *Azure Synapse Analytics FAQ* (pools SQL serverless et dédiés, contrôle des coûts).
- Direction on Microsoft, *Synapse Analytics roadmap* (septembre 2026) ; Microsoft Fabric Blog, *Two Years in: How Fabric Redefines the Modernization Path for Synapse Users*.