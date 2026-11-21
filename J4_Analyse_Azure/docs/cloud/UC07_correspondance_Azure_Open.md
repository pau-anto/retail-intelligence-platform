# UC-07 – Correspondance Azure / open source, coûts et limites

## 1. Tableau de correspondance

| Fonction | Rôle fonctionnel | Composant retenu dans notre parcours | Composant non déployé | Limites de l'équivalence |
|---|---|---|---|---|
| **Stockage Data Lake** | Conserver les fichiers des zones bronze, silver et gold et contrôler leur accès | **ADLS Gen2** (compte `stretailj4pa`, HNS activé) pour l'échantillon ; **disque local** pour le lac complet (Jours 2 et 3) | MinIO (stockage objet compatible S3) | Un disque local n'a ni Entra ID, ni RBAC, ni ACL, ni redondance. MinIO imite l'API S3 mais n'offre pas le modèle de permissions d'ADLS Gen2. Seul `gold/ca_par_mois` est dans Azure. |
| **Tables analytiques** | Organiser des fichiers en tables fiables (schéma, évolution) | **Fichiers Parquet** (silver et gold) | Format de table du lakehouse côté Azure ; Apache Iceberg côté open source | Du Parquet seul ne gère pas les transactions ni l'évolution des tables. Iceberg est un **format de table**, pas un moteur de calcul ni un équivalent de Synapse. |
| **Traitement distribué** | Nettoyer, transformer et agréger de gros volumes | **PySpark 4.3.0 en local** (`local[*]`) | Pool Spark de Synapse | En mode local, Spark tourne sur **une seule machine** : le code est le même, mais il n'y a pas de véritable distribution. 667 579 lignes ne justifient pas un cluster. |
| **Requêtes SQL** | Interroger les données en SQL | **DataFrames PySpark** et notebook | Synapse SQL (serverless ou dédié) ; Trino ou Spark SQL côté open source | Spark local sert à explorer, mais il n'y a pas de point d'accès SQL partagé pour plusieurs utilisateurs. Trino complète Spark sans remplacer à lui seul Synapse. |
| **Catalogue et métadonnées** | Décrire les jeux : schémas, emplacement, propriétaire, règles | **Aucun catalogue central** : schémas Parquet, dictionnaires, README, `_manifest.json` | Catalogue des services Azure ; Hive Metastore ou Nessie côté open source | La découverte des jeux est manuelle et la cohérence dépend de la discipline documentaire. |
| **Intégration et orchestration** | Déplacer les données et enchaîner les traitements | **Apache NiFi** (Jour 2) pour l'ingestion locale ; exécution manuelle des notebooks ; **dépôt manuel** dans le portail Azure | Azure Data Factory ; Airflow ou scripts planifiés | Rien n'est planifié, ni relancé automatiquement en cas d'échec ; l'enchaînement repose sur l'exécution manuelle. |
| **Visualisation** | Présenter les résultats aux utilisateurs | **Matplotlib dans Jupyter** (3 graphiques) | Power BI ; Superset | Graphiques statiques : pas de tableau de bord interactif, ni de rafraîchissement automatique. |
| **Identités et permissions** | Savoir qui accède à quoi | **Microsoft Entra ID** et **RBAC** (rôle *Storage Blob Data Contributor*), accès anonyme désactivé ; ACL du conteneur **consultée** | Groupes Entra, ACL par zone, identités managées ; comptes locaux et droits système côté open source | Un seul utilisateur réel : la séparation des profils est une **proposition** (étape 5), pas une mise en œuvre. |
| **Environnement d'exécution** | Fournir le cadre dans lequel tourne le code | **Poste local** (Jupyter, environnement Python) + service de stockage managé Azure | Docker ou Podman, machine virtuelle ; services cloud managés (Synapse) | La reproductibilité dépend des versions installées (`requirements.txt`) ; un conteneur la rendrait plus fiable. |

## 2. Pourquoi plusieurs composants open source pour remplacer Synapse

Synapse Analytics réunit, dans **un seul espace de travail**, un moteur Spark, des capacités SQL, des pipelines d'intégration et une interface web, avec une sécurité et une supervision communes. Reproduire cela en open source demande d'**assembler** des briques complémentaires :

| Capacité de Synapse | Brique open source possible |
|---|---|
| Calcul Spark | Apache Spark / PySpark |
| Requêtes SQL | Trino ou Spark SQL |
| Format et métadonnées des tables | Iceberg avec un catalogue (Nessie, Hive Metastore) |
| Pipelines et planification | Airflow (ou NiFi pour l'ingestion) |
| Stockage | Disque ou MinIO |
| Interface d'exploration et tableaux de bord | Jupyter, Superset |

Conséquences : plus de composants à installer, à relier, à sécuriser et à maintenir soi-même ; les versions doivent rester compatibles entre elles ; et la sécurité et la supervision ne sont plus unifiées. En contrepartie, chaque brique est remplaçable, sans abonnement cloud ni dépendance à un fournisseur. Aucune de ces briques n'est une copie exacte d'un service Azure.

## 3. Analyse des coûts

### 3.1 Ce qui a été créé dans Azure
| Ressource | Configuration | Coût attendu |
|---|---|---|
| Compte de stockage ADLS Gen2 | Standard, LRS, niveau Hot, HNS activé | Très faible : un fichier de 2 Ko et un manifeste ; stockage et quelques opérations |
| Groupe de ressources | Un seul, dédié | Aucun coût propre |
| Rôle et ACL | Attribution de rôle, lecture d'ACL | Aucun coût |

**Coût mesuré** (analyse des coûts de l'abonnement) : `<0.0.1€`. Les coûts s'affichent avec un délai d'au moins plusieurs heures.

### 3.2 Ressources à risque volontairement **non** créées
- Pool SQL dédié Synapse et pool Spark (facturés tant qu'ils sont actifs).
- Espace de travail Synapse et pipeline Data Factory.
- Machines virtuelles, disques, adresses IP publiques.
- SFTP sur le compte de stockage (facturé à l'heure) : **désactivé** à la création.

## 4. Contraintes d'accès rencontrées
- **Politique de régions** sur l'abonnement : le déploiement en West Europe a été refusé (`RequestDisallowedByAzure`) ; régions autorisées relevées : Italy North, Denmark East, Switzerland North, Poland Central, Austria East.
- **Crédit non consultable** dans le portail : abonnement géré par l'école ; le contrôle repose sur l'analyse des coûts.
- **Rôle de données nécessaire** : le rôle Owner ne suffit pas pour lire ou écrire les fichiers, il a fallu s'attribuer *Storage Blob Data Contributor*.
- **Délai de facturation** : les coûts d'une ressource neuve n'apparaissent pas immédiatement.

## 5. Limites générales
- Le déploiement réel se limite au stockage ; Data Factory, Synapse, Spark pools, ACL par zone et identités managées sont étudiés ou proposés.
- La comparaison avec l'open source est **documentaire** : aucun composant open source n'a été installé pour ce parcours.
- Les coûts de ressources non créées ne sont pas chiffrés.
- Les données du projet sont synthétiques et de faible volume : les conclusions sur la performance ne s'extrapolent pas à des volumes réels.
- Les offres et fonctionnalités Azure évoluent ; à vérifier avant tout déploiement futur.