# UC-08 –Constats métier

Contexte commun : jeu Silver `store_sales` (667 579 lignes, 89 100 tickets, 2001-01-01 → 2005-12-13), CA net HT = `_c20` ; données **synthétiques** TPCx-BB (spécification v1.7.0 : magasin tiré au hasard, catégorie tirée d'une liste pondérée, quantité aléatoire de 1 à 100).

---

## Constat 1 – Les magasins sont quasi équivalents : aucun « magasin star » ni « magasin en difficulté » n'est identifiable

**Résultat observé**
- Les 12 magasins réalisent entre 94,0 et 99,0 millions de CA net, soit de 8,17 % à 8,60 % du CA total.
- L'écart entre le premier (magasin 7) et le dernier (magasin 2) est de **5,22 %**.
- Le magasin 7 est à +3,20 % de la moyenne. Son avance vient de ses tickets (7 645 contre 7 425 en moyenne) et non de son panier (12 943, proche du panier global de 12 912,79).
- Le panier moyen varie peu d'un magasin à l'autre : de 12 723 à 13 027, soit environ 2,4 %.
- Le classement change fortement d'une année à l'autre. Seul le magasin 7 reste premier trois années de suite (2002 à 2004), puis tombe au rang 7 en 2005.
- Écart-type du nombre de tickets par magasin : 85,3 observé, contre 82,5 attendu si les tickets étaient répartis au hasard.

**Interprétation possible**
- Les écarts observés sont du même ordre que ceux du hasard (85,3 contre 82,5). Cela est cohérent avec la documentation TPCx-BB, qui indique que le magasin est une référence tirée au hasard.
- Il est donc plus probable que les écarts viennent du tirage que de la performance des points de vente.
- La première place du magasin 7 sur 2002–2004 pourrait être réelle, mais le jeu ne contient rien qui l'explique.

**Limite de l'analyse**
- `_c7` est identifié comme le magasin par sa position dans le schéma et la documentation ; aucune table magasin (nom, région, surface, date d'ouverture) n'est fournie.
- Données synthétiques : l'uniformité mesure le générateur, pas un réseau réel.
- Le classement annuel repose sur des écarts de 1 à 2 % : il est fragile.
- Les retours ne sont pas déduits du CA, et le canal web n'est pas dans le jeu.

**Recommandation**
- Ne pas classer les magasins en « bons » et « mauvais » à partir de ces seules données.
- Pour une vraie analyse de réseau, ajouter la table magasin et comparer le CA au m² ou au nombre de salariés.
- Si le magasin 7 est étudié, regarder d'abord son trafic (nombre de tickets), pas son panier.

---

## Constat 2 – Les ventes sont stables dans le temps : pas de tendance ni de saisonnalité visibles

**Résultat observé**
- Le CA net moyen par jour est de 636 983 en 2001, 632 732 en 2002, 639 932 en 2003, 640 287 en 2004 et 631 595 en 2005.
- Variations annuelles du CA **par jour** : −0,67 % (2002), +1,14 % (2003), +0,06 % (2004), −1,36 % (2005).
- Le CA total de 2005 paraît en baisse de 6,48 % : c'est un artefact, car 2005 ne compte que 347 jours (fin au 13 décembre).
- Sur le graphique, le CA par jour reste autour de 636 000 chaque mois, avec une variation d'environ 1,8 % (mois complets).
- Février est bas en CA total, mais pas en CA par jour : c'est un effet de calendrier.

**Interprétation possible**
- Le CA moyen par jour est quasi constant : le niveau d'activité ne croît ni ne décroît sur cinq ans, et il n'y a ni pic de fin d'année ni creux d'été.
- Cette régularité est inhabituelle pour de vraies ventes (période de fêtes, soldes) et correspond plutôt à un générateur qui répartit les ventes de manière homogène sur les jours.

**Limite de l'analyse**
- 2005 est partielle (13 jours en décembre) : il faut comparer le CA par jour, pas le CA total.
- Seules les ventes en magasin sont analysées (pas le web), les retours ne sont pas déduits, et les données sont synthétiques.
- Aucun événement (promotion, ouverture, fermeture) n'est disponible pour expliquer d'éventuelles variations.
- Les variations de ±1 % sont trop faibles pour être interprétées comme une tendance.

**Recommandation**
- Toujours présenter les évolutions en **CA par jour** (ou exclure 2005) pour éviter une fausse baisse de 6,48 %.
- Ne pas déduire de prévisions de ce jeu : une série plate ne permet pas de prévoir une saisonnalité réelle.
- Avec des données réelles, ajouter le calendrier des promotions et le canal web avant de conclure sur l'évolution.

---

## Constat 3 – La concentration du CA par produit est moyenne ; quatre produits atypiques ne l'expliquent pas

**Résultat observé**
- **1 133 produits sur 17 820 (6,4 %)** réalisent 50 % du CA net.
- Parts cumulées : top 4 = 5,02 %, top 10 = 6,70 %, top 100 = 28,12 %, top 1 000 = 49,30 %.
- Les produits 10000 à 10003 ont chacun de 7 505 à 9 029 lignes, contre une médiane de 21 lignes par produit.
- La moyenne du CA par produit (64 564) est presque le double de la médiane (34 949) ; le 99e percentile (1 067 531) est très éloigné du 90e (54 978).

**Interprétation possible**
- La distribution a une queue lourde : quelques centaines de produits (environ 1 % des produits ont plus de 613 lignes) portent une part importante du CA, tandis que la grande majorité reste autour de 21 lignes.
- Les produits 10000 à 10003 ne pèsent que 5,02 % du CA à eux quatre : ils sont atypiques, mais ils ne créent pas à eux seuls la concentration.
- Leur sur-représentation pourrait être un artefact du générateur ; la documentation ne l'explique pas.

**Limite de l'analyse**
- Les identifiants produits sont des clés techniques : aucun libellé exploitable n'est utilisé.
- Données synthétiques : la concentration peut refléter les paramètres du générateur et non un comportement d'achat.
- Le classement porte sur toute la période (2005 partielle), sans tenir compte de la date d'arrivée d'un produit au catalogue.
- Anomalies conservées : 7 768 produits avec coût > prix, 3 324 prix nuls, 14 doublons (effet négligeable sur le CA net).

**Recommandation**
- Ne pas construire une stratégie sur un « top 4 » ou un « top 10 » : ils pèsent 5,02 % et 6,70 % du CA.
- Suivre les produits par **classes de contribution** (par exemple A / B / C selon la part cumulée du CA) plutôt que par un simple top N.
- Faire vérifier les produits 10000 à 10003 (formateur, générateur) avant toute conclusion commerciale.

---

## Constat 4 – Music et Books font près des trois quarts du CA, à cause du nombre de ventes et non d'un prix plus élevé

**Résultat observé**
- Music = 45,17 % du CA net (301 236 lignes) et Books = 26,70 % (177 671 lignes), soit **71,87 %** à eux deux.
- Les sept autres catégories se partagent 28,13 % du CA.
- Le CA moyen par ligne est proche d'une catégorie à l'autre, entre environ 1 690 et 1 730 (par exemple Music ≈ 1 725, Electronics ≈ 1 708, Home & Kitchen ≈ 1 692).

**Interprétation possible**
- La part de chaque catégorie suit le nombre de lignes vendues : c'est le volume, pas le prix ni la valeur du panier, qui distingue Music et Books.
- La documentation TPCx-BB précise que la catégorie est tirée d'une liste **pondérée** : ce poids explique la domination de Music et Books, sans qu'il s'agisse forcément d'un choix de clients.

**Limite de l'analyse**
- Le CA par ligne est calculé à partir des sorties du notebook (CA net / lignes) ; il ne tient pas compte des quantités différentes par ligne.
- Données synthétiques ; les retours ne sont pas déduits ; pas de notion de marge fiable (74,29 % de lignes à perte).
- Aucune donnée sur le stock, la place en rayon ou les promotions par catégorie.

**Recommandation**
- Présenter les catégories en **part de lignes et part de CA** côte à côte, pour montrer que l'écart vient du volume.
- Pour piloter un assortiment réel, compléter par la marge et le taux de retour par catégorie avant toute décision.

---

## Synthèse 

| # | Constat | Résultat clé | Niveau de confiance |
|---|---|---|---|
| 1 | Magasins équivalents | Écart max 5,22 %, classement instable | Élevé sur le chiffre ; faible sur toute explication |
| 2 | Ventes stables | ≈ 636 000 par jour, ±1,8 % | Élevé sur le chiffre ; faible sur la prévision |
| 3 | Concentration moyenne par produit | 6,4 % des produits = 50 % du CA | Élevé sur le chiffre ; cause du top 4 inconnue |
| 4 | Music + Books = 71,87 % du CA | Effet du volume de lignes | Élevé sur le chiffre ; lié à la génération pondérée |

Les quatre constats partagent une même limite : **jeu synthétique**. Ils décrivent ce que contient le jeu, pas le fonctionnement d'une vraie enseigne.