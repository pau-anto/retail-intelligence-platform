# Fiche d'environnement technique - Jour 2

Date de relevé : 2026-11-17 14:03:33 CET
Utilisateur : pauline - Machine : pauline-XMG-APEX-L23

## Résumé 
Élément
Valeur relevée le 17/11/2026 à 14:03
Système
Ubuntu 26.04.1 LTS, noyau Linux 7.0.0-43
Matériel
Ryzen 7 7840HS, 16 cœurs, 30 Gi de RAM, 98 G de disque (29 % utilisé)
Java
21.0.13 par défaut et pour NiFi ; 17.0.21 pour Hadoop
Hadoop / NiFi / Python
3.5.0 / 2.12.0 / 3.14.4
Chemins
/opt/hadoop, /opt/nifi, données HDFS dans /home/pauline/hadoop-data/, dossiers NiFi dans /data/nifi/{input,archive,error}
Services actifs
NameNode, DataNode, SecondaryNameNode, NiFi, SSH
Ports
9000 (RPC, local), 9866 / 9867 / 9868 / 9870 (HDFS), 8443 (NiFi, local, certificat auto-signé)

## 1. Système d'exploitation
```
Distributor ID:	Ubuntu
Description:	Ubuntu 26.04.1 LTS
Release:	26.04
Codename:	resolute
Linux 7.0.0-43-generic x86_64
```

## 2. Ressources matérielles
```
CPU : AMD Ryzen 7 7840HS w/ Radeon 780M Graphics
Coeurs : 16
               total        used        free      shared  buff/cache   available
Mem:            30Gi        10Gi       5.6Gi       302Mi        15Gi        20Gi
Swap:          8.0Gi          0B       8.0Gi
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p5   98G   27G   67G  29% /
```

## 3. Versions des composants
```
--- Java par défaut
openjdk version "21.0.13.0.3" 2026-10-24
OpenJDK Runtime Environment (build 21.0.13.0.3+1-1-26.04.1-Ubuntu)
OpenJDK 64-Bit Server VM (build 21.0.13.0.3+1-1-26.04.1-Ubuntu, mixed mode, sharing)
--- Java 17 (Hadoop)
openjdk version "17.0.21.0.3" 2026-10-24
OpenJDK Runtime Environment (build 17.0.21.0.3+1-1-26.04.1-Ubuntu)
OpenJDK 64-Bit Server VM (build 17.0.21.0.3+1-1-26.04.1-Ubuntu, mixed mode, sharing)
--- Java 21 (NiFi)
openjdk version "21.0.13.0.3" 2026-10-24
OpenJDK Runtime Environment (build 21.0.13.0.3+1-1-26.04.1-Ubuntu)
OpenJDK 64-Bit Server VM (build 21.0.13.0.3+1-1-26.04.1-Ubuntu, mixed mode, sharing)
--- Hadoop
Hadoop 3.5.0
Source code repository https://github.com/apache/hadoop.git -r dbcc7cd797100e6b32cd84f85b53a5193a5f9af0
Compiled by cnauroth on 2026-03-24T16:56Z
--- NiFi
nifi-api-2.12.0.jar
--- Python
Python 3.14.4
```

## 4. Chemins des installations
```
HADOOP_HOME      = /opt/hadoop
NiFi             = /opt/nifi
Données NameNode = /home/pauline/hadoop-data/namenode
Données DataNode = /home/pauline/hadoop-data/datanode
Journaux NiFi    = /opt/nifi/logs/nifi-app.log
Kit TPCx-BB      = /home/pauline/Documents/IPSSI/DataLake Warehouse Lakehouse/retail_project
Dossier preuves  = /home/pauline/Documents/IPSSI/DataLake Warehouse Lakehouse/TP/J2/preuves
Dossiers NiFi    = /data/nifi/{input,archive,error}
```

## 5. Configuration Hadoop
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/pauline/hadoop-data/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/pauline/hadoop-data/datanode</value>
  </property>
</configuration>
```

## 6. Services actifs
```
--- jps
288224 Jps
278832 BootstrapProcess
273010 DataNode
278874 NiFi
273258 SecondaryNameNode
272826 NameNode
--- NiFi
2026-11-17 14:03:34,484 INFO [main] org.apache.nifi.bootstrap.Command Application Process [278874] Command Status [SUCCESS] HTTP 200
2026-11-17 14:03:34,486 INFO [main] org.apache.nifi.bootstrap.Command Status: UP

--- SSH
active
```

## 7. État de HDFS
```
Configured Capacity: 105089261568 (97.87 GB)
Present Capacity: 71671148544 (66.75 GB)
DFS Remaining: 71577620480 (66.66 GB)
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
```

## 8. Réseau (ports en écoute)
```
LISTEN 0      256               0.0.0.0:9866       0.0.0.0:*    users:(("java",pid=273010,fd=337)) 
LISTEN 0      256               0.0.0.0:9867       0.0.0.0:*    users:(("java",pid=273010,fd=475)) 
LISTEN 0      500               0.0.0.0:9868       0.0.0.0:*    users:(("java",pid=273258,fd=338)) 
LISTEN 0      500               0.0.0.0:9870       0.0.0.0:*    users:(("java",pid=272826,fd=342)) 
LISTEN 0      256             127.0.0.1:9000       0.0.0.0:*    users:(("java",pid=272826,fd=357)) 
LISTEN 0      4096              0.0.0.0:22         0.0.0.0:*                                       
LISTEN 0      50     [::ffff:127.0.0.1]:8443             *:*    users:(("java",pid=278874,fd=1821))
LISTEN 0      4096                 [::]:22            [::]:*                                       
```

## 9. Permissions
```
drwxr-xr-x  5 pauline pauline 4096 Nov 17 13:07 /data/nifi
drwxr-xr-x  2 pauline pauline 4096 Nov 17 13:07 /data/nifi/archive
drwxr-xr-x  2 pauline pauline 4096 Nov 17 13:07 /data/nifi/error
drwxr-xr-x  2 pauline pauline 4096 Nov 17 13:07 /data/nifi/input
drwxr-xr-x 12 pauline pauline 4096 Nov 17 12:14 /opt/hadoop
drwxrwxr-x 18 pauline pauline 4096 Nov 17 12:48 /opt/nifi
Found 1 items
drwxr-xr-x   - pauline supergroup          0 2026-11-17 13:05 /retail-lake
Found 6 items
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/bronze
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/gold
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:28 /retail-lake/logs
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:28 /retail-lake/quality
drwxr-xr-x   - pauline supergroup          0 2026-11-17 13:05 /retail-lake/raw
drwxr-xr-x   - pauline supergroup          0 2026-11-17 12:27 /retail-lake/silver
```

## 10. Analyse et contraintes

- **Type de déploiement** : mono-nœud pseudo-distribué. Environnement pédagogique, pas un cluster de production.
- **Séparation Java** : Hadoop utilise Java 17, NiFi utilise Java 21. Java 21 est le défaut du système.
- **Permissions** : /opt/hadoop, /opt/nifi et /data/nifi appartiennent à pauline, donc lisibles et écrivables par le processus NiFi. HDFS : /retail-lake appartient à pauline:supergroup.

