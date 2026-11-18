# Schéma et description du flux d'ingestion NiFi (UC-04)

## 1. Ce qui a été réellement exécuté

Le flux obligatoire à deux processeurs : `GetFile` → `PutHDFS`. Rien de plus n'a été construit : l'approfondissement (UpdateAttribute, RouteOnAttribute, LogAttribute) ne fait pas partie de ce rendu.

## 2. Composants

| Composant | Rôle | Propriétés principales |
|---|---|---|
| `GetFile` | Lit le fichier dans le dossier d'entrée et crée le FlowFile | Input Directory `/data/nifi/input` ; Keep Source File `false` ; Recurse Subdirectories `false` |
| Connexion `success` | Transporte le FlowFile de `GetFile` vers `PutHDFS`, avec une file d'attente | Relation `success` |
| `PutHDFS` | Écrit le contenu dans HDFS | Hadoop Configuration Resources `/opt/hadoop/etc/hadoop/core-site.xml,/opt/hadoop/etc/hadoop/hdfs-site.xml` ; Directory `/retail-lake/raw/nifi` ; Conflict Resolution Strategy `fail` |
| Provenance Repository | Enregistre les événements de chaque FlowFile | Voir `documentation-provenance-nifi.md` |

## 3. Relations

| Processeur | Relation | Traitement |
|---|---|---|
| `GetFile` | `success` | Reliée à `PutHDFS` |
| `PutHDFS` | `success` | Auto-terminée : le FlowFile se termine une fois déposé |
| `PutHDFS` | `failure` | Reliée à `PutHDFS` lui-même : un fichier en échec reste en file d'attente, visible pour le diagnostic |

La relation d'échec n'est pas supprimée : le TP demande de l'examiner avant toute suppression.

## 4. Choix de configuration et leur raison

- `Keep Source File = false` : le fichier est retiré du dossier d'entrée après lecture. Seule une copie de travail y est placée ; l'original reste dans `retail_project`.
- `Conflict Resolution Strategy = fail` : un fichier existant n'est jamais écrasé en silence.
- Destination `/retail-lake/raw/nifi`, distincte de `/retail-lake/raw/tpcxbb/initial` (UC-03) : les deux méthodes se comparent sans écraser le dépôt manuel.

## 5. Résultat observé

- `GetFile` : 1 fichier lu (88,47 Mo). `PutHDFS` : 1 fichier reçu, file `failure` à 0.
- Fichier présent dans `/retail-lake/raw/nifi` (88,5 M, 17:02), SHA-256 identique à la source.
- Dossier d'entrée vide après le traitement.

Preuves : P24, P26, P27, P28, P29, P30, P33 à P35.
