# Architecture du Data Lake /retail-lake (UC-03, étape 3)

## 1. Arborescence HDFS créée

```
/retail-lake
├── raw
│   ├── tpcxbb
│   │   ├── initial        (contient store_sales.dat, 92 764 700 octets)
│   │   └── refresh        (vide)
│   └── nifi               (vide, destination du flux NiFi)
├── bronze
│   └── tpcxbb             (vide)
├── silver                 (vide)
├── gold                   (vide)
├── quality                (vide)
└── logs                   (vide)
```

Commandes utilisées : `hdfs dfs -mkdir -p /retail-lake/...` puis `hdfs dfs -ls -R /retail-lake` pour vérifier.
Une faute de frappe (`raww`) a été corrigée par `hdfs dfs -rm -r /retail-lake/raww` ; elle est documentée dans le tableau des erreurs.

## 2. Rôle de chaque zone

| Zone | Chemin | Rôle | État |
|---|---|---|---|
| Raw | `/retail-lake/raw/tpcxbb/initial` | Copie brute du lot initial TPCx-BB | 1 fichier déposé |
| Raw | `/retail-lake/raw/tpcxbb/refresh` | Copie brute du lot de rafraîchissement | vide |
| Raw | `/retail-lake/raw/nifi` | Fichiers ingérés par NiFi, sans transformation | vide (flux à exécuter) |
| Bronze | `/retail-lake/bronze/tpcxbb` | Données reçues, rendues exploitables (format, schéma, métadonnées d'ingestion) | vide (Jour 3) |
| Silver | `/retail-lake/silver` | Données contrôlées et nettoyées | vide (Jour 3) |
| Gold | `/retail-lake/gold` | Jeux analytiques et indicateurs par besoin métier | vide (Jour 3) |
| Quality | `/retail-lake/quality` | Résultats des contrôles qualité, rejets | vide |
| Logs | `/retail-lake/logs` | Journaux d'ingestion, fiches de provenance | vide |

## 3. Explications demandées

### 3.1 Pourquoi conserver les données sources

- Elles sont la référence : si un traitement est faux, on peut le rejouer depuis l'original.
- Elles permettent de prouver l'intégrité : on peut montre ce qui a été reçu, avant toute transformation.
- Elles protègent contre une erreur humaine : une transformation ne détruit jamais la seule copie.
- Exemple concret : `store_sales.dat` (92 764 700 octets, 667 579 lignes, 23 champs) est conservé tel quel, avec une empreinte SHA-256 identique à la source locale.

### 3.2 Différence entre Raw et Bronze

- **Raw** : copie fidèle, octet pour octet. Aucun changement de format, d'encodage ou de contenu. Les fichiers TPCx-BB gardent leur forme d'origine .
- **Bronze** : mêmes données, mais préparées pour être lues de façon fiable : format et schéma déclarés (les colonnes ne sont identifiées que par leur position dans le kit), métadonnées d'ingestion ajoutées (source, date, lot).

### 3.3 Rôle de Silver et Gold

- **Silver** : on y applique les contrôles et corrections. Dans notre inventaire, cela concerne par exemple les colonnes entièrement vides, très peu remplies, la gestion des valeurs manquantes, des types, des clés et des doublons.
- **Gold** : on y publie les jeux prêts pour l'analyse, organisés par besoin métier (par exemple les ventes en magasin par période ou par produit). Seules des données déjà validées en Silver y arrivent.

### 3.4 Pourquoi séparer données métier, contrôles qualité et logs

- **Données métier** : ce sont elles que l'on analyse ; leur volume et leurs droits d'accès sont ceux du métier.
- **Contrôles qualité (`quality`)** : les rapports et rejets ont un autre cycle de vie et un autre public (équipe qualité). Les mélanger aux données polluerait les jeux analytiques.
- **Logs et provenance (`logs`)** : ils décrivent le fonctionnement des traitements, pas le contenu des données. Séparés, ils restent consultables et archivables sans toucher aux données.
- Cette séparation permet aussi de donner des droits différents par zone et d'éviter qu'un outil de lecture analytique ne lise des fichiers techniques.

### 3.5 Comment la provenance sera conservée

Deux niveaux :

1. **Manuel (HDFS)** : une fiche de provenance par fichier déposé.
2. **Automatique (NiFi)** : le flux GetFile → PutHDFS génère des événements de provenance (réception, envoi, nom de fichier, horodatage), consultables dans NiFi (étape 11).

Fiche de provenance, exemple pour le fichier déjà déposé :

| Champ | Valeur |
|---|---|
| Nom de la source | store_sales.dat |
| Domaine | Ventes en magasin |
| Chemin d'origine | `retail_project/data/store_sales.dat` (machine locale) |
| Destination | `/retail-lake/raw/tpcxbb/initial/store_sales.dat` |
| Date et heure de dépôt | 17/11/2026, 12:40 |
| Méthode | `hdfs dfs -put` |
| Taille | 92 764 700 octets |
| Lignes / champs | 667 579 lignes, 23 champs |
| SHA-256 | `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e` |
| Version du kit | TPCx-BB 1.7.0 |
| Vérification | Copie `get` retirée de HDFS, SHA-256 identique |

## 4. Points à signaler

- Les zones Bronze, Silver, Gold, quality et logs sont créées mais vides : leur alimentation relève du Jour 3.
- `raw/tpcxbb/refresh` et `raw/nifi` seront remplies après l'étape 9 (exécution du flux) ou lors du dépôt du lot refresh.
- La distinction Raw / Bronze est une convention de groupe, à expliquer à l'oral si le formateur pose la question.
