# UC06 - Rapport de qualité des données 

Contrôles exécutés dans `UC06_controles_qualite.ipynb` sur les données **relues depuis les fichiers Parquet** (Silver, quarantaine, Gold), le 2026-11-19. Jeux contrôlés : `silver/store_sales` (667 579 lignes), `silver/item` (17 820 lignes), `quarantine/*` (0 ligne) et les quatre jeux Gold.

## 1. Tableau de contrôle

| Contrôle | Règle | Résultat | Statut | Preuve |
| --- | --- | --- | --- | --- |
| Complétude | `id_produit`, `date_vente`, `quantite`, `prix_vente` non nuls dans `store_sales` | 0 valeur nulle sur chacun | Respectée | `P09_controles_qualite.png` |
| Complétude | `id_produit` non nul dans `item` | 0 valeur nulle | Respectée | `P09_controles_qualite.png` |
| Unicité | `ligne_id` unique dans `store_sales` | 0 doublon | Respectée | `P09_controles_qualite.png` |
| Unicité | `id_produit` unique dans `item` (clé candidate) | 0 doublon (17 820 distincts) | Respectée | `P09_controles_qualite.png` |
| Validité des types | Types attendus conservés après écriture et relecture | integer, double, date, boolean et long retrouvés ; `date_vente` est de type `date` | Respectée | `P07_silver_schema_lignes.png`, `P08_gold_schema_lignes.png` |
| Cohérence | `quantite` strictement positive | 0 ligne avec `quantite` ≤ 0 | Respectée | `P09_controles_qualite.png` |
| Cohérence | `prix_vente` jamais négatif | 0 ligne négative | Respectée | `P09_controles_qualite.png` |
| Cohérence | Dates dans une plage plausible | du 2001-01-01 au 2005-12-13 | Respectée | `P09_controles_qualite.png` |
| Cohérence | Gold = Silver | écart de 0,0 entre la somme de `total_ventes` de chaque Gold et le CA de Silver | Respectée | `P10_coherence_gold_silver.png` |
| Volume | Silver + quarantaine = lignes d'entrée | 667 579 + 0 = 667 579 | Respectée | `P09_controles_qualite.png` |
| Volume | Présence et taille des fichiers | 8 jeux présents, `_SUCCESS` partout | Respectée | `P06_presence_format_taille_parquet.png` |
| Clés candidates | `id_produit` (`item`), `ligne_id` (`store_sales`) | uniques ; aucune clé naturelle stricte dans `store_sales` | Respectée, avec limite (voir section 3) | `P09_controles_qualite.png` |
| Intégrité référentielle | Chaque vente a un produit dans `item` | 0 vente sans produit | Respectée | `P09_controles_qualite.png` |
| Intégrité référentielle | Chaque clé de date existe dans `date_dim` | 0 clé absente (contrôlé lors du nettoyage, 667 579 lignes avant et après la jointure) | Respectée | `P05_nettoyage.png` (volumes) et `UC06_regles_nettoyage.md` |

## 2. Règles respectées

Toutes les règles du tableau sont respectées : aucune valeur manquante sur les champs requis, aucun doublon sur les clés, types conservés à la relecture, quantités et prix valides, aucune vente sans produit, aucun écart entre Gold et Silver, aucune ligne perdue entre l'entrée et la sortie.

## 3. Anomalies restantes

Ces anomalies sont conservées volontairement et signalées par des indicateurs, car les exclure fausserait le chiffre d'affaires (règle documentée dans `UC06_regles_nettoyage.md`).

| Anomalie | Volume | Traitement |
| --- | --- | --- |
| Ventes à perte (`vente_a_perte`, profit négatif) | 495 971 lignes (74,3 %) | Conservées, signalées. Cohérent avec la définition du profit (coût de gros × quantité supérieur au prix de vente), à discuter avec le formateur |
| Prix de vente nul (`prix_nul`) | 3 324 lignes (0,50 %) | Conservées, signalées |
| Coût supérieur au prix (`cout_superieur_prix`, `item`) | 7 768 produits (43,6 %) | Conservés, signalés |
| Lignes quasi identiques sur ticket, produit et promotion | 14 lignes en excédent | Conservées : elles sont distinctes sur la ligne entière, `ligne_id` les identifie. Non inspectées une à une |
| Valeurs manquantes optionnelles `store_sales` | `_c4` (238), `_c5` (295), `_c6` (448), `_c8` (158) | Conservées avec `NULL` |
| Valeurs manquantes `item` | `_c4` (4), `_c7` (8), `_c8` (6), `_c10` (1 576), `_c15` (2 502), `_c18` (1 767) | Conservées avec `NULL` après remplacement des valeurs de remplissage |
| Quatre produits au CA exceptionnel (10000 à 10003) | 14,2 à 17,1 millions chacun | Conservés, à confirmer avec le formateur |
| Année 2005 incomplète | ventes jusqu'au 2005-12-13 | Documenté |

## 4. Données mises à l'écart

| Zone | Lignes | Observation |
| --- | --- | --- |
| `quarantine/store_sales` | 0 | Aucune ligne invalide détectée par les règles |
| `quarantine/item` | 0 | Aucune ligne invalide détectée |
| Colonnes retirées de `item` | `_c3` (`i_rec_end_date`), `_c19` (`i_container`) | Vides à 100 %, conservées dans `raw/` |

Le schéma du dossier `quarantine/item` contient encore la colonne `_c19`, car il a été écrit avant son retrait des données Silver. Il ne contient aucune ligne, donc sans conséquence.

## 5. Limites des contrôles

- Les contrôles portent sur les deux tables traitées (`store_sales` et `item`) et sur les Gold. Les autres tables (`customer`, `store`, `promotion`, etc.) ne sont pas contrôlées.
- L'intégrité référentielle est vérifiée pour le produit et la date seulement. Magasin, client et promotion ne sont pas vérifiés, faute de table de référence chargée.
- Les contrôles de plage sont des repères : aucun seuil fixe n'est codé, par exemple sur la date.
- Les 14 lignes quasi identiques n'ont pas été examinées ligne par ligne.
- Le sens des colonnes repose sur la spécification TPCx-BB et sur l'ordre standard des colonnes, confirmé par deux calculs. Les montants n'ont pas été comparés à une source indépendante.
- Les contrôles de complétude et d'unicité sont faits sur Silver, pas rejoués sur chaque Gold. Les Gold sont contrôlés par la somme et le nombre de lignes.

## 6. Corrections éventuelles

| Correction possible | Intérêt | Statut |
| --- | --- | --- |
| Inspecter les 14 lignes quasi identiques et décider de les garder ou non | Lever le doute sur d'éventuels doublons | À faire si le temps le permet |
| Confirmer avec le formateur le profit négatif et les produits 10000 à 10003 | Interprétation des résultats | À discuter |
| Renommer les colonnes `_cN` restantes selon la spécification TPCx-BB | Lisibilité de Silver | Facultatif, demande de relancer le traitement |
| Réécrire `quarantine/item` pour retirer `_c19` de son schéma | Cohérence des schémas | Facultatif |
| Écrire `store_sales` Silver en moins de fichiers (`coalesce`) | Lecture plus simple | Facultatif |

## 7. Conclusion

Les jeux Silver et Gold sont exploitables pour une analyse descriptive du chiffre d'affaires : aucune ligne perdue, aucun écart entre Gold et Silver, aucune vente sans produit. Les anomalies restantes sont connues, quantifiées et signalées : elles concernent surtout la marge (profit négatif sur 74,3 % des lignes) et ne remettent pas en cause le calcul du chiffre d'affaires.
