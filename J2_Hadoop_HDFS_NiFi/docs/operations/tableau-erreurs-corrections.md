# Tableau des erreurs et des corrections

Les heures viennent des listings HDFS et des journaux. Les résultats marqués « déduit » viennent de la commande et du résultat obtenu ensuite : l'historique du shell ne conserve pas les messages d'erreur.

## UC-03 : Hadoop et HDFS

| N° | Étape | Erreur | Cause | Correction | Preuve |
|---|---|---|---|---|---|
| 1 | 3 | `hdfs -mkdir -p /retail-lake/raw/tpcxbb/initial` échoue | Sous-commande `dfs` oubliée | `hdfs dfs -mkdir -p …` | `historique-commandes-hdfs.md` (lignes 133-134) |
| 2 | 4 | `hdfs dfs -put ./ventes.csv …` échoue (déduit) | `ventes.csv` est le nom d'exemple du TP, absent du kit | Choix d'un fichier réel du kit : `store_sales.dat` | `historique-commandes-hdfs.md` (ligne 141) |
| 3 | 3 | `hdfs dfs -ls -R /retail_lake` échoue (déduit) | `_` au lieu de `-` dans le nom du répertoire | `hdfs dfs -ls -R /retail-lake` | `historique-commandes-hdfs.md` (lignes 145-146) |
| 4 | 3 | Dossier parasite `/retail-lake/raww` créé vers 12:30 | Faute de frappe (`raww`) dans deux `mkdir` | `hdfs dfs -rm -r /retail-lake/raww` puis recréation de `raw/tpcxbb/refresh` et `raw/nifi` vers 13:05 | P4 (arborescence finale) |
| 5 | 4 | `hdfs dfs -put retail/projet/… …/intitial/` échoue (déduit) | Chemin local erroné (`retail/projet`) et faute dans la destination (`intitial`) ; rien n'a été écrit | Commande corrigée avec `retail_project` et `initial`, dépôt réussi à 12:40 | `historique-commandes-hdfs.md` (lignes 180-184) |
| 6 | 5 | `cat: Unable to write to output stream` | `head` ferme le tube avant la fin de lecture de `hdfs dfs -cat` | Aucune : message sans gravité, résultat correct | P17 |

## UC-04 : NiFi

| N° | Étape | Erreur | Cause | Correction | Preuve |
|---|---|---|---|---|---|
| 7 | 6 et 8 | Processeur `PutHDFS` introuvable : aucun module Hadoop dans `/opt/nifi/lib` | L'installation NiFi 2.12.0 ne contenait pas `nifi-hadoop-nar` ni `nifi-hadoop-libraries-nar` | Téléchargement des deux modules 2.12.0 depuis Maven Central dans `/opt/nifi/extensions` ; NiFi les charge à chaud (journal 16:33 et 16:34) ; `PutHDFS` apparaît dans l'interface | P18, P19, P20, `installation-module-hadoop-nifi.md` |
| 8 | 6 | `bash: cd: too many arguments` (deux fois) | Plusieurs commandes collées sur une seule ligne | Commandes lancées une par une | `installation-module-hadoop-nifi.md` |
| 9 | 6 | Fichier `nifi-hadoop-nar-2.12.0.nar.1` créé | Second téléchargement du même module | Doublon supprimé ; NiFi l'avait ignoré (« Skipping non-nar file ») | `installation-module-hadoop-nifi.md` |
| 10 | 8 | `PutHDFS` invalide : « Relationship 'success' / 'failure' is not connected to any component and is not auto-terminated » | Relations de sortie ni reliées ni auto-terminées | `success` auto-terminée ; `failure` reliée à `PutHDFS` lui-même | P25 |
| 11 | 10 | `GetFile` invalide : « 'Input Directory' validated against '/data/nifi/inexistant' is invalid because Directory does not exist » | Erreur volontaire : dossier source inexistant | Input Directory rétabli à `/data/nifi/input` | P31, P32, `erreur-controlee-nifi.md` |

Remarque sur l'erreur 11 : le `grep` du journal ne renvoie rien, car l'erreur est détectée par la validation du processeur avant toute exécution. Elle n'est visible que sur le canevas.

