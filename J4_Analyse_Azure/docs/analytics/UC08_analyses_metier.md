# UC-08 – Étape 4 : analyses métier

Deux analyses répondent à des questions métier issues du TP UC-01 :

- **Analyse 1** : quelles différences observe-t-on entre les magasins ?
- **Analyse 2** : quels produits contribuent le plus au montant des ventes ?

Les chiffres ci-dessous viennent des sorties du notebook `analytics/notebooks/TP4_Retail_Intelligence.ipynb`, exécuté sur le jeu **Silver** `store_sales` (667 579 lignes), joint à `item` pour l'analyse 2.

## Règles communes aux deux analyses

| Point | Choix | Justification |
|---|---|---|
| Mesure | **CA net HT = `_c20`** (`_c15` − coupons `_c19`) | Définition du KPI de l'UC-01. Le Gold est calculé sur le CA brut `_c15`, il n'est donc pas utilisé ici. |
| Unité | Monnaie du jeu TPCx-BB (non précisée), hors taxes | Le jeu ne fournit pas de devise. |
| Granularité source | 1 ligne = 1 article d'un ticket | 89 100 tickets, 17 820 produits, 12 valeurs de `_c7`. |
| Période | 2001-01-01 → 2005-12-13 | 2005 est partielle (347 jours). |
| Périmètre | Canal magasin uniquement (`store_sales`) | Le canal web n'est pas dans ce jeu : aucune analyse par canal n'est faite. |
| Filtres | Aucun : 667 579 lignes conservées | Les anomalies connues sont documentées en limites, pas supprimées. |
| Documentation du jeu | Spécification TPCx-BB v1.7.0, annexes B.1 et B.2 (fichier « Documentation jeu de données TPCxBB » du projet) | Sert à confirmer le sens des colonnes et à expliquer le caractère synthétique des données (voir encadré ci-dessous). |
| Vérification de jointure | 667 579 lignes avant et après la jointure `item`, 0 produit sans catégorie | Pas de perte ni de duplication de lignes. |

### Ce que dit la documentation du jeu (TPCx-BB v1.7.0, annexe B.2)

| Colonne (nom TPCx-BB) | Colonne du jeu | Ce que dit la documentation | Conséquence pour les analyses |
|---|---|---|---|
| `ss_store_sk` | `_c7` | « Random reference to s_store_sk » : le magasin est tiré **au hasard** | Les différences entre magasins ne sont pas un comportement commercial : elles sont produites par le générateur. |
| `ss_quantity` | `quantite` | Entier aléatoire de 1 à 100 | Explique la quantité min 1, max 100 et moyenne ≈ 50,6. |
| `ss_sales_price` | `prix_vente` | Prix catalogue réduit d'une remise aléatoire jusqu'à 1,00 | Le prix par produit varie très peu. |
| `ss_ext_sales_price` | `_c15` | `ss_sales_price` × `ss_quantity` | Relation vérifiée sans écart sur les données (CA brut). |
| `ss_coupon_amt` | `_c19` | 0,00 dans 80 % des cas, sinon une fraction aléatoire de `ss_ext_sales_price` | Explique les coupons : 9,92 % du CA brut. |
| `ss_net_paid` | `_c20` | Formule du document : `ss_ext_sales_price * ss_coupon_amt`, jugée **probablement une coquille** | Sur les données, `_c20` = `_c15` − `_c19` sans aucun écart : on retient cette définition (CA net). |
| `ss_ticket_number` | `num_ticket` | Séquence dense unique | Un ticket est bien un identifiant de panier. |
| `i_category` | `categorie` | Tirée d'une **liste pondérée** de catégories | Explique la part de Music (45,17 %) et Books (26,70 %) : elle suit le poids de la liste, pas un choix de clients. |
| `i_current_price` | (item) | Décimal aléatoire de 0,09 à 99,99 | Les prix ne reflètent pas de gamme réelle. |

La documentation décrit aussi des tables de **retours** (`store_returns`) et un canal **web** (`web_sales`), mais aucune de ces tables n'est dans nos jeux Silver/Gold : les retours ne sont pas déduits et le canal n'est pas analysable.

La documentation ne dit **rien** sur les produits d'identifiant 10000 à 10003 : leur sur-représentation reste inexpliquée (voir analyse 2). Les noms exacts des colonnes `_cN` sont retrouvés par leur **position** dans le schéma `store_sales` : la documentation ne les numérote pas.

---

## Analyse 1 – Différences entre les magasins

### 1. Question métier
Les magasins vendent-ils des volumes très différents ? Si oui, d'où vient l'écart (nombre de tickets ou montant du panier), et le classement est-il stable dans le temps ?

### 2. Données utilisées
- Table : `silver/store_sales`.
- Colonnes : `_c7` (identifiant du magasin, 12 valeurs de 0 à 11), `_c20` (CA net), `num_ticket`, `date_vente`.
- `_c7` correspond à `ss_store_sk` d'après sa **position** dans le schéma TPCx-BB (identification par l'ordre des colonnes, cohérente avec les 12 valeurs observées). La documentation confirme que `ss_store_sk` est le magasin, **tiré au hasard**. Le jeu ne contient aucune table magasin (pas de nom, de ville ni de surface).
- Granularité : une ligne par article. Chaque ticket a un seul magasin, donc on peut compter les tickets par magasin sans ambiguïté.

### 3. Méthode de calcul
- CA net par magasin = somme de `_c20`.
- Tickets = `countDistinct(num_ticket)`.
- Panier moyen = CA net / tickets. Le diviseur est le nombre de **tickets**, pas de lignes (diviser par les lignes donnerait environ 1 723, ce qui est faux).
- Part (%) = CA du magasin / CA total.
- Écart à la moyenne (%) = CA du magasin / moyenne des 12 magasins − 1.
- Écart meilleur / dernier = CA max / CA min − 1.
- Stabilité : classement des magasins par CA net, année par année.
- Test du hasard : écart-type observé du nombre de tickets par magasin, comparé à l'écart-type attendu si chaque ticket était affecté au hasard à l'un des 12 magasins (loi binomiale).

### 4. Résultats obtenus

| Magasin (`_c7`) | CA net | Tickets | Panier moyen | Part | Écart à la moyenne |
|---|---|---|---|---|---|
| 7 | 98 950 138 | 7 645 | 12 943 | 8,60 % | **+3,20 %** |
| 4 | 96 770 106 | 7 462 | 12 968 | 8,41 % | +0,93 % |
| 9 | 96 748 357 | 7 435 | 13 013 | 8,41 % | +0,91 % |
| 0 | 96 727 852 | 7 456 | 12 973 | 8,41 % | +0,89 % |
| 8 | 96 578 623 | 7 414 | 13 027 | 8,39 % | +0,73 % |
| 3 | 96 063 991 | 7 396 | 12 989 | 8,35 % | +0,19 % |
| 1 | 95 929 845 | 7 422 | 12 925 | 8,34 % | +0,05 % |
| 11 | 95 607 843 | 7 449 | 12 835 | 8,31 % | −0,28 % |
| 6 | 94 751 173 | 7 284 | 13 008 | 8,24 % | −1,17 % |
| 10 | 94 263 978 | 7 409 | 12 723 | 8,19 % | −1,68 % |
| 5 | 94 097 279 | 7 369 | 12 769 | 8,18 % | −1,86 % |
| 2 | 94 040 403 | 7 359 | 12 779 | 8,17 % | −1,92 % |

- **Écart entre le meilleur (magasin 7) et le dernier (magasin 2) : 5,22 %.**
- Les parts vont de 8,17 % à 8,60 %, pour une part « égale » théorique de 8,33 %.
- Panier moyen par magasin : de 12 723 à 13 027, soit environ 2,4 % d'écart. Le panier moyen global est de 12 912,79.
- Tickets par magasin : de 7 284 à 7 645, pour une moyenne de 7 425.

**Stabilité du classement (rang du CA net par année)**

| Magasin | 2001 | 2002 | 2003 | 2004 | 2005 |
|---|---|---|---|---|---|
| 7 | 3 | 1 | 1 | 1 | 7 |
| 0 | 5 | 6 | 2 | 9 | 2 |
| 1 | 1 | 9 | 11 | 6 | 4 |
| 9 | 11 | 8 | 6 | 5 | 1 |
| 2 | 9 | 4 | 10 | 11 | 10 |

(Extrait de 5 magasins sur 12.) Seul le magasin 7 reste en tête trois années de suite, puis retombe au rang 7 en 2005.

**Test du hasard** : écart-type observé des tickets par magasin = **85,3**, contre **82,5** attendu si l'affectation était purement aléatoire. Un test du χ² donne p ≈ 0,46, donc aucun écart significatif.


### 5. Interprétation

**Observé**
- Les magasins sont très proches : tous entre 8,17 % et 8,60 % du CA, avec 5,22 % d'écart entre le premier et le dernier.
- Le magasin 7 est le premier au total (+3,2 % par rapport à la moyenne). Son avance vient de son nombre de tickets (7 645 contre 7 425 en moyenne, soit +3,0 %) et non d'un panier plus élevé (12 943, soit +0,2 % par rapport au panier global).
- Le panier moyen varie peu d'un magasin à l'autre (environ 2,4 %).
- Le classement bouge beaucoup d'une année à l'autre. Les magasins 0, 1, 2 et 9 passent par exemple du haut au bas du classement, et inversement. Seul le magasin 7 est stable pendant trois ans.

**Hypothèses (non prouvées)**
- **Appuyé par la documentation** : `ss_store_sk` est une référence aléatoire. La dispersion observée est de l'ordre de celle du hasard (85,3 contre 82,5) : c'est cohérent avec cette génération aléatoire, et les écarts entre magasins s'expliquent donc très probablement par le tirage, pas par la performance des points de vente. Cela reste un raisonnement : seul un test sur des données réelles pourrait le confirmer.
- La première place du magasin 7 sur 2002–2004 pourrait être réelle, mais rien dans le jeu ne permet de l'expliquer (pas de surface, de zone de chalandise ni d'ouverture).

**Recommandations**
- Ne pas présenter de « magasin star » ni de « magasin en difficulté » sur ces seules données : l'écart est faible et instable.
- Pour une analyse réelle, il faudrait la table magasin, les surfaces et le calendrier d'ouverture, afin de comparer le CA au m² plutôt que le CA brut.
- Si le magasin 7 devait être étudié, il faudrait regarder en priorité son trafic (tickets) et non son panier.

### 6. Limites
- `_c7` est identifié comme le magasin par sa position dans le schéma et la documentation TPCx-BB, mais aucune table magasin n'est fournie pour le confirmer sur nos données.
- La documentation indique que le magasin est tiré au hasard : l'analyse mesure donc le comportement du générateur, pas celui d'un réseau réel.
- Aucun nom, région ni surface : on ne peut pas expliquer les écarts.
- Données synthétiques : l'uniformité observée est probablement un effet de la génération.
- 2005 est partielle, mais tous les magasins sont observés sur les mêmes jours, donc le classement total reste comparable.
- Le classement annuel repose sur des écarts de 1 à 2 % : il est fragile.
- Les retours ne sont pas déduits du CA (limite de l'UC-01).
- Canal web exclu (non présent dans `store_sales`) ; la marge n'est pas utilisée (74,29 % de lignes à perte, donc non fiable).

---

## Analyse 2 – Produits qui contribuent le plus au montant des ventes

### 1. Question métier
Le CA est-il concentré sur quelques produits, ou réparti sur tout le catalogue ? Combien de produits faut-il pour faire la moitié du CA ?

### 2. Données utilisées
- Tables : `silver/store_sales` (colonnes `id_produit`, `_c20`) jointe à `silver/item` (colonnes `id_produit`, `categorie`).
- Clé de jointure : `id_produit` (17 820 valeurs distinctes de chaque côté).
- Granularité d'analyse : le produit (agrégation des lignes de ticket).

### 3. Méthode de calcul
- CA net par produit = somme de `_c20`, et nombre de lignes par produit.
- Part (%) = CA du produit / CA total.
- **Part cumulée** : produits triés par CA décroissant, puis somme cumulée des parts. C'est le principe d'une courbe de Pareto.
- Concentration : part cumulée des 4, 10, 100 et 1 000 premiers produits, et nombre de produits nécessaires pour atteindre 50 % du CA.
- Distribution : `describe()` du CA et du nombre de lignes par produit (médiane, 90e et 99e percentiles).

### 4. Résultats obtenus

**Les 10 premiers produits**

| Rang | Produit | Catégorie | CA net | Lignes | Part | Part cumulée |
|---|---|---|---|---|---|---|
| 1 | 10000 | Home & Kitchen | 15 408 394 | 9 029 | 1,34 % | 1,34 % |
| 2 | 10003 | Electronics | 14 933 870 | 8 761 | 1,30 % | 2,64 % |
| 3 | 10001 | Music | 14 572 125 | 8 269 | 1,27 % | 3,90 % |
| 4 | 10002 | Music | 12 817 438 | 7 505 | 1,11 % | 5,02 % |
| 5 | 17502 | Books | 3 336 530 | 1 878 | 0,29 % | 5,31 % |
| 6 | 10579 | Music | 3 250 368 | 1 767 | 0,28 % | 5,59 % |
| 7 | 8601 | Clothing & Accessories | 3 238 750 | 1 761 | 0,28 % | 5,87 % |
| 8 | 5618 | Music | 3 212 955 | 1 867 | 0,28 % | 6,15 % |
| 9 | 2651 | Music | 3 172 288 | 1 730 | 0,28 % | 6,43 % |
| 10 | 16513 | Music | 3 162 636 | 1 817 | 0,27 % | 6,70 % |

**Concentration**

| Premiers produits | Part cumulée du CA |
|---|---|
| Top 4 | 5,02 % |
| Top 10 | 6,70 % |
| Top 100 | 28,12 % |
| Top 1 000 | 49,30 % |

- **1 133 produits sur 17 820 (6,4 %) suffisent pour atteindre 50 % du CA.**

**Distribution par produit**

| Indicateur | CA net | Lignes |
|---|---|---|
| Moyenne | 64 564 | 37 |
| Médiane | 34 949 | 21 |
| 90e percentile | 54 978 | 28 |
| 99e percentile | 1 067 531 | 613 |
| Maximum | 15 408 394 | 9 029 |
| Minimum | 2 787 | 6 |

### 5. Interprétation

**Observé**
- La concentration est **moyenne** : la moitié du CA vient de 6,4 % des produits, et 80 % du CA demande environ 8 930 produits (la moitié du catalogue).
- Les produits 10000 à 10003 sont **atypiques** : chacun a de 7 505 à 9 029 lignes, contre une médiane de 21 lignes par produit. Ils pèsent pourtant 5,02 % du CA à eux quatre, ce qui reste modeste : ils ne suffisent pas à créer une forte concentration.
- Après ces quatre produits, le CA décroît progressivement : les produits 5 à 10 valent chacun environ 0,28 %, et le CA par ligne est comparable partout.
- La moyenne (64 564) est presque le double de la médiane (34 949) et le 99e percentile (1 067 531) est très éloigné du 90e (54 978) : la distribution a une **queue lourde** portée par un petit nombre de produits (environ 1 % des produits dépassent 613 lignes).
- La domination de Music (45,17 %) et Books (26,70 %) vient du nombre de lignes (301 236 et 177 671), pas de produits individuels exceptionnels. La documentation précise que la catégorie est tirée d'une liste **pondérée** : ce poids explique cette part.

**Hypothèses (non prouvées)**
- Les quatre produits à identifiants consécutifs 10000–10003 ont un volume sans rapport avec les autres, et la documentation ne l'explique pas. L'hypothèse la plus plausible est un artefact de génération (probabilité de tirage plus forte) plutôt qu'un vrai best-seller ; à confirmer avec le formateur ou le noyau du générateur.
- Le catalogue présente une longue traîne régulière, avec un faible nombre de lignes par produit pour la majorité (médiane 21).

**Recommandations**
- Ne pas bâtir de stratégie sur un « top 4 » : il ne représente que 5 % du CA. Un classement plus utile se fait au niveau **catégorie** puis produit.
- Signaler dans le rendu que 10000–10003 sont des cas atypiques à vérifier avant toute conclusion commerciale.
- Un suivi par classes de produits (par exemple A / B / C selon la part cumulée de CA) serait plus parlant qu'un top 10.

### 6. Limites
- Les identifiants produits sont des clés techniques ; seule la catégorie est ajoutée via `item`.
- Les 7 768 produits dont le coût dépasse le prix, les 3 324 prix nuls et les 14 lignes en doublon sont conservés : leur effet sur le CA net est nul ou négligeable (les prix nuls donnent un montant de 0).
- Données synthétiques : la concentration observée peut refléter les paramètres du générateur et non un comportement d'achat.
- Les retours ne sont pas déduits, et la marge n'est pas utilisée (74,29 % de lignes à perte).
- Le classement est sur toute la période 2001–2005, sans corriger l'inégalité des années (2005 partielle).
- Aucune notion de prix catalogue ni de période de présence du produit : un produit récent pourrait être désavantagé.
