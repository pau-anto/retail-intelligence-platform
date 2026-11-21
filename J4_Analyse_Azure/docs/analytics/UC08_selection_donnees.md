# UC-08 – Sélection et caractérisation des données 

Cette étape décrit les jeux Silver et Gold choisis pour l'analyse. Tout ce qui est écrit ici a été **relevé en lisant les fichiers Parquet du TP3** (relevé du 2026-11-20).

Les données sont **synthétiques** (jeu TPCx-BB) : les chiffres servent à apprendre la démarche, ils ne décrivent pas une vraie entreprise.

## 1. Jeux sélectionnés

| # | Jeu (nom exact) | Zone | Lignes | Colonnes | Pourquoi retenu |
| --- | --- | --- | --- | --- | --- |
| 1 | `silver/store_sales` | Silver | 667 579 | 27 | Ventes au grain le plus fin (ligne, ticket, magasin) |
| 2 | `silver/item` | Silver | 17 820 | 21 | Référentiel produits et catégories |
| 3 | `gold/ca_par_mois` | Gold | 60 | 4 | Évolution des ventes dans le temps |
| 4 | `gold/ca_par_categorie` | Gold | 9 | 4 | Contribution des catégories au CA |

Deux autres jeux Gold existent et sont **disponibles mais non retenus** pour l'instant : `gold/ca_par_annee` (5 lignes, 2 colonnes : `annee`, `total_ventes`), utilisé pour contrôler la cohérence, et `gold/ca_par_produit` (17 820 lignes, 4 colonnes : `id_produit`, `categorie`, `total_ventes`, `quantite_totale`), utilisable pour un classement de produits.

---

## 2. Fiche 1 – `silver/store_sales`

| Point | Contenu |
| --- | --- |
| **1. Nom exact** | `silver/store_sales` : dossier contenant 200 fichiers `part-xxxxx-….snappy.parquet` et un fichier `_SUCCESS` |
| **2. Provenance** | Table `store_sales` du jeu TPCx-BB, fichier `store_sales.dat` (92 764 700 octets, séparateur `\|`, sans en-tête). Déposé sur HDFS au Jour 2 (SHA-256 contrôlé après dépôt manuel et par NiFi), puis lu au Jour 3 depuis le système de fichiers local et nettoyé par `UC06_script_traitement.ipynb` : renommage de colonnes, jointure avec `date_dim` pour calculer `date_vente`, ajout de `vente_a_perte`, `prix_nul` et `ligne_id`. Mise à l'écart des lignes invalides dans `quarantine/` (vide) |
| **3. Format** | Parquet, compression Snappy, 67,41 Mo au total (relevé) |
| **4. Schéma** | 27 colonnes, détail ci-dessous |
| **5. Granularité** | **Une ligne = un article d'un ticket de caisse** (une ligne de vente). 667 579 lignes pour **89 100 tickets** distincts (`num_ticket`), soit environ 7,5 lignes par ticket. 12 magasins (`_c7`, valeurs 0 à 11), 17 820 produits vendus, du 2001-01-01 au 2005-12-13 |
| **6. Contrôles qualité disponibles** | Voir tableau ci-dessous |
| **7. Pourquoi adapté** | C'est le seul jeu qui garde le ticket, le magasin, le produit, la date et le montant au grain le plus fin. Il permet de calculer le CA, le nombre de tickets et le panier moyen, de ventiler par magasin (ce que les Gold ne permettent pas) et de recontrôler les agrégats Gold. Il est propre : aucune ligne invalide, aucun produit orphelin, montants vérifiés |

### Schéma de `silver/store_sales` (sortie de `printSchema()`)

| Colonne | Type Spark | Sens (spécification TPCx-BB) | Statut du sens |
| --- | --- | --- | --- |
| `cle_date` | integer | `ss_sold_date_sk` : clé de la date | Nom du TP3 |
| `_c1` | integer | `ss_sold_time_sk` : heure de vente | Déduit de l'ordre des colonnes |
| `id_produit` | integer | `ss_item_sk` : produit | Nom du TP3 |
| `_c3` | integer | `ss_customer_sk` : client | Déduit |
| `_c4` | integer | `ss_cdemo_sk` : démographie client | Déduit |
| `_c5` | integer | `ss_hdemo_sk` : démographie foyer | Déduit |
| `_c6` | integer | `ss_addr_sk` : adresse | Déduit |
| `_c7` | integer | `ss_store_sk` : **magasin** | Déduit |
| `_c8` | integer | `ss_promo_sk` : promotion | Déduit |
| `num_ticket` | integer | `ss_ticket_number` : numéro de ticket | Nom du TP3 |
| `quantite` | integer | `ss_quantity` | Nom du TP3 |
| `_c11` | double | `ss_wholesale_cost` : coût de gros unitaire | Déduit |
| `_c12` | double | `ss_list_price` : prix catalogue unitaire | Déduit |
| `prix_vente` | double | `ss_sales_price` : prix de vente unitaire | Nom du TP3 |
| `_c14` | double | `ss_ext_discount_amt` : remise × quantité | Déduit |
| `_c15` | double | `ss_ext_sales_price` : **montant de la ligne** (= quantité × prix de vente) | Déduit, **vérifié** |
| `_c16` | double | `ss_ext_wholesale_cost` : coût de gros × quantité | Déduit |
| `_c17` | double | `ss_ext_list_price` | Déduit |
| `_c18` | double | `ss_ext_tax` : taxe | Déduit |
| `_c19` | double | `ss_coupon_amt` : coupon | Déduit |
| `_c20` | double | `ss_net_paid` : net payé | Déduit |
| `_c21` | double | `ss_net_paid_inc_tax` : net payé, taxe comprise | Déduit |
| `profit` | double | `ss_net_profit` | Nom du TP3, **vérifié** |
| `date_vente` | date | Calculée : date de la vente (via `date_dim`) | Créée au TP3 |
| `vente_a_perte` | boolean | Calculée : `profit < 0` | Créée au TP3 |
| `prix_nul` | boolean | Calculée : `prix_vente = 0` | Créée au TP3 |
| `ligne_id` | long | Calculée : identifiant technique unique | Créée au TP3 |

### Contrôles qualité (rappel du TP3, recontrôlés sur les fichiers fournis)

| Contrôle | Résultat relevé |
| --- | --- |
| Silver + quarantaine = entrée | 667 579 lignes, quarantaine vide (TP3) |
| `ligne_id` unique | Oui (667 579 valeurs distinctes) |
| Ventes sans produit dans `item` | 0 |
| `_c15 = quantite × prix_vente` (écart > 0,01) | 0 ligne |
| `profit = _c20 − _c16` (écart > 0,01) | 0 ligne |
| Quantité ≤ 0 ou prix de vente < 0 | 0 ligne (quantité de 1 à 100, prix de 0,00 à 199,30) |
| `_c7` (magasin) nul | 0 ; 12 valeurs distinctes |
| Dates | 2001-01-01 à 2005-12-13 ; décembre 2005 : 13 jours |
| Anomalie connue : lignes à perte (`vente_a_perte`) | 495 971 lignes, soit 74,29 % |
| Anomalie connue : prix de vente nul (`prix_nul`) | 3 324 lignes |
| Anomalie connue : doublons sur (ticket, produit, `_c8`) | 14 lignes en trop (28 lignes concernées), conservées |
| **Valeurs manquantes** | `_c4` : 238, `_c5` : 295, `_c6` : 448, `_c8` : 158 (aucune sur les autres colonnes) |

---

## 3. Fiche 2 – `silver/item`

| Point | Contenu |
| --- | --- |
| **1. Nom exact** | `silver/item` : 5 fichiers `.snappy.parquet` et `_SUCCESS` |
| **2. Provenance** | Table `item` du jeu TPCx-BB (`item.dat`, séparateur `\|`, sans en-tête), nettoyée au Jour 3 par `UC06_script_traitement.ipynb` : renommage de `id_produit`, `prix`, `cout`, `categorie`, conversion de types, ajout de `cout_superieur_prix` |
| **3. Format** | Parquet, Snappy, 3,66 Mo |
| **4. Schéma** | 21 colonnes, voir ci-dessous |
| **5. Granularité** | **Une ligne = un produit.** 17 820 lignes, `id_produit` unique (17 820 valeurs distinctes) |
| **6. Contrôles qualité** | `id_produit` unique ; 9 catégories ; chaque produit a au moins une vente (0 produit sans vente) ; 0 vente sans produit ; valeurs manquantes listées ci-dessous ; `cout_superieur_prix` vrai pour 7 768 produits (indicateur conservé, non corrigé) |
| **7. Pourquoi adapté** | Apporte la dimension « catégorie » aux ventes par une jointure N:1 sûre (clé unique, aucune ligne dupliquée) : sans lui, aucune analyse par catégorie n'est possible |

Schéma :

| Colonne | Type | Remarque |
| --- | --- | --- |
| `id_produit` | integer | Clé du produit |
| `_c1` | string | Non identifiée (code produit probable) |
| `_c2` | date | Date, sens non confirmé |
| `_c4` | string | Texte descriptif probable ; 4 valeurs manquantes |
| `prix` | double | Prix du produit |
| `cout` | double | Coût du produit |
| `_c7` | integer | Non identifiée ; 8 valeurs manquantes |
| `_c8` | string | Non identifiée ; 6 valeurs manquantes |
| `_c9` | integer | Non identifiée |
| `_c10` | string | Non identifiée ; 1 576 valeurs manquantes |
| `_c11` | integer | Non identifiée |
| `categorie` | string | **Catégorie** (9 valeurs) |
| `_c13` | integer | Non identifiée |
| `_c14` | string | Non identifiée |
| `_c15` | string | Non identifiée ; 2 502 valeurs manquantes |
| `_c16`, `_c17` | string | Non identifiées |
| `_c18` | string | Non identifiée ; 1 767 valeurs manquantes |
| `_c20` | integer | Non identifiée |
| `_c21` | string | Non identifiée |
| `cout_superieur_prix` | boolean | Calculée : `cout > prix` |

Les colonnes `_c3` et `_c19` n'existent pas dans ce Silver (colonnes retirées lors du nettoyage au TP3 ; motif à retrouver dans `silver_documentation.md` du TP3). 

---

## 4. Fiche 3 – `gold/ca_par_mois`

| Point | Contenu |
| --- | --- |
| **1. Nom exact** | `gold/ca_par_mois` : 1 fichier `.snappy.parquet` et `_SUCCESS` |
| **2. Provenance** | Calculé depuis `silver/store_sales` par `UC06_script_transformation.ipynb` : année et mois extraits de `date_vente`, puis somme du montant (`_c15`, renommé `montant_vente` dans ce notebook) et de la quantité |
| **3. Format** | Parquet, Snappy |
| **4. Schéma** | `annee` integer, `mois` integer, `total_ventes` double, `quantite_totale` long |
| **5. Granularité** | **Une ligne = un mois d'une année.** 60 lignes (5 ans × 12 mois), la clé (`annee`, `mois`) est unique, aucune valeur manquante |
| **6. Contrôles qualité** | Somme de `total_ventes` = CA Silver (1 277 224 004,61), écart 0,0 ; somme de `quantite_totale` = 33 755 474 = quantité Silver ; 60 mois distincts. Réserve : décembre 2005 ne couvre que 13 jours (jusqu'au 13/12/2005) |
| **7. Pourquoi adapté** | Répond directement à « comment évoluent les ventes dans le temps ? » (Jour 1), déjà agrégé et recoupé avec Silver |

## 5. Fiche 4 – `gold/ca_par_categorie`

| Point | Contenu |
| --- | --- |
| **1. Nom exact** | `gold/ca_par_categorie` : 1 fichier `.snappy.parquet` et `_SUCCESS` |
| **2. Provenance** | Calculé par `UC06_script_transformation.ipynb` : jointure `silver/store_sales` et `silver/item` sur `id_produit` (667 579 lignes avant et après, 0 vente sans catégorie), puis somme par catégorie |
| **3. Format** | Parquet, Snappy |
| **4. Schéma** | `categorie` string, `total_ventes` double, `quantite_totale` long, `nombre_lignes` long |
| **5. Granularité** | **Une ligne = une catégorie de produit.** 9 lignes, `categorie` unique, aucune valeur manquante |
| **6. Contrôles qualité** | Somme de `total_ventes` = CA Silver (écart 0,0) ; somme de `nombre_lignes` = 667 579, donc toutes les ventes sont agrégées |
| **7. Pourquoi adapté** | Répond à « quels produits génèrent le plus de ventes ? » au niveau catégorie. Valeurs relevées : Music 577,3 M (45,2 %), Books 340,5 M (26,7 %), Movies & TV 83,0 M (6,5 %), puis six catégories entre 2,3 % et 4,9 % |

---

## 6. Vérification préalable obligatoire (§6.3 du sujet)

| Vérification | Résultat |
| --- | --- |
| 1. Nom exact | Dossiers `silver/store_sales`, `silver/item`, `gold/ca_par_mois`, `gold/ca_par_categorie` (relevés dans l'archive) |
| 2. Provenance | TPCx-BB → HDFS (J2) → Silver (J3, `UC06_script_traitement`) → Gold (J3, `UC06_script_transformation`) |
| 3. Format réel | Parquet Snappy pour les quatre jeux |
| 4. Colonnes | 27, 21, 4 et 4 colonnes ; schémas ci-dessus |
| 5. Types | Types Spark relevés par `printSchema()` ; les `_cN` gardent leur type d'origine |
| 6. Granularité | Ligne de vente, produit, mois, catégorie |
| 7. Clés et relations | `ligne_id` (clé technique) unique ; `id_produit` unique dans `item` ; `store_sales.id_produit → item.id_produit` N:1 vérifiée (0 orphelin) ; `store_sales.cle_date → date_dim` utilisée au TP3 (non rejouée ici, `date_dim` n'est pas dans l'archive). Pas de clé naturelle stricte dans `store_sales` |
| 8. Valeurs manquantes et anomalies | Voir fiches : 4 colonnes de `store_sales`, 6 colonnes de `item`, aucune dans les Gold. Anomalies : 74,29 % de lignes à perte, 3 324 prix nuls, 14 doublons, 7 768 produits avec coût > prix |
| 9. Règles de transformation | Voir « provenance » des fiches et `UC06_regles_nettoyage.md`, `UC06_transformations.md` du TP3. Le montant analysé est `_c15` (avant coupons et taxes) |

### Limites constatées

- **Pas de jeu Gold par magasin** : l'analyse par magasin devra partir de Silver (`_c7`). Pour construire ce Gold, il faudrait agréger `silver/store_sales` par `_c7` (CA, tickets distincts, quantité).
- **Pas de Gold pour les paniers** : le nombre de tickets et le panier moyen se calculent aussi depuis Silver.
- **Ventes web, retours et stocks absents** : les tables `web_sales`, `store_returns`, etc. n'ont pas été traitées en Silver. Les KPI de retour et de canal ne peuvent pas être calculés.

## 7. Observations, hypothèses, recommandations

| Type | Contenu |
| --- | --- |
| **Observé** | 667 579 lignes pour 89 100 tickets ; 12 valeurs de `_c7` ; Gold cohérent avec Silver (écart 0,0) ; 74,29 % de lignes à perte ; valeurs manquantes sur `_c4`, `_c5`, `_c6`, `_c8` |
| **Hypothèse** | `_c7` est le magasin, `_c15` le montant de la ligne, `_c20` le net payé, `_c8` la promotion : déduit de l'ordre TPCx-BB. `_c15` et `profit` sont confirmés par un calcul (0 écart) ; `_c7`, `_c20` et `_c8` ne le sont pas. Les valeurs manquantes de `_c8` correspondent probablement à des ventes sans promotion (non vérifié) |
| **Recommandation** | Rappeler cette hypothèse dans toute analyse par magasin ; ne pas présenter de marge sans réserve (74 % de lignes à perte) ; comparer les années complètes (2001 à 2004) et traiter 2005 à part |
