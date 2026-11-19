## UC06 - 4.6.3 Questions techniques

Le sens des colonnes vient de la spécification TPCx-BB v1.7.0, fournie par le formateur. La correspondance `_cN` / nom TPCx-BB repose sur l'ordre des colonnes, confirmé par deux calculs vérifiés : `_c15 = _c10 × _c13` et `_c22 = _c20 − _c16`. Le détail est dans `silver_documentation.md`.

### 1. Quelles colonnes sont numériques ?

- **store_sales** : les 23 colonnes. Entiers `_c0` à `_c10`, décimaux `_c11` à `_c22`.
- **item** : 8 colonnes sur 22. Entiers `_c0`, `_c7`, `_c9`, `_c11`, `_c13`, `_c20` ; décimaux `_c5`, `_c6`. Les 14 autres sont du texte (13) ou une date (1).

### 2. Quelles colonnes représentent des dates ?

- **item** : `_c2` (`i_rec_start_date`, début de validité de l'enregistrement) est la seule colonne typée `date` (par exemple 2000-01-14).
- **store_sales** : aucune colonne n'est typée date. `_c0` (36 890 à 38 697) et `_c1` (0 à 86 399) sont des entiers. Selon la spécification, `_c0` est `ss_sold_date_sk` (clé vers `date_dim`, jointure vérifiée) et `_c1` est `ss_sold_time_sk` (heure en secondes : 86 399 = 23 h 59 min 59 s).

### 3. Quelles colonnes sont des identifiants ?

| Table | Colonne | Rôle (TPCx-BB) | Indice observé |
| --- | --- | --- | --- |
| store_sales | `_c2` | Produit (`ss_item_sk`) | 0 à 17 819 : correspond à `item._c0`, jointure validée |
| store_sales | `_c9` | Numéro de ticket (`ss_ticket_number`) | 0 à 89 099 : 89 100 valeurs distinctes |
| store_sales | `_c7` | Magasin (`ss_store_sk`) | 0 à 11 : 12 valeurs, comme les 12 magasins du Jour 1 |
| store_sales | `_c8` | Promotion (`ss_promo_sk`) | 0 à 299 |
| store_sales | `_c3`, `_c4`, `_c5`, `_c6` | Client (`ss_customer_sk`), démographie du client (`ss_cdemo_sk`), démographie du foyer (`ss_hdemo_sk`), adresse (`ss_addr_sk`) | Plages larges, avec des valeurs manquantes sur `_c4`, `_c5`, `_c6` |
| item | `_c0` | Identifiant produit (`i_item_sk`) | 0 à 17 819, unique |
| item | `_c1` | Code produit (`i_item_id`, 16 caractères) | `AAAAAAAAAAAAAAAA`, `...B`, unique |

Les autres colonnes numériques de `store_sales` sont des mesures : quantité `_c10` (`ss_quantity`, 1 à 100, comme indiqué par la spécification) et montants `_c11` à `_c22` : coût de gros, prix catalogue, prix de vente, remise, prix de vente × quantité, coût de gros × quantité, prix catalogue × quantité, taxe, coupon, net payé, net payé taxe comprise et profit net (voir `silver_documentation.md`).

### 4. Quels champs présentent des valeurs manquantes ?

| Table | Colonne | Valeurs manquantes |
| --- | --- | --- |
| store_sales | `_c4` (`ss_cdemo_sk`) | 238 |
| store_sales | `_c5` (`ss_hdemo_sk`) | 295 |
| store_sales | `_c6` (`ss_addr_sk`) | 448 |
| store_sales | `_c8` (`ss_promo_sk`) | 158 |
| item | `_c3` (`i_rec_end_date`) | 17 820 (colonne entièrement vide) |
| item | `_c4` (`i_item_desc`) | 4 |
| item | `_c7` (`i_brand_id`) | 8 |
| item | `_c8` (`i_brand`) | 6 |

Toutes les autres colonnes n'ont aucune valeur manquante avant nettoyage. Après la règle sur les valeurs de remplissage (`N/A`, `Unknown`, `NO_SUB_CAT`), d'autres colonnes texte d'`item` en contiennent : `_c10` (`i_class`, 1 576), `_c15` (`i_size`, 2 502), `_c18` (`i_units`, 1 767) et `_c19` (`i_container`, 17 820, colonne retirée).

### 5. Existe-t-il des doublons ?

- Aucune ligne entièrement identique, ni dans `store_sales` ni dans `item` (0 et 0).
- Sur la clé `(_c9, _c2)` de `store_sales`, un même produit apparaît plusieurs fois dans un ticket. Ces lignes diffèrent par la quantité, la promotion et les prix : ce ne sont pas de vrais doublons.
- Dans `item`, `_c0` et `_c1` sont uniques.

### 6. Certaines valeurs sont-elles incohérentes ?

- **`_c22` (store_sales, `ss_net_profit`)** : minimum −9 866,6, maximum 9 134,0, moyenne −827,7. La moyenne négative et 74,3 % de lignes négatives indiquent des ventes sous le coût d'achat. La spécification définit ce profit comme le net payé moins le coût de gros × quantité : le résultat est donc cohérent avec sa définition.
- **Prix et montants à 0** : `_c13` (`ss_sales_price`), `_c15` (`ss_ext_sales_price`) et `_c20` (`ss_net_paid`) ont un minimum à 0,0 alors que la quantité vaut au moins 1.
- **item `_c3` (`i_rec_end_date`)** : colonne vide à 100 %.
- **item, valeurs de remplissage** : `N/A`, `Unknown`, `NO_SUB_CAT` dans l'échantillon.
- **item `_c4` (`i_item_desc`)** : descriptions qui semblent tronquées (mots coupés en fin de texte).
- **item `_c8`, `_c14`, `_c21`** (`i_brand`, `i_manufact`, `i_product_name`) : textes aléatoires sans signification, ce qui est cohérent avec des données générées.
