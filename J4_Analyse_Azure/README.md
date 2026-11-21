# J4 – Analyse des données et transposition sur Azure

Retail Intelligence Platform – IPSSI, Mastère Développement / Data / IA – TP du Jour 4
**Parcours choisi : A – Azure** (abonnement Azure for Students fourni par l'école)

Ce dossier contient les livrables du Jour 4 :
- **UC-08** : analyse des données et visualisation, à partir des jeux Silver et Gold produits au Jour 3 ;
- **UC-07** : transposition de la plateforme sur Azure, avec un déploiement **réel** limité au stockage ADLS Gen2.

Toutes les données sont **synthétiques** (jeu TPCx-BB). Les conclusions décrivent le contenu du jeu, pas le fonctionnement d'une vraie enseigne.

## 1. Contenu du dossier

```
J4_Analyse_Azure/
├── README.md                          ce fichier (J4-11)
├── analytics/
│   ├── notebooks/TP4_Retail_Intelligence.ipynb     calculs, analyses, visualisations, dépôt Azure
│   └── visualizations/                3 graphiques (PNG)
├── docs/
│   ├── analytics/                     documents UC-08
│   └── cloud/                         documents UC-07
└── azure/
    ├── architecture/azure-architecture.png         schéma d'architecture (J4-07)
    ├── demo/ca_par_mois/              fichier de démonstration et manifeste déposés dans Azure
    └── evidence/                      captures P01 à P17
```

## 2. Inventaire des livrables

| Code | Livrable | Fichier |
|---|---|---|
| J4-01 | Inventaire analytique | `docs/analytics/UC08_selection_donnees.md` |
| J4-02 | Dictionnaire des KPI | `docs/analytics/UC08_dictionnaire_KPI.md` |
| J4-03 | Analyses statistiques | `docs/analytics/UC08_stats_desc.md` et section « Stats descriptives » du notebook |
| J4-04 | Analyses métier (2 analyses) | `docs/analytics/UC08_analyses_metier.md` |
| J4-05 | Visualisations (3 graphiques) | `analytics/visualizations/v1_ca_par_magasin.png`, `v2_pareto_produits.png`, `v3_evolution_ca_par_jour.png` |
| J4-06 | Synthèse décisionnelle (4 constats) | `docs/analytics/UC08_constats.md` |
| J4-07 | Architecture Azure | `azure/architecture/azure-architecture.png` |
| J4-08 | Organisation ADLS Gen2 et rôle du HNS | `docs/cloud/UC07_organisation_ADLS.md`, `docs/cloud/UC07_role_HNS.md` |
| J4-09 | Sécurité | `docs/cloud/UC07_securite.md` |
| J4-10 | Preuves Azure | `docs/cloud/UC07_mise_en_oeuvre.md` (journal) et `azure/evidence/` |
| J4-11 | README J4 | ce fichier |

Documents complémentaires UC-07 : `UC07_composants_azure.md` (composants et relations), `UC07_ADF_Synapse.md` (étude ADF, Synapse, Spark pools, SQL), `UC07_correspondance_Azure_Open.md` (correspondance Azure / open source, coûts, limites).

## 3. Reproduire l'analyse (UC-08)

**Prérequis** : Python 3.10 ou plus, Java 17 ou plus (PySpark), et les jeux **Silver** (`store_sales`, `item`) et **Gold** du Jour 3 au format Parquet.

1. Créer l'environnement et installer les dépendances :
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python -m ipykernel install --user --name tp4-retail
   ```
2. Ouvrir `analytics/notebooks/TP4_Retail_Intelligence.ipynb` dans JupyterLab ou VS Code avec ce noyau.
3. Adapter dans la cellule de démarrage la variable `BASE` (dossier contenant `silver/` et `gold/`) et, dans la cellule « Style commun », la variable `OUT` (dossier de sortie des graphiques).
4. Exécuter les cellules **dans l'ordre**. Chaque section affiche ses résultats : vérification des volumes, statistiques, analyses par magasin et par produit, trois visualisations.
5. Comparer vos sorties avec les chiffres de la section 4 ci-dessous.

Choix de méthode à connaître :
- **CA net HT = colonne `_c20`** (`_c15` − coupons `_c19`) : définition du KPI de l'UC-01. Les jeux Gold sont calculés sur le **CA brut** (`_c15`) et ne servent que de contrôle.
- Le panier moyen se calcule en divisant par les **tickets**, pas par les lignes.
- Les évolutions se comparent en **CA par jour** : 2005 est partielle (fin au 13 décembre).
- `_c7` est interprété comme l'identifiant de magasin (position dans le schéma TPCx-BB) ; aucune table magasin n'est fournie.

## 4. Résultats principaux (jeu Silver `store_sales`, 667 579 lignes)

| Indicateur | Valeur |
|---|---|
| CA net HT total | 1 150 529 586,37 |
| CA brut total | 1 277 224 004,61 |
| Tickets | 89 100 |
| Panier moyen (net / tickets) | 12 912,79 |
| Période | 2001-01-01 → 2005-12-13 |
| Écart entre le premier et le dernier magasin | 5,22 % |
| Produits nécessaires pour 50 % du CA | 1 133 sur 17 820 (6,4 %) |
| CA net moyen par jour | environ 636 000, sans tendance |
| Music + Books | 71,87 % du CA, par effet du nombre de lignes |

Les quatre constats détaillés (observé, interprétation, limite, recommandation) sont dans `docs/analytics/UC08_constats.md`.

## 5. Ce qui a été réalisé sur Azure, et ce qui ne l'a pas été (UC-07)

| Élément | Statut |
|---|---|
| Groupe de ressources `rg-retail-intelligence-j4` | **Déployé** |
| Compte de stockage `stretailj4pa` : ADLS Gen2 (HNS activé), Standard, LRS, niveau Hot, accès anonyme désactivé, NFS v3 et SFTP désactivés | **Déployé** |
| Conteneur `retail-intelligence` et 7 répertoires racine (`bronze`, `silver`, `quarantine`, `gold`, `quality`, `logs`, `documentation`) | **Déployé** |
| Dépôt de `gold/ca_par_mois` (60 lignes, 2 182 octets) avec manifeste, empreinte SHA-256 vérifiée après téléchargement | **Déployé et vérifié** |
| Rôle de données *Storage Blob Data Contributor* attribué à l'étudiante, accès par identité Microsoft Entra (pas de clé de compte) | **Déployé** |
| Accès anonyme refusé (`PublicAccessNotPermitted`) | **Vérifié** |
| Azure Data Factory, Synapse, pools Spark, SQL serverless | **Étudié, non déployé** |
| Groupes Entra, ACL par zone, identités managées, Key Vault, restriction réseau | **Proposé, non déployé** (matrice de l'étape 5) |
| Dépôt des gros jeux (Silver, `ca_par_produit`) | **Non réalisé** (volontairement : inutile pour la démonstration) |
| Renommage de répertoire | **Non réalisé** |

Contraintes rencontrées : la création du compte en West Europe a été **refusée** par une politique de l'abonnement limitant les régions (`RequestDisallowedByAzure`) ; le compte a été créé dans une région autorisée (Italy North, d'après l'analyse des coûts). Le groupe de ressources est resté en West Europe, ce qui est sans conséquence. Le crédit restant n'est pas affiché dans le portail (abonnement géré par l'école) ; le coût a été relevé dans l'analyse des coûts : moins de 0,01 € à la date de la capture P16.

### Reproduire le déploiement Azure
1. Portail Azure : créer le groupe de ressources, puis le compte de stockage (Standard, LRS, **espace de noms hiérarchique coché dans l'onglet Avancé**, SFTP et NFS v3 décochés, accès anonyme désactivé), dans une région autorisée par l'abonnement.
2. Dans le compte, s'attribuer le rôle *Storage Blob Data Contributor* (Access control, IAM), puis créer le conteneur et les répertoires.
3. Générer le fichier de démonstration avec la cellule « Écriture Azure-ready » du notebook (crée `ca_par_mois.parquet` et `_manifest.json`), le déposer dans `gold/ca_par_mois`, le retélécharger et comparer les SHA-256.
4. **Nettoyage** : une fois les captures prises et l'accord du formateur obtenu, supprimer le groupe de ressources, ce qui supprime tout ce qu'il contient.

Règles suivies : aucun secret (clé de compte, jeton SAS, chaîne de connexion) dans le dépôt ni dans les captures ; un seul groupe de ressources dédié ; aucune ressource de calcul facturée créée.

## 6. Limites
- Données synthétiques : l'uniformité des magasins, des ventes dans le temps et la concentration des produits reflètent probablement le générateur (la documentation TPCx-BB indique que le magasin est tiré au hasard).
- Retours non déduits du CA, canal web absent du jeu analysé, marge non exploitée (74,29 % de lignes à perte).
- Déploiement Azure limité au stockage ; la comparaison avec l'open source est documentaire (étape 8 non concernée par le parcours A).
- Les offres et fonctionnalités Azure évoluent : à vérifier avant tout déploiement futur.
