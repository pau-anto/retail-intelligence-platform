# Rapport de vérification du stockage HDFS (UC-03, étape 5)

Livrable : **Rapport de vérification du stockage HDFS**
Date : 17/11/2026 · Utilisateur HDFS : `pauline` · Fichier contrôlé : `store_sales.dat`
Emplacement conseillé : `docs/ingestion/rapport-verification-stockage-hdfs.md`
Sources brutes : `tests_hdfs/rapport-verification.txt` (exécution de 14:47) et `tests_hdfs/controle-recuperation.txt`

## 1. Synthèse

| Contrôle demandé | Résultat | Verdict |
|---|---|---|
| Répertoires attendus présents | 11 répertoires, conformes à l'architecture | Conforme |
| Fichier déposé présent | `/retail-lake/raw/tpcxbb/initial/store_sales.dat` | Conforme |
| Taille | 92 764 700 octets en HDFS et en local | Conforme |
| Permissions | Fichier `-rw-r--r--`, répertoires `drwxr-xr-x`, propriétaire `pauline`, groupe `supergroup` | Consulté |
| Lecture ou récupération contrôlée | Lecture (`-cat`) et récupération (`-get`) réussies | Conforme |
| Comparaison source / stockage | SHA-256 identique, 667 579 lignes | Conforme |

Conclusion : le fichier stocké dans HDFS est identique à la source locale, qui est conservée.

## 2. Détail des contrôles

### 2.1 Répertoires (`hdfs dfs -ls -R /retail-lake`)

Présents : `raw`, `raw/tpcxbb`, `raw/tpcxbb/initial`, `raw/tpcxbb/refresh`, `raw/nifi`, `bronze`, `bronze/tpcxbb`, `silver`, `gold`, `quality`, `logs`.
Aucun répertoire en trop (la faute `raww` a été supprimée, voir tableau des erreurs).

### 2.2 Fichier déposé, taille et permissions

```
-rw-r--r--   1 pauline supergroup   92764700 2026-11-17 12:40 /retail-lake/raw/tpcxbb/initial/store_sales.dat
```

- Facteur de réplication : 1 (cluster mono-nœud).
- Taille identique à la source locale : `stat` donne 92 764 700 octets.
- Le fichier tient dans 1 bloc (taille de bloc 134 217 728 octets).

### 2.3 Permissions

| Élément | Droits | Lecture |
|---|---|---|
| Répertoires du lac | `rwxr-xr-x` | Le propriétaire écrit ; groupe et autres lisent et parcourent |
| Fichier `store_sales.dat` | `rw-r--r--` | Le propriétaire modifie ; les autres ne font que lire |

Commentaire : ces droits sont les valeurs par défaut de HDFS. Il n'y a pas de Kerberos ni d'ACL configurés : le contrôle d'accès repose sur le nom d'utilisateur, ce qui suffit pour ce TP mono-utilisateur mais serait insuffisant en production. Pour protéger la zone Raw, il faudrait retirer l'écriture au propriétaire après dépôt ou la restreindre à un compte d'ingestion.

### 2.4 Lecture contrôlée

`hdfs dfs -cat … | head -n 2` renvoie deux lignes de 23 champs séparés par `|`, cohérentes avec le format attendu.

### 2.5 Récupération contrôlée

Le fichier a été récupéré avec `hdfs dfs -get` vers un emplacement local distinct, puis son SHA-256 a été comparé à celui de la source : identique (voir `controle-recuperation.txt`). La copie de contrôle ne remplace pas la source.

### 2.6 Comparaison source locale / stockage

| Mesure | Local | HDFS |
|---|---|---|
| Taille (octets) | 92 764 700 | 92 764 700 |
| Lignes | 667 579 | 667 579 |
| SHA-256 | `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e` | `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e` |

## 3. Méthode réellement utilisée

- Somme de contrôle **SHA-256** (`sha256sum`), calculée sur le fichier local puis sur le flux lu dans HDFS (`hdfs dfs -cat | sha256sum`), sans copie intermédiaire. Elle a été confirmée par la copie `-get`.
- Nous n'avons pas utilisé `hdfs dfs -checksum` : il donne une somme propre à HDFS (par blocs et par CRC), non comparable à une somme calculée en local.
- Le message `cat: Unable to write to output stream` vu pendant l'exécution est sans gravité : il apparaît quand `head` ferme le tube avant la fin de lecture.

## 4. Limites

- Seul `store_sales.dat` est déposé ; les 35 autres fichiers du kit n'ont pas été vérifiés.
- Une exécution antérieure du rapport (v1, 13:08) ne comportait que taille, SHA-256 et nombre de lignes ; la version 2 y ajoute répertoires, permissions et lecture contrôlée.
- Le contrôle porte sur le contenu du fichier, pas sur la santé des blocs (`hdfs fsck` non exécuté).
