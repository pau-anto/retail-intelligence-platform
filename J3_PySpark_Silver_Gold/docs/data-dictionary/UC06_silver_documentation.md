# UC06 - Documentation des jeux Silver 

## 1. Vue d'ensemble

| Jeu Silver | Source brute | Dossier | Lignes | Colonnes | Format | Taille |
| --- | --- | --- | --- | --- | --- | --- |
| `store_sales` | `raw/data/store_sales/store_sales.dat` | `data/silver/store_sales` | 667 579 | 27 | Parquet (snappy) | 64,79 Mo (200 fichiers) |
| `item` | `raw/data/item/item.dat` | `data/silver/item` | 17 820 | 21 | Parquet (snappy) | 3,52 Mo (5 fichiers) |

Les lignes invalides vont dans `data/quarantine/` (`store_sales` : 0 ligne, `item` : 0 ligne). Les données de `raw/` ne sont jamais modifiées.

Seuls les domaines réellement traités sont créés dans Silver : les ventes et les produits.

## 2. Provenance et traitements appliqués

| Étape | `store_sales` | `item` |
| --- | --- | --- |
| Lecture | CSV, séparateur `|`, sans en-tête, types inférés | idem |
| Nettoyage du texte | non concerné (colonnes numériques) | `trim`, puis `N/A`, `Unknown`, `NO_SUB_CAT` et chaînes vides remplacés par `NULL` |
| Colonnes retirées | aucune | `_c3` et `_c19` (100 % vides) |
| Doublons | `dropDuplicates` sur la ligne entière | idem |
| Renommage | 6 colonnes (voir section 3) | 4 colonnes (voir section 4) |
| Enrichissement | `date_vente` (jointure avec `date_dim`), `ligne_id` | aucun |
| Indicateurs ajoutés | `vente_a_perte`, `prix_nul` | `cout_superieur_prix` |
| Contrôle de rattachement | clé de date présente dans `date_dim`, produit présent dans `item` | identifiant non nul |
| Écriture | `mode("overwrite")` en Parquet | idem |

Les règles détaillées, avec leur justification, sont dans `UC06_regles_nettoyage.md`.

## 3. Schéma et colonnes de `silver/store_sales`

Source de la description : spécification TPCx-BB v1.7.0 (annexe B), fournie par le formateur. La correspondance entre `_cN` et les noms TPCx-BB repose sur l'ordre des colonnes, confirmé par les calculs vérifiés (voir dessous).

| Colonne Silver | Type | Colonne TPCx-BB | Description |
| --- | --- | --- | --- |
| `cle_date` | integer | `ss_sold_date_sk` | Clé de la date de vente (vers `date_dim`) |
| `_c1` | integer | `ss_sold_time_sk` | Clé de l'heure de vente |
| `id_produit` | integer | `ss_item_sk` | Produit vendu (vers `item`) |
| `_c3` | integer | `ss_customer_sk` | Client |
| `_c4` | integer | `ss_cdemo_sk` | Démographie du client |
| `_c5` | integer | `ss_hdemo_sk` | Démographie du foyer |
| `_c6` | integer | `ss_addr_sk` | Adresse du client |
| `_c7` | integer | `ss_store_sk` | Magasin |
| `_c8` | integer | `ss_promo_sk` | Promotion |
| `num_ticket` | integer | `ss_ticket_number` | Identifie une vente (ticket) |
| `quantite` | integer | `ss_quantity` | Quantité achetée |
| `_c11` | double | `ss_wholesale_cost` | Coût de gros unitaire |
| `_c12` | double | `ss_list_price` | Prix catalogue unitaire |
| `prix_vente` | double | `ss_sales_price` | Prix de vente unitaire |
| `_c14` | double | `ss_ext_discount_amt` | Remise × quantité |
| `_c15` | double | `ss_ext_sales_price` | Prix de vente × quantité (renommé `montant_vente` dans l'étape Gold) |
| `_c16` | double | `ss_ext_wholesale_cost` | Coût de gros × quantité |
| `_c17` | double | `ss_ext_list_price` | Prix catalogue × quantité |
| `_c18` | double | `ss_ext_tax` | Taxe |
| `_c19` | double | `ss_coupon_amt` | Montant de coupon (surtout 0) |
| `_c20` | double | `ss_net_paid` | Net payé |
| `_c21` | double | `ss_net_paid_inc_tax` | Net payé, taxe comprise |
| `profit` | double | `ss_net_profit` | Net payé − coût de gros × quantité |
| `date_vente` | date | calculée | Date de la vente, via `cle_date` et `date_dim` (2001-01-01 au 2005-12-13) |
| `vente_a_perte` | boolean | calculée | `true` si `profit < 0` (495 971 lignes) |
| `prix_nul` | boolean | calculée | `true` si `prix_vente = 0` (3 324 lignes) |
| `ligne_id` | long | calculée | Identifiant technique unique (`monotonically_increasing_id`) |

Vérifications faites sur les données qui confirment cette correspondance :
- `_c15 = _c10 × _c13` sur toutes les lignes, soit `ss_ext_sales_price = ss_quantity × ss_sales_price` ;
- `_c22 = _c20 − _c16` sur toutes les lignes, soit `ss_net_profit = ss_net_paid − ss_ext_wholesale_cost`.

Aucune clé naturelle stricte n'a été trouvée : `ligne_id` sert de clé technique. 14 lignes restent identiques sur `(_c9, _c2, _c8)`, soit ticket, produit et promotion. Elles sont conservées et signalées comme anomalie connue.

## 4. Schéma et colonnes de `silver/item`

| Colonne Silver | Type | Colonne TPCx-BB | Description |
| --- | --- | --- | --- |
| `id_produit` | integer | `i_item_sk` | Clé unique du produit (0 doublon) |
| `_c1` | string | `i_item_id` | Identifiant produit de 16 caractères |
| `_c2` | date | `i_rec_start_date` | Début de validité de l'enregistrement (2000-01-03 au 2000-12-31) |
| `_c4` | string | `i_item_desc` | Description du produit |
| `prix` | double | `i_current_price` | Prix courant |
| `cout` | double | `i_wholesale_cost` | Coût de gros |
| `_c7` | integer | `i_brand_id` | Identifiant de marque |
| `_c8` | string | `i_brand` | Marque |
| `_c9` | integer | `i_class_id` | Identifiant de classe |
| `_c10` | string | `i_class` | Classe |
| `_c11` | integer | `i_category_id` | Identifiant de catégorie |
| `categorie` | string | `i_category` | Nom de la catégorie (9 catégories) |
| `_c13` | integer | `i_manufact_id` | Identifiant du fabricant |
| `_c14` | string | `i_manufact` | Fabricant |
| `_c15` | string | `i_size` | Taille |
| `_c16` | string | `i_formulation` | Formulation |
| `_c17` | string | `i_color` | Couleur |
| `_c18` | string | `i_units` | Unité |
| `_c20` | integer | `i_manager_id` | Identifiant du responsable |
| `_c21` | string | `i_product_name` | Nom du produit |
| `cout_superieur_prix` | boolean | calculée | `true` si `cout > prix` |

Colonnes retirées : `_c3` (`i_rec_end_date`) et `_c19` (`i_container`), vides à 100 %.

Valeurs manquantes après nettoyage : `_c10` (1 576), `_c15` (2 502), `_c18` (1 767), `_c4` (4), `_c8` (6).

## 5. Convention de nommage

| Élément | Règle | Exemple |
| --- | --- | --- |
| Dossiers | `zone/nom_de_la_source` en minuscules | `silver/store_sales` |
| Colonnes renommées | minuscules, mots séparés par `_`, sans accent | `id_produit`, `date_vente` |
| Indicateurs booléens | préfixe ou nom qui se lit comme une condition | `vente_a_perte`, `prix_nul` |
| Colonnes non identifiées | nom d'origine conservé, `_cN` | `_c11` |
| Colonne technique | `ligne_id` | |
| Format | Parquet, compression snappy, un dossier par jeu | |

Seules 6 colonnes de `store_sales` et 4 d'`item` ont été renommées pendant le nettoyage. Les autres gardent leur nom `_cN` ; leur nom TPCx-BB est indiqué dans les tableaux des sections 3 et 4.

## 6. Contrôles après écriture (4.9.3)

| Contrôle | Résultat | Preuve |
| --- | --- | --- |
| Présence des fichiers | 8 jeux présents (Silver, quarantaine, Gold), `_SUCCESS` partout | `P06_presence_format_taille_parquet.png` |
| Format | Parquet (`.snappy.parquet`) | `P06_presence_format_taille_parquet.png` |
| Lisibilité | Les 8 jeux se relisent avec `spark.read.parquet` | `P07_silver_schema_lignes.png` |
| Nombre de lignes | `store_sales` 667 579, `item` 17 820 | `P07_silver_schema_lignes.png` |
| Schéma | Types conservés (integer, double, date, boolean, long) | `P07_silver_schema_lignes.png` |
| Cohérence avec les résultats attendus | Silver + quarantaine = 667 579 ; 0 vente sans produit ; sommes Gold = Silver (écart 0,0) | `P09_controles_qualite.png`, `P10_coherence_gold_silver.png` |

## 7. Limites

- La correspondance `_cN` / nom TPCx-BB repose sur l'ordre des colonnes. Elle est confirmée par deux calculs et par la cohérence des valeurs, mais la spécification lue ne donne pas elle-même l'ordre complet des colonnes du fichier.
- Beaucoup de colonnes gardent encore un nom `_cN` dans Silver.
- `store_sales` est écrit en 200 petits fichiers (comportement par défaut de Spark en local). Cela ne change pas le contenu.
- Les anomalies (ventes à perte, prix nuls, coût supérieur au prix, 14 lignes proches de doublons) sont conservées et signalées, pas corrigées.
- Aucune table n'est transactionnelle : Parquet seul ne fournit pas de garanties ACID.
