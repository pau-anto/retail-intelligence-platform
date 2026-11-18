# Documentation de la provenance NiFi

## 1. FlowFile observé

| Élément | Valeur |
|---|---|
| Fichier | `store_sales.dat` (copie de travail placée dans `/data/nifi/input`) |
| Taille | 88,47 Mo (92 764 700 octets) |
| FlowFile UUID | `c4c6ff5c-836a-4db0-9255-c0fc26ad52de` |
| Source | `/data/nifi/input` (lecture par `GetFile`) |
| Destination | `/retail-lake/raw/nifi` (écriture par `PutHDFS`) |
| Parents / enfants | Aucun : le FlowFile n'a pas été découpé ni fusionné |

## 2. Événements de provenance

| Heure | Type | Composant | Lecture |
|---|---|---|---|
| 17:02:09.834 | RECEIVE | `GetFile` | NiFi prend le fichier dans `/data/nifi/input` |
| 17:02:10.218 | SEND | `PutHDFS` | Le contenu est envoyé vers HDFS (durée de l'événement : 0,346 s) |
| 17:02:10.219 | ATTRIBUTES_MODIFIED | `PutHDFS` | Des attributs du FlowFile sont ajoutés ou modifiés par `PutHDFS` |
| 17:02:10.219 | DROP | `PutHDFS` | Le FlowFile se termine : la relation `success` est auto-terminée |

Durée de vie du FlowFile dans NiFi (Lineage Duration) : 0,447 s.
Le composant `PutHDFS` a pour identifiant `ea366103-01a1-1000-c071-8da90a65dc1a`.

Le graphe de lignage montre la chaîne : RECEIVE (`GetFile`) → connexion `success` → SEND → ATTRIBUTES_MODIFIED → DROP (`PutHDFS`). Il n'y a aucune branche : pas d'événement d'échec pour ce fichier.

## 3. Comment ces informations reconstituent le parcours

- L'**identifiant du FlowFile** relie tous les événements : on suit un même fichier du début à la fin, même s'il traverse plusieurs composants.
- Le **type d'événement** dit ce qui s'est passé : entrée dans le flux (RECEIVE), sortie vers un système externe (SEND), modification d'attributs, fin de vie (DROP).
- Le **composant** et son identifiant disent où cela s'est passé.
- L'**heure** donne l'ordre et la durée de chaque étape.
- La **taille** (88,47 Mo à chaque étape) confirme que le contenu n'a pas été altéré en route.
- L'absence de parents, d'enfants et d'événement d'échec montre que le fichier a suivi le chemin prévu, sans détour.

On peut ainsi répondre à : quel fichier est entré, quand, par quel composant, où il est parti, et s'il y a eu un incident.

## 4. Lien avec la fiche de provenance manuelle

| | UC-03 (manuel) | UC-04 (NiFi) |
|---|---|---|
| Méthode | `hdfs dfs -put` | `GetFile` → `PutHDFS` |
| Destination | `/retail-lake/raw/tpcxbb/initial` | `/retail-lake/raw/nifi` |
| Heure du dépôt | 12:40 | 17:02 |
| Trace de provenance | Fiche rédigée à la main (source, destination, SHA-256) | Événements enregistrés automatiquement par NiFi |
| SHA-256 du fichier en HDFS | `7e0a7f16…ed3d2e` | `7e0a7f16…ed3d2e` (identique) |

La fiche manuelle décrit ce que l'opérateur a fait ; la provenance NiFi enregistre ce que le système a fait, sans intervention. Les deux se complètent : NiFi donne le parcours et l'horodatage, la fiche donne l'intégrité (SHA-256) et la version du kit.

## 5. Limites

- Cette provenance porte sur un seul fichier, traité une seule fois.
- Le détail de l'événement SEND (adresse de destination exacte, attributs `filename` et `path`) est à compléter depuis les onglets Details et Attributes.

## 6. Preuves

| Capture | Contenu |
|---|---|
| `P33_nifi_provenance-evenements.png` | Liste des quatre événements |
| `P34_nifi_provenance-detail-send.png` | Détail de l'événement SEND |
| `P35_nifi_provenance-lineage.png` | Graphe du parcours du FlowFile |
