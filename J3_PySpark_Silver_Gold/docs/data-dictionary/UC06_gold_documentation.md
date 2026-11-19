# UC06 - Documentation des jeux Gold

## 1. Vue d'ensemble

| Jeu Gold | Question métier (Jour 1) | Granularité | Lignes | Dossier |
| --- | --- | --- | --- | --- |
| `ca_par_categorie` | Quels produits génèrent le plus de ventes ? (par catégorie) | Une ligne par catégorie | 9 | `data/gold/ca_par_categorie` |
| `ca_par_produit` | Quels produits génèrent le plus de ventes ? (par article) | Une ligne par produit | 17 820 | `data/gold/ca_par_produit` |
| `ca_par_mois` | Comment évoluent les ventes dans le temps ? | Une ligne par année et mois | 60 | `data/gold/ca_par_mois` |
| `ca_par_annee` | Comment évolue le CA d'une année à l'autre ? | Une ligne par année | 5 | `data/gold/ca_par_annee` |

Tous les jeux sont écrits au format Parquet (voir `P06_presence_format_taille_parquet.png`), relus avec succès (voir `P08_gold_schema_lignes.png`) et cohérents avec Silver (voir `P10_coherence_gold_silver.png`).

## 2. Définition fonctionnelle commune

| Élément | Description |
| --- | --- |
| Objectif | Suivre le chiffre d'affaires des ventes en magasin par catégorie, produit et période |
| Sources | Jeux Silver vérifiés : `silver/store_sales` (667 579 lignes) et `silver/item` (17 820 lignes) |
| Préparation | Ajout de `categorie` aux ventes par jointure sur `id_produit` (N:1, 667 579 lignes avant et après), ajout de `annee` et `mois` à partir de `date_vente`, renommage de `_c15` en `montant_vente` |
| Mesure principale | `total_ventes` = somme de `montant_vente` |
| Dimensions | catégorie, produit, année, mois |
| Usage | Analyse descriptive et restitution |
| Période couverte | 2001-01-01 au 2005-12-13 |

Règle de calcul du montant : `montant_vente` correspond à `ss_ext_sales_price` dans la spécification TPCx-BB, soit `quantite × prix_vente`, avant coupons et taxes (vérifié sur les 667 579 lignes). Aucune ligne de Silver n'est exclue du calcul : les ventes à perte, les prix nuls et les 14 lignes proches de doublons sont incluses.

## 3. Description de chaque jeu

### 3.1 `ca_par_categorie`

| Colonne | Type | Description | Règle de calcul |
| --- | --- | --- | --- |
| `categorie` | string | Catégorie du produit (`i_category`) | Dimension, issue d'`item` |
| `total_ventes` | double | Chiffre d'affaires de la catégorie | Somme de `montant_vente` |
| `quantite_totale` | long | Quantité vendue | Somme de `quantite` |
| `nombre_lignes` | long | Nombre de lignes de vente | Comptage des lignes |

Finalité : identifier les catégories qui pèsent le plus dans le chiffre d'affaires. Music (45,2 %) et Books (26,7 %) représentent 71,9 % du total.

### 3.2 `ca_par_produit`

| Colonne | Type | Description | Règle de calcul |
| --- | --- | --- | --- |
| `id_produit` | integer | Identifiant du produit (`i_item_sk`) | Dimension |
| `categorie` | string | Catégorie du produit | Dimension, issue d'`item` |
| `total_ventes` | double | Chiffre d'affaires du produit | Somme de `montant_vente` |
| `quantite_totale` | long | Quantité vendue | Somme de `quantite` |

Finalité : classer les produits par chiffre d'affaires. Les 17 820 produits d'`item` ont au moins une vente. Quatre produits (10000 à 10003) se détachent avec 14,2 à 17,1 millions chacun, contre 3,7 millions pour le cinquième.

### 3.3 `ca_par_mois`

| Colonne | Type | Description | Règle de calcul |
| --- | --- | --- | --- |
| `annee` | integer | Année de la vente | Extraite de `date_vente` |
| `mois` | integer | Mois de la vente (1 à 12) | Extrait de `date_vente` |
| `total_ventes` | double | Chiffre d'affaires du mois | Somme de `montant_vente` |
| `quantite_totale` | long | Quantité vendue | Somme de `quantite` |

Finalité : suivre l'évolution des ventes dans le temps. Sur 2001, le CA mensuel reste entre 19,96 et 22,36 millions, sans saisonnalité marquée. 60 lignes couvrent 5 années de 12 mois ; le mois de décembre 2005 est incomplet.

### 3.4 `ca_par_annee`

| Colonne | Type | Description | Règle de calcul |
| --- | --- | --- | --- |
| `annee` | integer | Année de la vente | Extraite de `date_vente` |
| `total_ventes` | double | Chiffre d'affaires de l'année | Somme de `montant_vente` |

Finalité : comparer les années. Le CA est stable de 2001 à 2004 (257,0 à 260,0 millions). 2005 (243,0 millions) est incomplète : les ventes s'arrêtent au 13 décembre.

## 4. Contrôles de cohérence

| Contrôle | Résultat |
| --- | --- |
| CA total des ventes (Silver) | 1 277 224 004,61 |
| Somme de `total_ventes` par jeu Gold − CA total | Écart de 0,0 pour les quatre jeux |
| Lignes agrégées dans `ca_par_categorie` | 667 579 (toutes les lignes de vente) |
| Relecture de `gold/ca_par_annee` | 5 lignes, schéma conservé |

## 5. Limites d'interprétation

- Le montant est calculé avant coupons et taxes. Il n'est pas le montant réellement payé (`ss_net_paid`, `_c20`).
- Seules les ventes en magasin sont analysées. Les ventes web et les retours ne sont pas inclus.
- Aucune marge ni aucun profit n'est agrégé. Le profit (`ss_net_profit`) est négatif sur 74,3 % des lignes : il doit être discuté avec le formateur avant d'être interprété.
- 2005 est incomplète (jusqu'au 13 décembre) : ne pas la comparer directement aux autres années.
- Les quatre produits au CA exceptionnel (10000 à 10003) sont probablement liés à la génération des données. Hypothèse non confirmée.
- La spécification ne précise pas l'unité monétaire.
- Les jeux sont des fichiers Parquet, sans garanties transactionnelles (pas de format de table Lakehouse).
- La granularité est celle des ventes en magasin : pas de dimension magasin, client ou promotion dans ces agrégats, alors que les colonnes existent dans Silver (`_c7`, `_c3`, `_c8`).
