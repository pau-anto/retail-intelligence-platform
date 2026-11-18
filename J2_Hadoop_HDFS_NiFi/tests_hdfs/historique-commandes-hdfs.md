# Historique des commandes HDFS tapées pendant la séance du 17/11/2026

Extrait de `history | grep hdfs`, filtré sur les commandes HDFS et annoté. Les numéros sont ceux de l'historique du shell, qui ne conserve ni les heures ni les messages d'erreur.

- Les heures indiquées viennent des listings HDFS (`ls`, `ls -R`) et de la date du fichier récupéré.
- Les résultats marqués **(déduit)** sont déduits de la commande et des listings ; recopiez le message d'erreur exact si vous l'avez encore.

| Ligne | Commande | Étape | Résultat |
| --- | --- | --- | --- |
| 127 | `hdfs namenode -format` | Installation (§1.4) | Initialisation du NameNode, faite une seule fois avant le premier démarrage. Opération destructive : à ne jamais relancer. |
| 130 | `hdfs dfsadmin -report` | 1 | État de HDFS (voir `fiche-hadoop-hdfs.md`). |
| 131 | `hdfs dfs -ls` | 2 | Sans chemin, liste le dossier personnel HDFS de `pauline`, qui n'existe pas : échec **(déduit)**. |
| 132 | `hdfs dfs -ls /` | 2 | Liste la racine de HDFS. |
| 133 | `hdfs -mkdir -p /retail-lake/raw/tpcxbb/initial` | 3 | **Échec** : la sous-commande `dfs` est oubliée. Corrigé à la ligne 134. |
| 134 | `hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/initial` | 3 | Création de `raw/tpcxbb/initial`, vers 12:27. |
| 135 à 139 | `hdfs dfs -mkdir -p` pour `bronze/tpcxbb`, `silver`, `gold`, `quality`, `logs` | 3 | Zones créées entre 12:27 et 12:28. |
| 140 | `hdfs dfs -ls /` | 3 | Vérification. |
| 141 | `hdfs dfs -put ./ventes.csv /retail-lake/raw/tpcxbb/initial/` | 4 | **Échec (déduit)** : `ventes.csv` est le nom d'exemple du TP, absent du kit. |
| 143 | `hdfs dfs -mkdir -p /retail-lake/raww/tpcxbb/refresh` | 3 | **Faute de frappe** (`raww`) : crée un dossier parasite, vers 12:30. |
| 144 | `hdfs dfs -mkdir -p /retail-lake/raww/nifi` | 3 | Même faute, même dossier parasite. |
| 145 | `hdfs dfs -ls -R /retail_lake` | 3 | **Échec (déduit)** : `_` au lieu de `-`, le chemin n'existe pas. |
| 146 | `hdfs dfs -ls -R /retail-lake` | 3 | Montre le dossier `raww` (capture P14). |
| 180 | `hdfs dfs -put retail/projet/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/intitial/` | 4 | **Échec (déduit)** : chemin local erroné (`retail/projet`) et faute dans la destination (`intitial`). Rien n'a été écrit : aucun dossier `intitial` dans les listings. |
| 184 | `hdfs dfs -put retail_project/data/store_sales/store_sales.dat /retail-lake/raw/tpcxbb/initial/` | 4 | **Dépôt réussi** : fichier daté de 12:40 dans HDFS. |
| 185 | `hdfs dfs -ls -h /retail-lake/raw/tpcxbb/initial` | 4 | Présence et taille du fichier. |
| 186 | `hdfs dfs -cat …/store_sales.dat \| head -3` | 5 | Lecture contrôlée. |
| 188 | `hdfs dfs -ls /retail-lake/raw/tpcxbb/initial/store_sales.dat` | 5 | Taille et permissions. |
| 190 | `hdfs dfs -cat …/store_sales.dat \| sha256sum` | 5 | Empreinte du fichier lu dans HDFS. |
| 191 | `hdfs dfs -du -h /retail-lake` | 5 | Taille des données stockées. |
| 192 | `hdfs dfs -get /retail-lake/raw/tpcxbb/initial/store_sales.dat` | 5 | **Récupération** dans le dossier courant : le `store_sales.dat` de 92 764 700 octets daté de 12:43, à la racine de `DataLake Warehouse Lakehouse`. |
| 235 | `hdfs dfs -ls -R /retail-lake/raww` | Correction | Inspection du dossier parasite avant suppression. |
| 236 | `hdfs dfs -rm -r /retail-lake/raww` | Correction | Suppression du dossier parasite, vers 13:05. |
| 237 | `hdfs dfs -mkdir -p /retail-lake/raw/tpcxbb/refresh` | 3 | Création de `raw/tpcxbb/refresh`, vers 13:05. |
| 238 | `hdfs dfs -mkdir -p /retail-lake/raw/nifi` | 3 | Création de `raw/nifi`, vers 13:05. |
| 239 et 274 | `hdfs dfs -ls -R /retail-lake` | 3 | Vérification de l'arborescence corrigée (capture P4). |
| 256 à 258 | `… \| sha256sum`, `… \| wc -l`, puis génération du rapport v1 | 5 | Rapport de vérification de 13:08 : somme de contrôle et nombre de lignes. |
| 283 et 306 | Génération du rapport v2 | 5 | Rapport complet de 14:47. |
| 322, 328, 329 | `hdfs dfsadmin -report`, `hdfs getconf -confKey dfs.blocksize`, `hdfs dfs -du -h /retail-lake` | 1 et 2 | Compléments de la fiche Hadoop et du journal. |
| 335 | Génération du journal de l'étape 2 | 2 | `journal-commandes-hdfs.md`. |
