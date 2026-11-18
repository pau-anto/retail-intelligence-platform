# Fiche Hadoop et HDFS – Jour 2 (UC-03, étape 1)

Livrable : fiche décrivant l'environnement Hadoop, ses composants et leur état.

## 1. Résumé

L'environnement est un Hadoop 3.5.0 **mono-nœud en mode pseudo-distribué**, avec HDFS seul (aucun processus YARN dans `jps`). Aux relevés de 14:03 et 15:16, il comporte un NameNode actif, un DataNode vivant et aucun bloc corrompu, manquant ou sous-répliqué. Les journaux du NameNode et du SecondaryNameNode ne contiennent aucune ligne `ERROR` ou `FATAL`.

## 2. Identification

| Point relevé | Valeur |
| --- | --- |
| Version | Hadoop 3.5.0 |
| Révision du code source | `dbcc7cd797100e6b32cd84f85b53a5193a5f9af0` |
| Compilation | 2026-03-24T16:56Z par cnauroth |
| Chemin d'installation | `HADOOP_HOME = /opt/hadoop` |
| Dossier de configuration | `HADOOP_CONF_DIR = /opt/hadoop/etc/hadoop` |
| Java utilisé par Hadoop | OpenJDK 17.0.21 (le Java 21 par défaut du système est réservé à NiFi) |
| Données du NameNode | `/home/pauline/hadoop-data/namenode` |
| Données du DataNode | `/home/pauline/hadoop-data/datanode` |
| Identifiant de cluster | `CID-04c1d9bb-1ee3-4ac2-bfbc-2677049e726f` |
| Identifiant du pool de blocs | `BP-180555232-127.0.1.1-1794914086280` |

## 3. Configuration utilisée

| Fichier | Propriété | Valeur |
| --- | --- | --- |
| `core-site.xml` | `fs.defaultFS` | `hdfs://localhost:9000` |
| `hdfs-site.xml` | `dfs.replication` | `1` |
| `hdfs-site.xml` | `dfs.namenode.name.dir` | `file:///home/pauline/hadoop-data/namenode` |
| `hdfs-site.xml` | `dfs.datanode.data.dir` | `file:///home/pauline/hadoop-data/datanode` |

Aucune autre propriété n'est définie : la taille de bloc est la valeur par défaut de Hadoop.

## 4. Composants et état

| Composant | PID (14:03 et 15:16, inchangé) | Ports à l'écoute | État constaté |
| --- | --- | --- | --- |
| NameNode | 272826 | 9000 (RPC, local uniquement), 9870 (interface web) | Actif depuis le 17/11 à 12:14:55 ; Safemode désactivé ; sécurité désactivée |
| DataNode | 273010 | 9866 (transfert de données), 9867 (IPC) | 1 vivant, 0 mort ; statut de mise hors service « Normal » ; dernier rapport de blocs à 12:14:58 |
| SecondaryNameNode | 273258 | 9868 (interface web) | Actif |

Le journal des modifications du NameNode était `edits_inprogress_0000000000000000003` au moment de la capture de l'interface, avec un stockage `IMAGE_AND_EDITS` à l'état Active.

## 5. État de HDFS avant et après le dépôt

| Indicateur | Vers 12:26 (avant dépôt) | À 15:14 (après dépôt) |
| --- | --- | --- |
| Capacité configurée | 97,87 GB | 97,87 GB |
| DFS utilisé | 28 KB | 89,20 MB |
| DFS restant | 69,77 GB | 66,32 GB |
| Nombre de blocs | 0 | 1 |
| Blocs corrompus, manquants, sous-répliqués | 0 | 0 |

Le fichier `store_sales.dat` (92 764 700 octets) déposé à 12:40 occupe un seul bloc : sa taille est inférieure à la taille de bloc configurée (128 Mio).

## 6. Rôle des composants

- **NameNode.** Il tient les métadonnées du système de fichiers : l'arborescence, les droits et la correspondance entre chaque fichier et ses blocs. Il ne stocke pas les données elles-mêmes. Il sait où se trouvent les blocs grâce aux rapports des DataNodes, et conserve ses métadonnées sur disque sous forme d'image et de journal des modifications.
- **DataNode.** Il stocke les blocs sur son disque local, les sert en lecture et en écriture, et signale régulièrement son état et la liste de ses blocs au NameNode.
- **SecondaryNameNode.** Il fusionne périodiquement le journal des modifications dans l'image du NameNode (points de reprise). Ce n'est pas un NameNode de secours : il ne prend pas le relais en cas de panne.

## 7. Mono-nœud ou distribué

Le déploiement est **mono-nœud** : un seul DataNode, sur `localhost`, avec une réplication de 1. Chaque bloc n'existe qu'en un exemplaire et le NameNode est unique. La perte du disque ou du processus ferait donc perdre les données ou l'accès. C'est un environnement pédagogique pour apprendre les commandes HDFS, pas un cluster de production hautement disponible.

## 8. Erreurs de démarrage

- Le 17/11 à 15:16, `grep -iE "ERROR|FATAL" /opt/hadoop/logs/*namenode*.log` ne renvoie aucune ligne. Ce motif couvre les journaux du NameNode et du SecondaryNameNode.
- Journal du DataNode : aucune igne ERROR ouu FATAL

## 9. Sécurité et réseau

- HDFS fonctionne sans Kerberos (mode simple), avec l'utilisateur `pauline`.
- Le RPC du NameNode (9000) n'écoute qu'en local ; les ports 9866, 9867, 9868 et 9870 écoutent sur toutes les interfaces. Sur un réseau partagé, un pare-feu serait nécessaire.

## 10. Preuves

Les preuves sont rangées dans `preuves/hadoop/`.

| Preuve | Contenu | Fichier |
| --- | --- | --- |
| P1 | Interface NameNode : Overview et Summary, avant dépôt | `P01_hadoop_namenode-overview_avant-depot.png` |
| P02 | Interface NameNode : journal et stockage, avant dépôt | `P02_hadoop_namenode-stockage_avant-depot.png` |
| P03 | `hdfs dfsadmin -report`, avant dépôt (vers 12:26) | `P03_hadoop_dfsadmin-report.png` |
| P16 | `hadoop version`, `jps` et début de `dfsadmin -report` (15:16) | `P16_hadoop_version-jps-report.png` |

Les relevés complets de 14:03 sont dans `environnement-j2.md`, sections 3, 5, 6, 7 et 8.
