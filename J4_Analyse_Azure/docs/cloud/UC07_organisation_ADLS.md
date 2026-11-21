# UC-07 – Organisation ADLS Gen2

## 1. Arborescence proposée

Adaptée à nos données réelles (TPCx-BB, jeux Silver et Gold du Jour 3) et alignée sur le lac du Jour 2 (`bronze`, `silver`, `gold`, `quarantine`).

```
Compte de stockage : st<projet><suffixe>      (HNS activé = ADLS Gen2)
└── Conteneur : retail-intelligence
    ├── bronze/
    │   └── tpcxbb/
    │       ├── store_sales/        fichier brut .dat, jamais modifié
    │       ├── item/               fichier brut .dat
    │       └── date_dim/           fichier brut .dat (si présent dans l'inventaire du Jour 2)
    ├── silver/
    │   ├── store_sales/            Parquet nettoyé (667 579 lignes)
    │   └── item/                   Parquet nettoyé (17 820 lignes)
    ├── quarantine/
    │   ├── store_sales/            lignes rejetées (vide au TP3)
    │   └── item/
    ├── gold/
    │   ├── ca_par_mois/            60 lignes
    │   ├── ca_par_annee/           5 lignes
    │   ├── ca_par_categorie/       9 lignes
    │   └── ca_par_produit/         17 820 lignes
    ├── quality/                    rapports de contrôle
    ├── logs/                       journaux de traitement
    └── documentation/              dictionnaires, fiches
```

## 2. Règles par zone

| Zone | Fonction | Données qui peuvent y être déposées | Utilisateurs ou traitements | Règles de nommage | Conservation et traçabilité |
|---|---|---|---|---|---|
| `bronze/` | Garder les données **telles que reçues** | Fichiers `.dat` TPCx-BB, sans transformation | Écriture : ingestion (contrôlée). Lecture : data engineering | `bronze/<source>/<table>/<table>.dat`, minuscules | Jamais modifié ni écrasé ; empreinte SHA-256, taille et date de dépôt enregistrées dans un fichier `_manifest.json` du dossier |
| `silver/` | Données **nettoyées et typées**, une table par dossier | Parquet (compression snappy) | Écriture : traitements data engineering. Lecture : data engineering, analystes selon besoin | `silver/<table>/`, colonnes en minuscules, `_`, sans accent | Reconstructible depuis bronze ; règles de nettoyage décrites dans le dossier `documentation/` |
| `quarantine/` | Isoler les **lignes rejetées** par les contrôles | Parquet | Écriture : traitements. Lecture : data engineering | `quarantine/<table>/` | Conservée pour analyse ; la règle de rejet est notée dans `quality/` |
| `gold/` | Jeux **prêts pour l'analyse** | Agrégats Parquet | Écriture contrôlée : data engineering. Lecture : analystes | `gold/<indicateur>/`, nom lisible (`ca_par_mois`) | Chaque jeu a sa règle de calcul ; rappel : le Gold est calculé sur le **CA brut** (`_c15`), alors que le KPI UC-01 est le CA net |
| `quality/` | Rapports de contrôle qualité | CSV, Markdown | Écriture : traitements. Lecture : profils concernés | `quality/<AAAA-MM-JJ>_<controle>.<ext>` | Conservé pour l'audit |
| `logs/` | Journaux d'exécution | Texte, JSON | Écriture : traitements | `logs/<traitement>/<AAAA-MM-JJ>.log` | Durée de rétention proposée : 90 jours (à valider, car elle a un coût) |
| `documentation/` | Dictionnaires, fiches, schémas | Markdown, PDF | Lecture : tous | Nom explicite, sans espace | Versionnée avec Git ; la copie dans le lac est une copie de lecture |

