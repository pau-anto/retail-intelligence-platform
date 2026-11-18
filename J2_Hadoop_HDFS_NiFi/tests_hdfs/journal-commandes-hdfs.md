# Journal des commandes HDFS (étape 2) - 2026-11-17 15:26:38

Utilisateur : pauline - Machine : pauline-XMG-APEX-L23

Livrable 5 : commandes exécutées, résultats et erreurs. Les commandes ci-dessous ont été rejouées le 17/11/2026 à 15:26 ; elles sont en lecture seule, sauf `mkdir -p` sur un dossier déjà existant, sans effet. Les commandes réellement tapées pendant la séance sont dans `historique-commandes-hdfs.md`.

### 1. État du système HDFS

```
$ hdfs dfsadmin -report
Configured Capacity: 105089261568 (97.87 GB)
Present Capacity: 70875914240 (66.01 GB)
DFS Remaining: 70782386176 (65.92 GB)
DFS Used: 93528064 (89.20 MB)
DFS Used%: 0.13%
Replicated Blocks:
        Under replicated blocks: 0
        Blocks with corrupt replicas: 0
        Missing blocks: 0
        Missing blocks (with replication factor 1): 0
        Badly Distributed Blocks: 0
        Low redundancy blocks with highest priority to recover: 0
        Pending deletion blocks: 0
Erasure Coded Block Groups: 
        Low redundancy block groups: 0
        Block groups with corrupt internal blocks: 0
        Missing block groups: 0
        Badly Distributed Blocks: 0
        Low redundancy blocks with highest priority to recover: 0
        Pending deletion blocks: 0

-------------------------------------------------
Live datanodes (1):

Name: 127.0.0.1:9866 (localhost)
Hostname: pauline-XMG-APEX-L23
Decommission Status : Normal
Configured Capacity: 105089261568 (97.87 GB)
DFS Used: 93528064 (89.20 MB)
Non DFS Used: 28827860992 (26.85 GB)
DFS Remaining: 70782386176 (65.92 GB)
DFS Used%: 0.09%
DFS Remaining%: 67.35%
Configured Cache Capacity: 0 (0 B)
Cache Used: 0 (0 B)
Cache Remaining: 0 (0 B)
Cache Used%: 100.00%
Cache Remaining%: 0.00%
Xceivers: 0
Last contact: Tue Nov 17 15:26:37 CET 2026
Last Block Report: Tue Nov 17 12:14:58 CET 2026
Num of Blocks: 1
```

**Lecture.** Un seul DataNode est vivant (`Live datanodes (1)`), en statut « Normal ». Aucun bloc n'est sous-répliqué, corrompu ou manquant. HDFS stocke 89,20 MB (0,13 % de la capacité) répartis en 1 bloc. Le dernier rapport de blocs date de 12:14:58, au démarrage. Le disque est partagé avec le système : « Non DFS Used » (26,85 GB) est de l'espace occupé hors HDFS, ce qui explique que « DFS Remaining » baisse (66,32 GB à 15:14, 65,92 GB à 15:26) alors que « DFS Used » reste à 89,20 MB.

### 1 bis. Mode sans échec (Safemode)

```
$ hdfs dfsadmin -safemode get
Safe mode is OFF
```

**Lecture.** Le Safemode est désactivé : HDFS accepte les écritures.

### 2. Informations sur les nœuds

```
$ hdfs dfsadmin -printTopology
Rack: /default-rack
   127.0.0.1:9866 (localhost) In Service
```

**Lecture.** La topologie ne contient qu'un rack par défaut et un nœud, `127.0.0.1:9866`, en service : c'est un déploiement mono-nœud.

### 3. Lister les répertoires

```
$ hdfs dfs -ls /
Found 1 items
drwxr-xr-x   - pauline supergroup          0 2026-11-17 13:05 /retail-lake
```

**Lecture.** La racine de HDFS ne contient que `/retail-lake`, propriété de `pauline:supergroup`, dernière modification à 13:05.

### 4. Créer le répertoire de travail (déjà existant, commande sans effet)

```
$ hdfs dfs -mkdir -p /retail-lake
(aucune sortie)
```

**Lecture.** Aucune sortie : la commande a réussi sans rien changer, car `/retail-lake` existait déjà (créé à 12:27 d'après les listings). L'option `-p` évite l'erreur sur un dossier existant.

### 5. Vérifier les permissions

```
$ hdfs dfs -ls /retail-lake
Found 6 items
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/bronze
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/gold
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:28 /retail-lake/logs
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:28 /retail-lake/quality
drwxr-xr-x   - pauline supergroup          0 2026-11-17 13:05 /retail-lake/raw
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/silver
```

**Lecture.** Les six zones du Data Lake existent. Chacune appartient à `pauline:supergroup` avec les droits `drwxr-xr-x` : le propriétaire peut lire, écrire et traverser, le groupe et les autres peuvent seulement lire et traverser.

### 6. Taille des données stockées

```
$ hdfs dfs -du -h /retail-lake
0       0       /retail-lake/bronze
0       0       /retail-lake/gold
0       0       /retail-lake/logs
0       0       /retail-lake/quality
88.5 M  88.5 M  /retail-lake/raw
0       0       /retail-lake/silver
```

**Lecture.** Seule la zone `raw` contient des données : 88,5 M, ce qui correspond à `store_sales.dat` (92 764 700 octets). La seconde colonne (espace occupé avec la réplication) est identique à la première, car le facteur de réplication est 1.

### 6 bis. Taille totale

```
$ hdfs dfs -du -s -h /retail-lake
88.5 M  88.5 M  /retail-lake
```

**Lecture.** Le total de `/retail-lake` est de 88,5 M, soit la taille de la seule zone `raw`.

## Erreurs

Aucune erreur sur les commandes de cette étape. Les erreurs rencontrées ailleurs dans la séance (nom d'exemple `ventes.csv`, chemins erronés dans le dépôt, dossier `raww`) sont dans le tableau des erreurs et dans `historique-commandes-hdfs.md`.
