# UC-07 – Sécurité et gestion des accès

**Parcours A – Azure.** Ce document sépare ce qui a été **réalisé** dans Azure de ce qui est **proposé** (non déployé : abonnement géré par l'école, pas de création de groupes ni d'identités supplémentaires).

## 1. Principes retenus

- **Moindre privilège** : chaque profil reçoit le droit minimal nécessaire, par zone, jamais « tout le compte pour simplifier ».
- **Séparation des rôles** : ceux qui ingèrent ne publient pas en Gold ; ceux qui analysent ne lisent pas le brut.
- **Identités avant secrets** : accès par identité Microsoft Entra ; les clés de compte et jetons SAS ne sont pas utilisés.
- **Accès par groupes** plutôt que par personnes : une ACL est limitée en nombre d'entrées, et un groupe se met à jour sans retoucher les répertoires.
- **Traçabilité** : le manifeste de dépôt et les journaux (`logs/`) permettent de savoir qui a déposé quoi et quand.

## 2. Matrice des droits (proposition)

Zones : `bronze/`, `silver/`, `gold/`, plus `quarantine/`, `logs/`, `documentation/`.
Notation : **L** = lecture, **E** = écriture, **—** = aucun accès. Une lecture de répertoire suppose le droit de le traverser (voir §4).

| Profil | Bronze | Silver | Gold | Quarantine | Logs | Documentation |
|---|---|---|---|---|---|---|
| **Équipe ingestion** | E contrôlée (uniquement `bronze/<source>/`) | L limitée (contrôle de dépôt) | — par défaut | — | E (`logs/ingestion/`) | L |
| **Équipe Data Engineering** | L / E selon besoin | L / E | E contrôlée | L / E | L / E | L / E |
| **Analyste métier** | — par défaut | L selon besoin (jeux désignés) | L | — | — | L |
| **Traitement automatisé** (identité de service, proposé) | L | L / E (`silver/`) | E (`gold/`) | E | E | L |
| **Administrateur** | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation | Gestion selon habilitation |

Remarques :
- « E contrôlée » signifie limitée à un sous-répertoire précis, avec dépôt tracé par le manifeste ; une écriture sur un répertoire permet aussi d'en supprimer le contenu, d'où la suppression récupérable (7 jours) activée sur le compte.
- L'administrateur gère les ressources et les droits, mais n'a pas d'accès permanent aux données : un rôle de données élevé est accordé à la demande et pour une durée limitée.
- Un traitement automatisé (Spark, Data Factory) doit utiliser sa **propre identité**, jamais celle d'une personne.

## 3. Mise en œuvre proposée (non déployée)

| Profil | Groupe Entra proposé | Droits sur le conteneur |
|---|---|---|
| Équipe ingestion | `grp-retail-ingestion` | ACL `--x` sur la racine ; `rwx` sur `bronze/tpcxbb/` ; `r-x` sur `silver/` ; `rwx` sur `logs/ingestion/` |
| Équipe Data Engineering | `grp-retail-dataeng` | ACL `rwx` sur `bronze/`, `silver/`, `quarantine/`, `logs/` ; `rwx` sur `gold/` (écriture contrôlée) |
| Analyste métier | `grp-retail-analyst` | ACL `--x` sur la racine ; `r-x` sur `gold/` et sur les jeux Silver désignés ; `r-x` sur `documentation/` |
| Traitement automatisé | identité managée (proposée) | `r-x` sur `bronze/` ; `rwx` sur `silver/`, `gold/`, `quarantine/`, `logs/` |
| Administrateur | rôles Azure (gestion) | Rôle de gestion sur le groupe de ressources ; rôle de données à la demande |

Choix de conception : les profils reçoivent des **ACL** par zone et **aucun rôle de données large** au niveau du compte, parce qu'un rôle de données évalué au niveau du compte prime sur les ACL et rendrait la séparation par zone inopérante.

## 4. RBAC, ACL, identités, secrets : quatre notions distinctes

| Notion | Question à laquelle elle répond | Exemple dans ce projet |
|---|---|---|
| **Identité et authentification** | Qui est-ce, et comment le prouve-t-il ? | Compte Microsoft Entra de l'étudiante ; identité managée proposée pour les traitements |
| **Azure RBAC** | Quel rôle cette identité a-t-elle, et sur quel périmètre ? | Rôle *Storage Blob Data Contributor* sur le compte de stockage (réalisé) |
| **ACL du Data Lake** | Quels droits (r, w, x) sur ce répertoire ou ce fichier ? | ACL de `gold/` (proposé) ; ACL de la racine du conteneur (observée) |
| **Secrets** | Quelles informations permettent d'accéder sans identité ? | Clés du compte, chaînes de connexion, jetons SAS : **non utilisés** |

Points d'attention :
- **Ordre d'évaluation** : si un rôle RBAC de données autorise l'action, les ACL ne sont pas consultées.
- **Traversée** : pour lire `gold/ca_par_mois/…`, une identité doit avoir le droit d'exécution (`x`) sur la racine du conteneur et sur chaque répertoire du chemin. L'écran de gestion des ACL le rappelle : les droits de lecture et d'écriture ne fonctionnent que si l'identité a aussi l'exécution sur tous les répertoires parents, racine comprise.
- **Rôles de gestion ≠ rôles de données** : un propriétaire de l'abonnement gère les ressources mais n'a pas de droit de données par défaut. Attention toutefois : un rôle de gestion étendu (Owner, Contributor) permet d'obtenir les clés du compte, et donc d'accéder aux données si l'accès par clé est autorisé.
- **Secrets** : jamais dans le code, un README, Git ni une capture. Pour un traitement, préférer une identité managée ; sinon stocker le secret dans Azure Key Vault ou dans une variable d'environnement non versionnée, avec rotation.

## 5. Risques résiduels et recommandations

| Risque | État actuel | Recommandation |
|---|---|---|
| Accès réseau public ouvert au compte (accès anonyme désactivé) | Réseau public activé | Restreindre aux réseaux ou adresses autorisés, ou utiliser un point de terminaison privé |
| Accès par clé de compte toujours autorisé | Activé (valeur par défaut) | Le désactiver une fois les accès par identité validés |
| Rôle de données large au niveau du compte | Attribué à l'étudiante pour la démonstration | Restreindre au conteneur ; utiliser des groupes |
| Pas de journalisation des accès aux données | Non configurée | Activer les journaux de diagnostic vers `logs/` ou un espace de supervision |
| Droits « selon habilitation » de l'administrateur | Non automatisés | Accès à la demande et limité dans le temps, avec validation |
| Suppression par un profil en écriture | Atténuée par la suppression récupérable | Verrou sur le groupe de ressources et sauvegarde des zones critiques |

## 6. Limites
- La matrice est une **proposition** : aucun groupe ni ACL nominative n'a été créé dans l'abonnement de l'école.
- Les captures ne prouvent que les éléments marqués « réalisé » ou « observé ».
- Les durées et pratiques (accès à la demande, rotation des secrets) sont des recommandations, pas des règles imposées par Azure.
- Les données du projet sont synthétiques : les enjeux de confidentialité (données personnelles, conformité) sont présentés comme principes et ne sont pas évalués sur des données réelles.