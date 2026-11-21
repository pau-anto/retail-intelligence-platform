# UC-08 – Statistiques descriptives 

Cette étape décrit les données avant de les interpréter : combien d'enregistrements, quelles valeurs extrêmes, quelles valeurs typiques, quelles sommes, comment les ventes se répartissent et évoluent. Le code est dans la **section 4 du notebook** `TP4_Retail_Intelligence.ipynb`. Les valeurs ci-dessous ont été calculées sur tes fichiers Parquet (relevé du 2026-11-20) ; les tiennes, lues dans ton notebook, font foi. Données **synthétiques**.

## 1. Choix du jeu de données

Le sujet demande « au moins un jeu pertinent ». On le choisit avec les six statistiques demandées comme critères.

| Statistique demandée | `silver/store_sales` | `silver/item` | `gold/ca_par_mois` | `gold/ca_par_categorie` |
| --- | --- | --- | --- | --- |
| Nombre d'enregistrements | Oui (667 579) | Oui (17 820) | Oui, mais 60 | Oui, mais 9 |
| Minimum et maximum | Oui, sur des mesures | Prix, coût | Sur 60 valeurs mensuelles seulement | 9 valeurs seulement |
| Moyenne et médiane | Oui, significatives | Peu utile ici | Peu de valeurs | Non |
| Sommes de mesures additives | Oui | Non (pas de mesure à additionner) | Déjà sommé | Déjà sommé |
| Répartition par dimension | Oui (catégorie via `item`, magasin, année) | Par catégorie, mais sans ventes | Non | Déjà fait |
| Évolution temporelle | Oui (`date_vente`, 1 808 jours) | Non | Oui, mais déjà agrégé | Non |

**Choix : `silver/store_sales`**, complété par `silver/item` (pour la catégorie). C'est le seul jeu qui permet de calculer les six statistiques sur des données non agrégées. Les Gold sont déjà des résultats d'agrégation : ils servent à **recouper** les chiffres (écart 0,0), pas à décrire une distribution.

Règles à retenir pour choisir une statistique selon la nature de la colonne :

| Nature | Exemples | Statistiques adaptées | À éviter |
| --- | --- | --- | --- |
| Mesure additive | `quantite`, `_c15`, `_c20`, `profit` | min, max, moyenne, médiane, **somme** | – |
| Mesure non additive | `prix_vente` (prix unitaire) | min, max, moyenne, médiane | **Somme** (sans sens) |
| Clé / identifiant | `num_ticket`, `id_produit`, `_c7` | nombre de valeurs **distinctes** | Moyenne, somme |
| Dimension | `categorie`, magasin | répartition (effectifs, parts) | Moyenne |
| Date | `date_vente` | première et dernière date, évolution | – |

## 2. Construire le notebook, cellule par cellule

Chaque sous-section s'ouvre par une cellule Markdown qui dit l'objectif, puis une cellule de code. Prérequis : la session Spark et les DataFrames `ventes` et `produits` de la section 2 du notebook.

| Section | Objectif | Idée du code | Sortie enregistrée |
| --- | --- | --- | --- |
| 4.1 Comptages | Taille et périmètre du jeu | `count()` et `select(...).distinct().count()` ; `min` et `max` de `date_vente` | `statistiques_comptages.csv` |
| 4.2 Variables numériques | Décrire chaque mesure | `agg` avec `count`, `min`, `percentile`, `max`, `avg`, `stddev`, `sum` ; somme remise à vide pour `prix_vente` | `statistiques_variables.csv` |
| 4.3 Tickets | Décrire au grain « ticket » | `groupBy("num_ticket")` puis `describe` sur le petit résultat | `statistiques_par_ticket.csv` |
| 4.4 Catégories | Répartition par dimension | `join` avec `item` sur `id_produit`, contrôle du nombre de lignes, `groupBy("categorie")`, part en % | `statistiques_par_categorie.csv` |
| 4.5 Temps | Évolution | agrégation **par jour** puis regroupement par année, mois, jour de la semaine en pandas | `statistiques_par_annee.csv`, `_par_mois.csv`, `_par_jour_semaine.csv` |
| 4.6 Contrôles | Prouver la cohérence | Comparer les sommes entre sections | affichage |

Le cœur de la cellule 4.2 (à comprendre, le reste suit le même principe) :

```python
r = ventes.agg(
    F.count(col).alias("n"),                                     # valeurs non nulles
    F.sum(F.col(col).isNull().cast("int")).alias("manquants"),   # valeurs manquantes
    F.min(col).alias("min"), F.max(col).alias("max"),
    F.expr(f"percentile(`{col}`, 0.5)").alias("mediane"),        # médiane exacte
    F.avg(col).alias("moyenne"), F.stddev(col).alias("ecart_type"),
    F.sum(col).alias("somme")).first()
```

Trois bonnes pratiques :
- **Agréger dans Spark avant de passer à pandas** : on fait `toPandas()` sur un petit résultat (89 100 tickets, 1 808 jours), jamais sur les 667 579 lignes.
- **Contrôler les jointures** : nombre de lignes avant et après, lignes sans correspondance.
- **Terminer par des contrôles** : les sommes obtenues par des chemins différents doivent être égales (section 4.6, tous les écarts valent 0).

## 3. Résultats

### 3.1 Comptages (4.1)

| Élément | Valeur |
| --- | --- |
| Lignes de vente | 667 579 |
| Tickets distincts | 89 100 |
| Produits distincts vendus | 17 820 (tous les produits d'`item`) |
| Magasins distincts (`_c7`) | 12 |
| Jours distincts avec ventes | 1 808 |
| Période | 2001-01-01 au 2005-12-13 |

### 3.2 Variables numériques (4.2)

| Variable | Min | Q1 | Médiane | Q3 | Max | Moyenne | Écart-type | Somme |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quantité par ligne | 1 | 26 | 51 | 76 | 100 | 50,56 | 28,88 | 33 755 474 |
| Prix de vente unitaire | 0,00 | 10,25 | 27,69 | 56,78 | 199,30 | 37,86 | 34,40 | sans objet |
| Montant brut de la ligne (`_c15`) | 0,00 | 313,56 | 1 048,50 | 2 674,44 | 18 745,00 | 1 913,22 | 2 281,75 | 1 277 224 004,61 |
| Net payé de la ligne (`_c20`) | 0,00 | 245,70 | 878,54 | 2 366,51 | 18 745,00 | 1 723,44 | 2 167,90 | 1 150 529 586,37 |
| Profit de la ligne | −9 866,60 | −1 461,80 | −377,18 | 5,88 | 9 134,00 | −827,70 | 1 727,49 | −552 553 400 (environ) |

Aucune valeur manquante sur ces cinq variables. Le profit est négatif sur 495 971 lignes, positif sur 171 401 et nul sur 207.

### 3.3 Par ticket (4.3)

| Mesure | Moyenne | Écart-type | Min | Q1 | Médiane | Q3 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lignes par ticket | 7,49 | 4,02 | 1 | 4 | 7 | 11 | 14 |
| Quantité par ticket | 378,85 | 217,36 | 1 | 194 | 372 | 550 | 1 143 |
| Net payé par ticket | 12 912,79 | 9 063,74 | 0,00 | 5 572,46 | 11 645,14 | 18 791,10 | 64 785,95 |

46 tickets ont un net payé de 0.

### 3.4 Par catégorie (4.4)

Jointure : 667 579 lignes avant et après, 0 vente sans catégorie.

| Catégorie | Lignes | Quantité | CA net | Part du CA net | Part cumulée | Prix de vente moyen |
| --- | --- | --- | --- | --- | --- | --- |
| Music | 301 236 | 15 238 374 | 519,7 M | 45,17 % | 45,17 % | 37,85 |
| Books | 177 671 | 9 007 511 | 307,2 M | 26,70 % | 71,86 % | 37,89 |
| Movies & TV | 43 376 | 2 189 279 | 74,7 M | 6,50 % | 78,36 % | 37,91 |
| Clothing & Accessories | 32 372 | 1 640 550 | 56,8 M | 4,93 % | 83,29 % | 38,45 |
| Electronics | 32 619 | 1 632 098 | 55,7 M | 4,84 % | 88,14 % | 37,94 |
| Home & Kitchen | 24 380 | 1 226 839 | 41,3 M | 3,59 % | 91,72 % | 37,55 |
| Sports & Outdoors | 23 911 | 1 209 305 | 40,9 M | 3,56 % | 95,28 % | 37,74 |
| Toys & Games | 16 121 | 809 999 | 27,4 M | 2,38 % | 97,66 % | 37,83 |
| Tools & Home Improvement | 15 893 | 801 519 | 26,9 M | 2,34 % | 100,00 % | 37,12 |

### 3.5 Évolution dans le temps (4.5)

Par année :

| Année | Jours couverts | Lignes | Tickets | Quantité | CA net | CA net par jour |
| --- | --- | --- | --- | --- | --- | --- |
| 2001 | 365 | 134 873 | 17 991 | 6 814 234 | 232,50 M | 636 983 |
| 2002 | 365 | 135 084 | 17 990 | 6 825 340 | 230,95 M | 632 732 |
| 2003 | 365 | 134 773 | 17 990 | 6 820 308 | 233,58 M | 639 932 |
| 2004 | 366 | 136 014 | 18 039 | 6 887 086 | 234,34 M | 640 287 |
| 2005 | **347** | 126 835 | 17 090 | 6 408 506 | 219,16 M | 631 595 |

Par mois (59 mois complets, **décembre 2005 exclu** : 13 jours) : CA net moyen 19,36 M, médiane 19,42 M, écart-type 0,61 M ; minimum **février 2002** (17,59 M), maximum **octobre 2003** (20,63 M). Le CA net par jour d'un mois varie de 615 405 à 670 303, autour de 636 486.

Par mois calendaire : février est le plus bas en CA mensuel (18,06 M en moyenne) mais **pas en CA par jour** (640 557, parmi les plus hauts) : il compte simplement moins de jours.

Par jour de la semaine : le CA net par jour est quasi identique, de 633 756 (mardi) à 640 136 (mercredi).

## 4. Lecture des résultats

| Type | Contenu |
| --- | --- |
| **Observé** | Les cinq variables sont complètes. Médiane et moyenne sont proches pour la quantité (51 et 50,6) et le prix (27,7 et 37,9) : la quantité est symétrique (entre 1 et 100), le prix est asymétrique (moyenne > médiane). Le montant de ligne est très asymétrique (moyenne 1 913 pour une médiane de 1 049, max 18 745). Le CA par jour est stable d'une année à l'autre (632 000 à 640 000). Le CA mensuel ne varie que d'environ ±3 % autour de la moyenne. Le profit est négatif en médiane (−377). Le prix moyen est le même dans toutes les catégories (37 à 38) |
| **Hypothèses** | La régularité du CA (par jour, par mois, par jour de la semaine, par catégorie) est probablement un effet de la **génération synthétique** des données, pas un comportement de clients. L'écart de février vient du nombre de jours. Le profit négatif tient probablement à la façon dont les coûts sont générés (non confirmé) |
| **Recommandations** | Ne pas parler de saisonnalité ni de pic hebdomadaire. Comparer des années sur le **CA par jour** ou en excluant 2005. Ne pas présenter de marge. Décrire la concentration (Music + Books = 71,9 %) comme un fait de répartition, pas comme une cause |

## 5. Pièges rencontrés

- **2005 a 347 jours** : comparer son CA total à celui des autres années donne une fausse baisse de 6,5 %.
- **Somme d'un prix unitaire** : sans sens, elle est laissée vide.
- **Moyenne d'un identifiant** (`_c7`, `id_produit`) : sans sens, on compte les valeurs distinctes.
- **Net et brut** : les statistiques de 3.2 donnent les deux ; le CA net est celui de l'UC-01.
- **46 tickets à net nul contre 37 à brut nul** : 9 tickets ont un coupon égal à leur montant.

**Preuve** : sorties de la section « Stats descriptives » du notebook `analytics/notebooks/TP4_Retail_Intelligence.ipynb`.