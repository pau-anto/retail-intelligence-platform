# Comparaison des formats : CSV (`.dat`) et Parquet 

Formats réellement utilisés : les fichiers sources `.dat` (texte délimité par `|`, sans en-tête, donc un CSV) et le format Parquet écrit par Spark. 

## 1. Production et relecture Parquet

| Élément | Résultat | Preuve |
| --- | --- | --- |
| Écriture | `df.write.mode("overwrite").parquet(...)` vers un dossier dédié (`data/silver`, `data/gold`, `data/quarantine`, `outputs`) | `P04_ecriture_resultat.png`, `P06_presence_format_taille_parquet.png` |
| Relecture | `spark.read.parquet(...)` fonctionne sur les 8 jeux | `P07_silver_schema_lignes.png`, `P08_gold_schema_lignes.png` |
| Schéma conservé | types integer, double, date, boolean et long retrouvés tels quels | `P07_silver_schema_lignes.png` |
| Nombre de lignes | cohérent : 667 579 (`store_sales`), 17 820 (`item`), 5 (`ca_par_annee`) | `P07_silver_schema_lignes.png`, `P11_relecture_parquet_gold.png` |
| Valeurs exploitables | `ca_par_annee` relu avec les 5 années et leurs totaux | `P11_relecture_parquet_gold.png` |
| Répertoire de sortie | un dossier par jeu, avec `_SUCCESS` et des fichiers `.snappy.parquet` | `P06_presence_format_taille_parquet.png` |

`mode("overwrite")` n'est utilisé que sur des dossiers de sortie dédiés, jamais sur `raw/`.

## 2. Volume de stockage observé

| Table | Source `.dat` | Silver Parquet | Rapport Parquet / `.dat` | Gain |
| --- | --- | --- | --- | --- |
| `item` | 6 799 286 octets (6,48 Mo) | 3,52 Mo (5 fichiers) | 54,3 % | environ 46 % |
| `store_sales` | 92 764 700 octets (88,47 Mo) | 64,79 Mo (200 fichiers) | 73,2 % | environ 27 % |

Les tailles Silver viennent de la cellule « présence, format et taille » (`P06`), calculées en Mo (1 Mo = 1 048 576 octets).

Lecture prudente de ces chiffres :
- Le Silver n'est pas strictement comparable à la source : il a quatre colonnes de plus pour `store_sales` (`date_vente`, `vente_a_perte`, `prix_nul`, `ligne_id`) et une de moins en net pour `item` (deux colonnes vides retirées, `_c3` et `_c19`, un indicateur ajouté).
- Le gain est donc modéré sur `store_sales` : les colonnes numériques `double` et `integer` de ces données sont peu compressibles.
- `item` gagne davantage, car il contient beaucoup de texte répété.
- Les Gold, qui sont des agrégats, occupent moins de 0,2 Mo chacun (`ca_par_produit` 0,2 Mo, les trois autres affichés à 0,0 Mo après arrondi).

## 3. Comparaison

| Critère | CSV (`.dat` délimité par `|`) | Parquet |
| --- | --- | --- |
| Organisation des données | Par lignes : chaque ligne contient tous les champs | Par colonnes, regroupées en blocs avec des statistiques |
| Lisibilité | Lisible directement dans un éditeur de texte | Binaire : lisible seulement avec un outil (Spark, pandas, etc.) |
| En-tête et noms de colonnes | Aucun dans les `.dat` : colonnes `_c0`… | Noms conservés dans le fichier |
| Gestion des types | Aucune : tout est du texte, les types sont déduits (`inferSchema`) | Types stockés dans le fichier (integer, double, date, boolean) |
| Volume | Plus volumineux (voir section 2) | Plus compact grâce à la compression (snappy) |
| Lecture analytique | Lit toutes les colonnes d'une ligne | Peut lire seulement les colonnes utiles |
| Écriture | Simple, partout compatible | Nécessite une bibliothèque, écrit plusieurs fichiers avec Spark |
| Usages adaptés | Échange simple, import, source brute | Zones Silver et Gold, analyses, agrégations |

## 4. Avantages et limites dans ce TP

CSV (`.dat`) :
- Avantages : universel, lisible, c'est le format d'origine de la source (la zone `raw/` reste inchangée).
- Limites : pas de types ni de noms de colonnes (il a fallu déduire les types avec `inferSchema` et renommer des colonnes `_cN`), plus lourd, lecture complète.

Parquet :
- Avantages : types et schéma conservés à la relecture (vérifié), fichier plus petit, adapté aux calculs sur quelques colonnes.
- Limites : non lisible à la main, plusieurs fichiers par jeu (200 pour `store_sales` en local, c'est le comportement par défaut de Spark), pas de modification d'une ligne sans réécriture du jeu.

