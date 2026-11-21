# UC-07 – Le rôle du Hierarchical Namespace (HNS)

## 1. En une phrase
Le Hierarchical Namespace transforme un compte de stockage Azure (stockage d'objets) en un **système de fichiers** avec de vrais répertoires. C'est ce qui fait d'un compte de stockage un **ADLS Gen2**.

## 2. Organisation hiérarchique des répertoires

**Sans HNS (espace de noms plat).** Le conteneur contient des objets, chacun identifié par un nom unique. Le nom `silver/store_sales/part-0.parquet` est une seule chaîne de caractères : les `/` sont des caractères comme les autres, et les « dossiers » ne sont que des préfixes d'affichage. Un dossier vide n'existe pas.

**Avec HNS.** Le service gère une vraie arborescence :

```
retail-intelligence            (conteneur = racine du système de fichiers)
└── silver                     (répertoire)
    └── store_sales            (répertoire)
        └── part-0.parquet     (fichier)
```

Chaque répertoire et chaque fichier est une entrée du service, avec ses propres métadonnées (propriétaire, droits, dates). Un répertoire vide peut exister.

## 3. Opérations sur les chemins

| Opération | Avec HNS | Sans HNS |
|---|---|---|
| Renommer ou déplacer un répertoire | **Une seule opération** sur le répertoire, atomique (tout ou rien) | Copie de chaque objet puis suppression de l'ancien : proportionnelle au nombre de fichiers, non atomique |
| Supprimer un répertoire | Une seule opération | Suppression objet par objet |
| Créer un répertoire vide | Possible | Impossible (un préfixe n'existe que s'il y a un objet) |
| Lister le contenu d'un répertoire | Lecture d'un répertoire réel | Recherche des objets dont le nom commence par le préfixe |

**Intérêt pour Spark.** Un job Spark écrit d'abord ses fichiers dans un répertoire temporaire, puis le **renomme** à la fin pour publier le résultat. Avec HNS, ce renommage est une opération de métadonnées, rapide et sans état intermédiaire visible : un lecteur ne voit jamais un jeu Silver à moitié écrit. Sans HNS, le renommage est une copie complète, plus lente et sujette aux états incohérents en cas d'échec.

## 4. Permissions au niveau des répertoires et des fichiers

Avec HNS, on peut poser des **ACL de type POSIX** sur chaque répertoire et chaque fichier :
- **Trois droits :** lecture (r), écriture (w), exécution (x). Sur un répertoire, `x` permet de le **traverser** : il faut `x` sur chaque répertoire du chemin, racine du conteneur comprise, pour atteindre un fichier.
- **Trois catégories :** le propriétaire, le groupe propriétaire, les autres ; des entrées nommées supplémentaires peuvent viser des identités Entra ou des groupes précis (nombre limité par ACL).
- **ACL d'accès et ACL par défaut :** l'ACL d'accès s'applique à l'élément lui-même ; l'ACL par défaut, posée sur un répertoire, est copiée sur les nouveaux fichiers et sous-répertoires qui y sont créés. C'est ce qui évite de reposer les droits à chaque nouveau dépôt.

**Articulation avec RBAC.** Les rôles RBAC de données (famille *Storage Blob Data …*) sont évalués en premier : s'ils autorisent l'action, les ACL ne sont pas consultées. Les ACL ne jouent donc que lorsque l'identité n'a pas de rôle de données suffisant. Pour restreindre finement par zone, on accorde peu de rôles larges et on s'appuie sur les ACL.

## 5. Différences d'usage avec un stockage objet sans HNS

| Critère | ADLS Gen2 (HNS activé) | Stockage Blob sans HNS |
|---|---|---|
| Modèle | Système de fichiers hiérarchique | Objets dans un espace plat |
| Répertoires | Réels | Simulés par préfixes |
| Renommage / suppression de dossier | Atomique, une opération | Copie et suppression objet par objet |
| Permissions | RBAC + ACL par répertoire et fichier | RBAC et jetons au niveau compte ou conteneur |
| Point d'accès pour l'analytique | Pilote ABFS (`abfss://…dfs.core.windows.net`), adapté à Spark et Hadoop | Accès blob classique, moins adapté aux jobs qui renomment |
| Usage typique | Data lake, traitements Spark, zones Bronze / Silver / Gold | Médias, sauvegardes, fichiers déposés sans structure |
| Mise en place | À choisir à la **création** du compte | Par défaut |

Un compte avec HNS reste accessible aussi par les interfaces blob classiques, ce qui permet à des outils existants de continuer à fonctionner.