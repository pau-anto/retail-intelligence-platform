# UC-08 – Vérifier les KPI 

## 1. Ce que dit le dictionnaire UC-01 et ce qu'on peut vérifier

Le dictionnaire UC-01 contient 6 KPI, calculés sur le magasin **et** le web. Ici, seul le magasin est disponible (`web_sales` n'a pas été traité en Silver) : on vérifie donc la partie magasin, et on ne peut pas recalculer les valeurs web.

| KPI UC-01 | Valeur UC-01 (magasin) | Valeur recalculée | Verdict |
| --- | --- | --- | --- |
| Chiffre d'affaires net HT | 1 150 529 586 | 1 150 529 586,37 | Identique |
| Nombre de transactions | 89 100 | 89 100 | Identique |
| Panier moyen | 12 913 | 12 912,79 | Identique (arrondi) |
| Quantités vendues | 33 755 474 | 33 755 474 | Identique |
| Taux de remise | 50,0 % | 49,99 % | Identique (arrondi) |
| Évolution annuelle du CA | 2002 : −0,4 % ; 2003 : +1,1 % ; 2004 : −0,2 % (magasin **+ web**) | Magasin seul : voir K6 | **Non comparable** : périmètre différent |

## 2. Règles communes

| Élément | Valeur |
| --- | --- |
| Périmètre | Ventes **en magasin** (`store_sales`) ; pas de web, pas de retours |
| Période | 2001-01-01 au 2005-12-13 (décembre 2005 : 13 jours ; 2005 incomplète) |
| Filtres | **Aucun** : les 667 579 lignes sont conservées, y compris 495 971 lignes à perte et 3 324 lignes à prix nul |
| Unité monétaire | Non communiquée (« devise non communiquée » dans l'UC-01) : on écrit « monétaire » |
| Sources | `silver/store_sales` (K1 à K7, K9) ; `gold/ca_par_categorie` (K8) |
| Limites UC-01 reprises | CA **avant retours** ; numéros de ticket magasin et de commande web identiques : toujours préciser le canal ; données synthétiques |

## 3. Vérification préalable des champs

| Champ | Existe | Valeurs manquantes | Vérification de cohérence (toutes les lignes) |
| --- | --- | --- | --- |
| `_c20` (net payé, `ss_net_paid`) | Oui, double | 0 | `_c20 = _c15 − _c19` : 0 écart |
| `_c15` (montant brut de ligne) | Oui, double | 0 | `_c15 = quantite × prix_vente` : 0 écart |
| `_c19` (coupon) | Oui, double | 0 | Somme = 126 694 418,24 ; 137 194 lignes avec coupon |
| `_c14` (remise) et `_c17` (prix catalogue × quantité) | Oui, double | 0 | `_c14 = _c17 − _c15` : 0 écart ; `_c17 = quantite × _c12` : 0 écart |
| `quantite` | Oui, integer | 0 | De 1 à 100, aucune valeur ≤ 0 |
| `num_ticket` | Oui, integer | 0 | 89 100 valeurs distinctes ; 1 à 14 lignes par ticket ; chaque ticket n'a **qu'un magasin et qu'une date** |
| `_c7` (magasin) | Oui, integer | 0 | 12 valeurs distinctes (0 à 11) |
| `date_vente` | Oui, date | 0 | 2001-01-01 à 2005-12-13 |

Les relations arithmétiques confirment la cohérence interne des colonnes. Les **noms** TPCx-BB (`ss_net_paid`, `ss_ext_discount_amt`…) restent déduits de l'ordre des colonnes.

## 4. KPI retenus

Les six premiers sont ceux de l'UC-01 (partie magasin). K7 à K9 sont des compléments utiles à l'étape 4.

### K1 – Chiffre d'affaires net HT

| Élément | Contenu |
| --- | --- |
| Définition métier | Argent encaissé hors taxe, après remises et coupons (définition UC-01) |
| Formule | `SUM(ss_net_paid)`, soit la somme de `_c20` |
| Champs | `_c20` ; contrôle : `_c15` et `_c19` |
| Filtres | Aucun |
| Granularité | Calcul à la ligne de vente ; restitué en total, par année, par magasin |
| Unité | Monétaire (non communiquée) |
| **Valeur calculée** | **1 150 529 586,37** (= CA brut 1 277 224 004,61 − coupons 126 694 418,24) |
| Limites | **Retours non déduits** (limite UC-01) ; magasins seulement ; 2005 incomplète ; 54,6 % du CA brut provient de lignes à profit négatif : le CA ne mesure pas la rentabilité |

### K2 – Nombre de transactions

| Élément | Contenu |
| --- | --- |
| Définition métier | Nombre de tickets de caisse |
| Formule | `COUNT(DISTINCT ss_ticket_number)`, soit les valeurs distinctes de `num_ticket` |
| Champs | `num_ticket` |
| Filtres | Aucun |
| Granularité | Ticket |
| Unité | Nombre de tickets |
| **Valeur calculée** | **89 100** (7,49 lignes par ticket en moyenne, de 1 à 14) |
| Limites | Mêmes numéros que les commandes web : toujours préciser « magasin ». 37 tickets ont un montant de 0, conservés |

### K3 – Panier moyen

| Élément | Contenu |
| --- | --- |
| Définition métier | Chiffre d'affaires moyen par transaction |
| Formule | CA net ÷ nombre de transactions (K1 ÷ K2) |
| Champs | `_c20`, `num_ticket` |
| Filtres | Aucun |
| Granularité | Ticket |
| Unité | Monétaire par ticket |
| **Valeur calculée** | **12 912,79** par ticket (médiane 11 645,14). En brut : 14 334,73 |
| Limites | **Diviser par le nombre de lignes serait faux** (limite UC-01) : cela donne 1 723 en net, soit un montant moyen par ligne. Valeurs très élevées, signe de données synthétiques (50 articles par ligne en moyenne) |

### K4 – Quantités vendues

| Élément | Contenu |
| --- | --- |
| Définition métier | Nombre d'unités vendues |
| Formule | `SUM(ss_quantity)`, soit la somme de `quantite` |
| Champs | `quantite` |
| Filtres | Aucun |
| Granularité | Ligne de vente |
| Unité | Unités |
| **Valeur calculée** | **33 755 474** (égale à la somme de `quantite_totale` de `gold/ca_par_mois`) |
| Limites | Ne pas confondre avec les lignes (667 579) ni les tickets. Quantité moyenne de 50,6 par ligne : irréaliste pour un magasin, effet des données synthétiques |

### K5 – Taux de remise

| Élément | Contenu |
| --- | --- |
| Définition métier | Part du prix catalogue accordée en remise (définition UC-01) |
| Formule | `SUM(ext_discount_amt) ÷ SUM(ext_list_price)`, soit somme de `_c14` ÷ somme de `_c17` |
| Champs | `_c14`, `_c17` |
| Filtres | Aucun |
| Granularité | Ensemble des lignes ; peut être restitué par année |
| Unité | % |
| **Valeur calculée** | **49,99 %** (1 276 714 271,73 ÷ 2 553 938 276,34) |
| Limites | Quasi constant : peu informatif (limite UC-01), signe d'une génération de prix à partir d'un prix catalogue moitié moins cher. Ne comprend pas les coupons. Noms de colonnes déduits |

### K6 – Évolution annuelle du CA (magasin seul)

| Élément | Contenu |
| --- | --- |
| Définition métier | Variation du CA d'une année sur l'autre |
| Formule | CA net année N ÷ CA net année N−1 − 1 |
| Champs | `_c20`, `date_vente` (année) |
| Filtres | **2005 exclue** (incomplète : jusqu'au 13/12) ; la variation 2005/2004 n'est pas calculée |
| Granularité | Année |
| Unité | % |
| **Valeur calculée** | CA net : 2001 232,50 M ; 2002 230,95 M ; 2003 233,58 M ; 2004 234,34 M. Variations : **2002 : −0,67 %** ; **2003 : +1,14 %** ; **2004 : +0,33 %** |
| Limites | Le dictionnaire UC-01 donne −0,4 %, +1,1 % et −0,2 % pour **magasin + web** : les valeurs diffèrent car le périmètre n'est pas le même. Variations très faibles : pas de tendance, régularité typique de données synthétiques. Comparer 2005 aux autres années donnerait −6,5 % : c'est un artefact de la période incomplète, pas une baisse |

### K7 – Chiffre d'affaires brut (complément)

| Élément | Contenu |
| --- | --- |
| Définition métier | Valeur des ventes avant coupons et taxes : c'est la mesure des jeux Gold du TP3 |
| Formule | Somme de `_c15` (= `quantite × prix_vente`) |
| Champs | `_c15` |
| Filtres | Aucun |
| Granularité | Ligne de vente ; restitué par année, mois (Gold) |
| Unité | Monétaire |
| **Valeur calculée** | **1 277 224 004,61**, égale à la somme des 4 jeux Gold (écart 0,0) |
| Limites | Ce n'est pas l'argent encaissé (coupons de 9,92 % non déduits). Il ne doit pas être mélangé avec K1 dans un même graphique |

### K8 – Répartition des ventes par catégorie

| Élément | Contenu |
| --- | --- |
| Définition métier | Part de chaque catégorie de produit dans le CA |
| Formule | CA de la catégorie ÷ CA total |
| Champs | `categorie`, `total_ventes` de `gold/ca_par_categorie` (brut) ; jointure `silver/store_sales` et `silver/item` sur `id_produit` |
| Filtres | Aucun |
| Granularité | Catégorie (9 lignes) |
| Unité | % |
| **Valeur calculée** | Music **45,2 %**, Books **26,7 %**, Movies & TV 6,5 %, Clothing & Accessories 4,9 %, Electronics 4,8 %, Home & Kitchen 3,6 %, Sports & Outdoors 3,6 %, Toys & Games 2,4 %, Tools & Home Improvement 2,3 %. Music + Books : 71,9 %. Les parts sont **identiques à 0,1 point près en net** |
| Limites | Dépend de la jointure `item` (0 vente sans catégorie). Pas de marge. Les quatre produits les plus vendus (10000 à 10003) ne pèsent que 5,0 % du CA : ils n'expliquent pas la concentration |

### K9 – CA par magasin

| Élément | Contenu |
| --- | --- |
| Définition métier | CA réalisé par chaque magasin |
| Formule | Somme de `_c20` par valeur de `_c7` |
| Champs | `_c7` (magasin, **hypothèse** : `ss_store_sk`), `_c20`, `num_ticket` |
| Filtres | Aucun |
| Granularité | Magasin (12 lignes) |
| Unité | Monétaire et % du CA |
| **Valeur calculée** | Écart entre le plus haut et le plus bas magasin : **5,2 % en net** (4,9 % en brut). En brut, le magasin 7 est le plus élevé (109,7 M, 8,59 %) et le magasin 2 le plus bas (104,6 M, 8,19 %) |
| Limites | Sens de `_c7` déduit. Écarts faibles (déjà notés au Jour 1). Pas de taille de magasin ni de trafic. Pas de Gold par magasin : calcul depuis Silver |
