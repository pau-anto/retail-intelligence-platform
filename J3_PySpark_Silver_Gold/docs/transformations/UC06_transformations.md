# UC06 - 4.8 Transformations

Notebook : `UC06_script_transformation.ipynb`. Entrées : données Silver (`data/silver/store_sales`, `data/silver/item`). Sorties : jeux de données Gold (`data/gold/`). Date d'exécution : 2026-11-19.

## 1. Transformations réalisées

| Opération | Détail | Résultat |
| --- | --- | --- |
| Renommage | `_c15` (`ss_ext_sales_price`) renommée `montant_vente` | Colonne lisible |
| Colonnes calculées | `annee` et `mois`, extraits de `date_vente` (date issue de `date_dim`) | Exemple : 2001-01-01 donne `annee` = 2001 et `mois` = 1 |
| Jointure ventes et produits | Ajout de `categorie` aux ventes | 667 579 lignes avant et après, 0 vente sans catégorie |
| Agrégations | CA par catégorie, par produit, par mois et par année | Quatre jeux Gold |

Règle de calcul du montant : `montant_vente` correspond à `ss_ext_sales_price` dans la spécification TPCx-BB : le prix de vente multiplié par la quantité (`quantite × prix_vente`), avant coupons et taxes. Cette égalité a été vérifiée sur les 667 579 lignes lors de l'exploration (0 écart). Les coupons (`ss_coupon_amt`) et le net payé (`ss_net_paid`) sont des colonnes distinctes, non utilisées ici. La spécification ne précise pas l'unité monétaire.

## 2. Jointures

| Jointure | Sources | Colonnes utilisées | Nature de la relation | Cardinalité attendue | Lignes avant / après | Non rapprochés |
| --- | --- | --- | --- | --- | --- | --- |
| Ventes et produits | `store_sales` (Silver) et `item` (Silver) | `id_produit` | Plusieurs lignes de vente pour un produit | N:1 | 667 579 / 667 579 | 0 vente sans catégorie |
| Ventes et dates | `store_sales` et `date_dim` | `cle_date` = `date_dim._c0` | Plusieurs lignes de vente pour une date | N:1 | 667 579 / 667 579 | 0 clé absente de `date_dim` |

La jointure ventes et dates a été réalisée à l'étape de nettoyage (`UC06_script_traitement.ipynb`), pour obtenir la colonne `date_vente`.

Les deux jointures sont de type `left` : elles conservent toutes les lignes de vente. La relation a été vérifiée avant la jointure : `item.id_produit` est unique (17 820 valeurs distinctes sur 17 820 lignes), donc une vente ne peut correspondre qu'à un seul produit et le nombre de lignes ne peut pas augmenter. Le contrôle le confirme : 667 579 lignes avant et après.

## 3. Agrégations

| Agrégation | Question du Jour 1 | Granularité | Règle de calcul |
| --- | --- | --- | --- |
| `ca_par_categorie` | Quels produits génèrent le plus de ventes ? (par catégorie) | Une ligne par catégorie (9 lignes) | `total_ventes` = somme de `montant_vente` ; `quantite_totale` = somme de `quantite` ; `nombre_lignes` = nombre de lignes de vente |
| `ca_par_produit` | Quels produits génèrent le plus de ventes ? (par article) | Une ligne par produit et sa catégorie | `total_ventes` = somme de `montant_vente` ; `quantite_totale` = somme de `quantite` |
| `ca_par_mois` | Comment évoluent les ventes dans le temps ? | Une ligne par année et mois | `total_ventes` = somme de `montant_vente` ; `quantite_totale` = somme de `quantite` |
| `ca_par_annee` | Comment évolue le CA d'une année à l'autre ? | Une ligne par année (5 lignes) | `total_ventes` = somme de `montant_vente` par `annee` |

## 4. Résultats

### CA par catégorie

| Catégorie | Total des ventes | Part du CA | Quantité vendue | Lignes de vente |
| --- | --- | --- | --- | --- |
| Music | 577 349 769 | 45,2 % | 15 238 374 | 301 236 |
| Books | 340 528 435 | 26,7 % | 9 007 511 | 177 671 |
| Movies & TV | 83 022 698 | 6,5 % | 2 189 279 | 43 376 |
| Clothing & Accessories | 62 856 360 | 4,9 % | 1 640 550 | 32 372 |
| Electronics | 61 668 912 | 4,8 % | 1 632 098 | 32 619 |
| Home & Kitchen | 45 896 148 | 3,6 % | 1 226 839 | 24 380 |
| Sports & Outdoors | 45 610 701 | 3,6 % | 1 209 305 | 23 911 |
| Toys & Games | 30 467 445 | 2,4 % | 809 999 | 16 121 |
| Tools & Home Improvement | 29 823 537 | 2,3 % | 801 519 | 15 893 |
| **Total** | **1 277 224 005** | **100 %** | | **667 579** |

Music et Books représentent 71,9 % du chiffre d'affaires. Les sept autres catégories pèsent chacune moins de 7 %.

### Dix produits au CA le plus élevé

| Produit | Catégorie | Total des ventes | Quantité vendue |
| --- | --- | --- | --- |
| 10000 | Home & Kitchen | 17 132 395 | 454 954 |
| 10003 | Electronics | 16 546 858 | 439 086 |
| 10001 | Music | 16 042 740 | 420 138 |
| 10002 | Music | 14 232 584 | 377 027 |
| 17502 | Books | 3 665 154 | 94 625 |
| 10579 | Music | 3 642 188 | 91 179 |
| 8601 | Clothing & Accessories | 3 593 108 | 89 600 |
| 5618 | Music | 3 511 170 | 95 677 |
| 16513 | Music | 3 503 889 | 91 710 |
| 2651 | Music | 3 503 651 | 88 936 |

Quatre produits (10000 à 10003) se détachent : chacun fait entre 14,2 et 17,1 millions, soit environ 5,0 % du CA à eux quatre, alors que le cinquième produit est à 3,7 millions. Cet écart est inhabituel (facteur 4 à 5) et peut venir de la façon dont les données ont été générées. Hypothèse à confirmer.

### CA par année

| Année | Total des ventes |
| --- | --- |
| 2001 | 258 159 395 |
| 2002 | 256 977 672 |
| 2003 | 259 060 055 |
| 2004 | 260 029 657 |
| 2005 (jusqu'au 13 décembre) | 242 997 226 |
| **Total** | **1 277 224 005** |

De 2001 à 2004, le CA annuel est stable : il reste entre 257,0 et 260,0 millions, soit un écart de 1,2 % entre la plus basse et la plus haute année. L'année 2005 paraît plus faible (−6,5 % par rapport à 2004), mais elle est incomplète : les ventes s'arrêtent le 2005-12-13, soit 18 jours en moins. Rapporté au nombre de jours couverts, le CA journalier moyen de 2005 est d'environ 0,700 million, contre 0,704 à 0,710 million sur 2001 à 2004 (calcul à partir des totaux ci-dessus : 2005 couvre 347 jours, 2004 en compte 366). Il n'y a donc pas de baisse nette des ventes en 2005.

### CA par mois (extrait : 2001)

Sur les 12 mois de 2001 affichés, le CA mensuel reste entre 19,96 millions (février) et 22,36 millions (octobre), sans saisonnalité marquée. Cela rejoint le constat du Jour 1 (« pas de saisonnalité visible »). Les ventes couvrent la période du 2001-01-01 au 2005-12-13.

## 5. Vérifications

| Contrôle | Résultat |
| --- | --- |
| CA total des ventes enrichies | 1 277 224 004,61 |
| Somme des CA par catégorie = CA total | OK |
| Somme des CA par mois = CA total | OK |
| Somme des CA par année = CA total | OK (1 277 224 004,61) |
| Lignes agrégées par catégorie = lignes des ventes (667 579) | OK |
| Lignes avant et après la jointure ventes et produits | 667 579 / 667 579 |
| Ventes sans catégorie | 0 |

Aucune ligne n'est perdue ni dupliquée par les transformations : toutes les agrégations retrouvent le total.

## 6. Écriture

Les quatre agrégations sont écrites au format Parquet :

- `data/gold/ca_par_categorie`
- `data/gold/ca_par_produit`
- `data/gold/ca_par_mois`
- `data/gold/ca_par_annee`

## 7. Limites

- Le montant est calculé avant coupons (`ss_ext_sales_price`). Il n'est donc pas le montant réellement payé, qui correspond à `ss_net_paid` (`_c20`).
- Seules les ventes en magasin (`store_sales`) sont analysées. Les ventes web et les retours ne sont pas inclus : la question sur les volumes par canal n'est pas couverte.
- Aucune marge ni aucun profit n'est agrégé. Le profit (`ss_net_profit`, `_c22`) est défini par la spécification comme le net payé moins le coût de gros × quantité. Il est négatif sur 74,3 % des lignes : une marge par catégorie serait possible, mais ce résultat inhabituel est à discuter avec le formateur avant interprétation.
- Le sens de `_c15` (`montant_vente`) est documenté par la spécification TPCx-BB (`ss_ext_sales_price`). La correspondance `_c15` / nom TPCx-BB repose sur l'ordre des colonnes du jeu de données, confirmé par le calcul `quantite × prix_vente`.
- L'année 2005 est incomplète (ventes jusqu'au 13 décembre) : ne pas la comparer directement aux autres années.
- Les quatre produits au CA exceptionnel (10000 à 10003) et l'absence de saisonnalité sont des constats à confirmer avec le formateur.

## 8. Conclusion

Les transformations répondent à la question prioritaire du Jour 1, « quels produits génèrent le plus de ventes ? » : le CA est concentré sur Music et Books (71,9 %), et quatre produits dominent le classement par article. Elles montrent aussi l'évolution dans le temps : un CA annuel stable de 2001 à 2004 (autour de 257 à 260 millions) et un CA mensuel stable sur 2001. La valeur plus basse de 2005 s'explique par une année incomplète. Les jeux Gold sont cohérents avec les données Silver : les sommes sont identiques et aucune ligne n'est perdue.
