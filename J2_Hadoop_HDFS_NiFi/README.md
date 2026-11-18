# TP Jour 2 :Hadoop, HDFS et ingestion des données

README de reproduction. Ce dossier contient les livrables, les preuves et les tests du Jour 2.

## 1. Versions

| Élément | Version |
|---|---|
| Système | Ubuntu 26.04.1 LTS, noyau Linux 7.0.0-43 |
| Hadoop | 3.5.0 (HDFS seul, pseudo-distribué, sans YARN), Java 17 |
| NiFi | 2.12.0, Java 21 |
| Modules NiFi ajoutés | `nifi-hadoop-nar` 2.12.0 et `nifi-hadoop-libraries-nar` 2.12.0 (voir `docs/nifi/installation-module-hadoop-nifi.md`) |
| Python | 3.14.4 |
| Jeu de données | TPCx-BB 1.7.0, 36 fichiers (24 dans `data/`, 12 dans `data_refresh/`) |

Détail complet : `docs/operations/fiche_environnement.md`.

## 2. Démarrage

HDFS (Java 17, NameNode `hdfs://localhost:9000`) :

```bash
start-dfs.sh
jps                       # NameNode, DataNode, SecondaryNameNode
hdfs dfsadmin -report | head -n 12
hdfs dfsadmin -safemode get   # attendu : Safemode is OFF
```

NiFi (Java 21) :

```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh start
/opt/nifi/bin/nifi.sh status   # attendu : Status: UP
```

Interface NiFi : `https://localhost:8443/nifi` (local uniquement, certificat auto-signé). Les identifiants sont ceux générés au premier démarrage et ne sont pas versionnés.

À adapter si ton installation diffère : l'emplacement de `start-dfs.sh` et le `JAVA_HOME` de Hadoop (défini dans `hadoop-env.sh`).

## 3. Chemins

| Usage | Chemin |
|---|---|
| Hadoop, NiFi | `/opt/hadoop`, `/opt/nifi` |
| Configuration Hadoop | `/opt/hadoop/etc/hadoop/core-site.xml`, `hdfs-site.xml` |
| Données HDFS locales | `/home/pauline/hadoop-data/` |
| Dossiers NiFi | `/data/nifi/input`, `/data/nifi/archive`, `/data/nifi/error` |
| Journal NiFi | `/opt/nifi/logs/nifi-app.log` |
| Kit TPCx-BB local | `retail_project/data/`, `retail_project/data_refresh/` |

Arborescence HDFS :

```
/retail-lake/raw/tpcxbb/initial   (store_sales.dat, UC-03)
/retail-lake/raw/tpcxbb/refresh
/retail-lake/raw/nifi             (store_sales.dat, UC-04)
/retail-lake/bronze/tpcxbb
/retail-lake/silver
/retail-lake/gold
/retail-lake/quality
/retail-lake/logs
```

## 4. Reproduire

UC-03 : création de l'arborescence et dépôt manuel.

```bash
hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/initial /retail-lake/raw/tpcxbb/refresh /retail-lake/raw/nifi
hdfs dfs -mkdir -p /retail-lake/bronze/tpcxbb /retail-lake/silver /retail-lake/gold /retail-lake/quality /retail-lake/logs
hdfs dfs -put retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/
hdfs dfs -ls -R /retail-lake
hdfs dfs -cat /retail-lake/raw/tpcxbb/initial/store_sales.dat | sha256sum
```

UC-04 : dépôt par NiFi.

```bash
mkdir -p /data/nifi/input /data/nifi/archive /data/nifi/error
cp retail_project/data/store_sales/store_sales.dat /data/nifi/input/
```

Dans NiFi, construire `GetFile` → `PutHDFS` avec les paramètres du tableau ci-dessous, démarrer `PutHDFS` puis `GetFile`, puis vérifier :

```bash
hdfs dfs -ls -h /retail-lake/raw/nifi
hdfs dfs -cat /retail-lake/raw/nifi/store_sales.dat | sha256sum
```

SHA-256 attendu : `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e`.

## 5. Paramètres NiFi (non sensibles)

| Processeur | Propriété | Valeur |
|---|---|---|
| `GetFile` | Input Directory | `/data/nifi/input` |
| | Keep Source File | `false` |
| | Recurse Subdirectories | `false` |
| `PutHDFS` | Hadoop Configuration Resources | `/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml` |
| | Directory | `/retail-lake/raw/nifi` |
| | Conflict Resolution Strategy | `fail` |
| Relations | `GetFile` → `PutHDFS` | `success` |
| | `PutHDFS` `success` | auto-terminée |
| | `PutHDFS` `failure` | reliée à `PutHDFS` (file d'attente visible) |

## 6. Arrêt

NiFi puis HDFS :

```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh stop
stop-dfs.sh
jps                       # NiFi, NameNode, DataNode et SecondaryNameNode ne doivent plus apparaître
```

Ne jamais relancer `hdfs namenode -format` : il détruit le système de fichiers.

## 7. Contenu du dossier

| Livrable (§12.6) | Fichier |
|---|---|
| 1. Fiche d'environnement technique | `docs/operations/fiche_environnement.md` |
| 2. Fiche de découverte Hadoop et HDFS | `docs/architecture/fiche-hadoop-hdfs.md`, `docs/nifi/fiche-decouverte-nifi.md` |
| 3. Inventaire des fichiers TPCx-BB | `docs/ingestion/inventaire/`, `docs/ingestion/fiche-depot-store_sales.md` |
| 4. Arborescence du Data Lake | `docs/architecture/architecture-data-lake.md` |
| 5. Commandes et résultats HDFS | `tests_hdfs/journal-commandes-hdfs.md`, `historique-commandes-hdfs.md` |
| 6. Preuves du dépôt et des contrôles | `docs/ingestion/rapport-verification-stockage-hdfs.md`, `tests_hdfs/`, `preuves/hdfs/` |
| 7. Schéma du flux NiFi | `docs/nifi/schema-flux-nifi.md` |
| 8. Captures de la configuration NiFi | `preuves/nifi/` (propriétés de `GetFile` et `PutHDFS`, canevas) |
| 9. Preuves d'exécution et de dépôt | `preuves/nifi/` |
| 10. Tableau des erreurs et corrections | `docs/operations/tableau-erreurs-corrections.md`, `docs/nifi/erreur-controlee-nifi.md` |
| 11. Documentation de la provenance | `docs/nifi/documentation-provenance-nifi.md` |
| 12. Script de repli | Sans objet : NiFi et `PutHDFS` ont fonctionné, aucune solution de remplacement n'a été utilisée |
| 13. README de reproduction | Ce fichier |

## 8. Limites

- Un seul fichier (`store_sales.dat`) a été déposé, une fois par `hdfs dfs -put` (UC-03) et une fois par NiFi (UC-04). Les 35 autres fichiers du kit sont inventoriés mais non déposés.
- Les zones `bronze`, `silver`, `gold`, `quality` et `logs` sont créées mais vides (travail du Jour 3).
- L'approfondissement NiFi (étape 12) n'a pas été réalisé.
