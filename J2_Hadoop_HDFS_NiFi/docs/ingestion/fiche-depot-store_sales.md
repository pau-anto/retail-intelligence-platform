# Fiche de dépôt et d'inventaire : store_sales.dat (UC-03, étape 4)

## 1. Contrôles avant dépôt

| Point demandé | Résultat |
|---|---|
| Chemin local | `retail_project/data/store_sales/store_sales.dat` |
| Nom et format | `store_sales.dat`, texte, séparateur `\|`, fins de ligne CRLF, sans en-tête |
| Taille | 92 764 700 octets |
| Structure | 667 579 lignes, 23 champs par ligne, colonnes identifiées par position (le kit ne fournit pas de noms) |
| Provenance | Kit TPCx-BB version 1.7.0, lot initial (`data/`), domaine ventes en magasin |
| Lisibilité | Fichier ouvert et lu en local (comptage des lignes et des champs réussi) |

## 2. Commande de dépôt

```bash
hdfs dfs -put "$BASE/retail_project/data/store_sales/store_sales.dat" /retail-lake/raw/tpcxbb/initial/
```

Dépôt réalisé le 17/11/2026 à 12:40 (horodatage HDFS). Une première tentative avec un chemin mal saisi (`…/intitial/`) a échoué ; elle est dans le tableau des erreurs.

## 3. Contrôles après dépôt

| Point demandé | Résultat | Commande |
|---|---|---|
| Le fichier apparaît dans HDFS | Oui, dans `raw/tpcxbb/initial` | `hdfs dfs -ls /retail-lake/raw/tpcxbb/initial` |
| Taille cohérente | 92 764 700 octets, identique à la source, 1 bloc (blocksize 134 217 728) | `hdfs dfs -ls` puis `hdfs dfs -du -h` |
| Accessible | Lecture possible (`-cat \| head`, `-get`) | `hdfs dfs -cat … \| head -n 3` |
| Chemin de destination correct | `/retail-lake/raw/tpcxbb/initial/store_sales.dat` | `hdfs dfs -ls -R /retail-lake` |
| Source originale conservée | Oui, `-put` copie et ne supprime pas ; fichier local toujours présent | `ls -l` sur le chemin local |
| Intégrité | SHA-256 de la copie récupérée par `-get` identique à celui de la source | `sha256sum` |

SHA-256 : `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e`

## 4. Inventaire mis à jour

Dans la matrice d'inventaire, la ligne `store_sales.dat` passe à :

| Champ | Valeur |
|---|---|
| Statut | **Déposé dans HDFS** (les 35 autres fichiers restent non déposés) |
| Destination HDFS | `/retail-lake/raw/tpcxbb/initial/store_sales.dat` |
| Date de dépôt | 17/11/2026 12:40 |
| Méthode | `hdfs dfs -put` |
| Intégrité vérifiée | Oui, SHA-256 identique |

## 5. Preuves jointes

| Preuve | Contenu de la capture | Fichier |
|---|---|---|
| Après dépôt | `hdfs dfs -ls -R /retail-lake` : `store_sales.dat` présent dans `raw/tpcxbb/initial`, 92 764 700 octets, 12:40 | `preuves/hdfs/P04_hdfs_arborescence-finale.png` |
| Taille | `date; hdfs dfs -du -h /retail-lake` : 88,5 Mo dans `raw` | `preuves/hdfs/P05_hdfs_du-h_retail-lake.png` |
| Source conservée, lecture, intégrité | `ls -l` du fichier local (92 764 700 octets, inchangé), `hdfs dfs -cat … \| head -n 2`, SHA-256 identique pour la source et la copie HDFS | `preuves/hdfs/P17_hdfs_lecture_store-sales.png` |
| Inventaire local avant dépôt | 36 fichiers, 987 Mo | `preuves/hdfs/P13_sources_inventaire_local-kit.png` |
| Commande `-put` et son résultat | commande n° 184 : dépôt réussi à 12:40 | `tests_hdfs/historique-commandes-hdfs.md` |
| Nombre de lignes | 667 579 lignes relues depuis HDFS | `tests_hdfs/rapport-verification.txt` |

Le message `cat: Unable to write to output stream` visible sur P17 est sans gravité : `head` ferme le tube avant la fin de la lecture (erreur n° 6 du tableau des erreurs).
