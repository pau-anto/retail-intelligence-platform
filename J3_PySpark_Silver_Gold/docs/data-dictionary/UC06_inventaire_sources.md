# Inventaire technique des sources – TP3 Retail Intelligence Platform

Date des relevés : 2026-11-18
Environnement : Python 3.14.4, PySpark 4.3.0, Spark `local[*]`, Jupyter dans VS Code (voir `fiche_environnement.md`)

## 1. Sources retenues

| Source | Domaine | Question du Jour 1 couverte |
| --- | --- | --- |
| `store_sales` | Ventes magasin | Quels produits génèrent le plus de ventes ? Évolution des ventes dans le temps. CA et marge par catégorie. |
| `item` | Produits | CA par article et par catégorie (référentiel produit). |

`store_sales` et `item` sont choisies parce qu'elles permettent de répondre à la question prioritaire « quels produits génèrent le plus de ventes ? » (CA par article et par catégorie). Les tables `store`, `store_returns` et les ventes web restent des sources possibles pour la suite.

## 2. Tableau d'inventaire

| Information | Source 1 : `store_sales` | Source 2 : `item` |
| --- | --- | --- |
| Nom réel du fichier | `store_sales.dat` | `item.dat` |
| Emplacement | `.../J3/data/raw/data/store_sales/` | `.../J3/data/raw/data/item/` |
| Format | Texte délimité par `\|`, sans en-tête | Texte délimité par `\|`, sans en-tête |
| Taille | 89 Mo | 6,5 Mo |
| Nombre de lignes | 667 579 | 17 820 |
| Nombre de colonnes | 23 | 22 |
| Colonnes principales | `_c0` à `_c22` (noms techniques, à renommer) | `_c0` à `_c21` (noms techniques, à renommer) |
| Types observés | `_c0`–`_c10` : integer ; `_c11`–`_c22` : double | 6 entiers, 13 textes, 1 date (`_c2`), 2 décimaux (`_c5`, `_c6`) |
| Clé candidate | Aucune clé naturelle stricte confirmée. `(_c9, _c2, _c8)` : 667 565 distincts sur 667 579, soit 14 lignes en excédent (0,002 %). `(_c9, _c2)` : 663 443 distincts, soit 4 136 lignes en excédent. `_c9` seule : 89 100 valeurs distinctes. Une clé technique sera ajoutée à l'étape Silver. | `_c0` : 17 820 distincts sur 17 820 (unique), utilisée pour la jointure avec `store_sales._c2`. `_c1` aussi unique. |
| Granularité | Une ligne = une ligne de ticket (un article avec ses montants). 89 100 tickets distincts, environ 7,5 lignes par ticket. Un même produit peut apparaître plusieurs fois dans un ticket. | Une ligne = un produit (17 820 produits). |
| Anomalies identifiées | Valeurs manquantes rares : `_c4` (238), `_c5` (295), `_c6` (448), `_c8` (158). 4 038 groupes `(_c9, _c2)` répétés, sans aucune ligne identique sur les 23 colonnes. Prix différents pour un même produit dans un même ticket. `_c22` négatif sur 74,3 % des lignes (495 971). Aucune quantité ≤ 0. | `_c3` vide sur 100 % des lignes (17 820). Valeurs manquantes rares : `_c4` (4), `_c7` (8), `_c8` (6). Descriptions sans sens, marques et noms de produits illisibles. |

## 3. Schémas observés

### `store_sales` (`printSchema`)

```
root
 |-- _c0:  integer      |-- _c12: double
 |-- _c1:  integer      |-- _c13: double
 |-- _c2:  integer      |-- _c14: double
 |-- _c3:  integer      |-- _c15: double
 |-- _c4:  integer      |-- _c16: double
 |-- _c5:  integer      |-- _c17: double
 |-- _c6:  integer      |-- _c18: double
 |-- _c7:  integer      |-- _c19: double
 |-- _c8:  integer      |-- _c20: double
 |-- _c9:  integer      |-- _c21: double
 |-- _c10: integer      |-- _c22: double
 |-- _c11: double
```

Les noms de colonnes sont ceux donnés par défaut par Spark, car les fichiers n'ont pas d'en-tête.

### `item` (`printSchema`)

```
root
 |-- _c0: integer (nullable = true)
 |-- _c1: string (nullable = true)
 |-- _c2: date (nullable = true)
 |-- _c3: string (nullable = true)
 |-- _c4: string (nullable = true)
 |-- _c5: double (nullable = true)
 |-- _c6: double (nullable = true)
 |-- _c7: integer (nullable = true)
 |-- _c8: string (nullable = true)
 |-- _c9: integer (nullable = true)
 |-- _c10: string (nullable = true)
 |-- _c11: integer (nullable = true)
 |-- _c12: string (nullable = true)
 |-- _c13: integer (nullable = true)
 |-- _c14: string (nullable = true)
 |-- _c15: string (nullable = true)
 |-- _c16: string (nullable = true)
 |-- _c17: string (nullable = true)
 |-- _c18: string (nullable = true)
 |-- _c19: string (nullable = true)
 |-- _c20: integer (nullable = true)
 |-- _c21: string (nullable = true)
```

## 4. Réponses aux questions techniques

| Question | Réponse |
| --- | --- |
| 1. Structurés, semi-structurés ou non structurés ? | Structurés : fichiers tabulaires avec séparateur fixe `\|` et le même nombre de colonnes sur chaque ligne. |
| 2. Colonnes correctement typées ? | Partiellement. `store_sales` : entiers pour les 11 premières colonnes (identifiants et quantité probables), décimaux ensuite (montants probables). `item` : une date reconnue (`_c2`), deux décimaux (`_c5`, `_c6`), des entiers et des textes. `_c3` est typée en texte parce qu'elle est entièrement vide. Sans en-tête ni dictionnaire, le sens des colonnes reste à confirmer. |
| 3. Valeurs nulles ? | `store_sales` : oui, mais rares. `_c4` : 238, `_c5` : 295, `_c6` : 448, `_c8` : 158 (entre 0,02 % et 0,07 % des lignes). `item` : `_c3` entièrement vide (17 820 sur 17 820) ; `_c4` (4), `_c7` (8) et `_c8` (6) rarement manquantes (moins de 0,05 %). |
| 4. Identifiants uniques ? | `item` : oui, `_c0` et `_c1` sont uniques (17 820 sur 17 820). `store_sales` : non, aucune clé naturelle stricte. `(_c9, _c2, _c8)` laisse 14 lignes en excédent, et aucune ligne n'est entièrement identique. |
| 5. Granularité connue ? | Non documentée dans les fichiers. Observée : une ligne de `store_sales` = une ligne de ticket (89 100 tickets, environ 7,5 lignes chacun) ; une ligne d'`item` = un produit. |
| 6. Données adaptées aux questions du Jour 1 ? | Oui pour « quels produits génèrent le plus de ventes ? » : montants et quantités dans `store_sales`, produits dans `item`, jointure complète (0 produit vendu absent d'`item`). Limites : marques et noms de produits illisibles ; marge négative sur 74,3 % des lignes, à traiter avec précaution pour la marge brute. |

## 5. Premiers constats

- **Volumétrie** : `store_sales` compte 667 579 lignes (89 Mo) et 23 colonnes ; `item` compte 17 820 lignes (6,5 Mo) et 22 colonnes. Soit environ 37 lignes de vente par produit en moyenne. Les volumes restent lisibles en local avec Spark.
- **Absence d'en-tête** : aucune des deux tables n'a de noms de colonnes, ce qui impose de les renommer avant toute analyse.
- **Jointure ventes / produits validée** : 0 produit vendu absent d'`item`, donc `store_sales._c2` correspond à `item._c0`.
- **Cohérence des montants** : sur toutes les lignes de `store_sales`, `_c15 = _c10 × _c13` et `_c22 = _c20 − _c16` (0 écart dans les deux cas). `_c22` se comporte donc comme un profit : montant payé moins coût d'achat. Cette lecture est déduite des calculs, pas d'une documentation.
- **Quantités** : aucune quantité nulle ou négative (`_c10`).
- **Marge négative** : `_c22` est négatif sur 495 971 lignes (74,3 %). C'est cohérent avec des ventes sous le coût d'achat. Ce n'est pas une erreur de format, mais cela fausse une lecture naïve de la marge et doit être signalé pour la question « quelle est la marge brute par canal et par catégorie ? ».
- **Prix incohérents pour un même produit** : dans un même ticket, un produit peut apparaître avec des coûts et des prix très différents (par exemple ticket 44, produit 10003 : coût d'achat 47,89 contre 85,85 ; prix de vente 53,16 contre 1,60). Il n'existe pas de prix de référence stable par produit dans ces données.
- **Lignes répétées** : 4 038 groupes `(_c9, _c2)` apparaissent plusieurs fois. Elles diffèrent par `_c8`, la quantité et les prix : ce ne sont pas des doublons au sens strict, mais des lignes distinctes à conserver. Avec `_c8` ajouté, il ne reste que 14 lignes en excédent.
- **Valeurs manquantes** : rares sur `store_sales` (`_c4`, `_c5`, `_c6`, `_c8`) et sur `item` (`_c4`, `_c7`, `_c8`), à documenter plutôt qu'à corriger à ce stade.
- **Colonne `_c3` d'`item`** : vide sur 100 % des lignes. Elle n'apporte aucune information et sera écartée ou signalée à l'étape de nettoyage.
- **Qualité du texte** : les descriptions d'`item` n'ont pas de sens, ce qui confirme la limite notée au Jour 1. Ces constats sont cohérents avec un jeu de données généré artificiellement, ce que le formateur peut confirmer.
- **Limites** : le sens des colonnes n'est confirmé par aucune documentation à ce stade.


