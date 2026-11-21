# UC-07 – Mise en œuvre réelle sur Azure (journal de réalisation)

**Parcours A – Azure.** Ce document est le **journal** de ce qui a été réellement exécuté le **20/11/2026**. Rien n'y est déclaré sans preuve ; les points non réalisés sont indiqués comme tels.

## 1. Contexte

| Élément | Valeur relevée |
|---|---|
| Abonnement | Azure for Students, état **Actif**, plan « Azure Plan » |
| Annuaire | Ecole IPSSI |
| Rôle de l'étudiante sur l'abonnement | Owner |
| Crédit restant | **Non affichable dans le portail** (abonnement géré par l'école) ; aucune valeur de crédit n'est donc déclarée comme vérifiée |
| Groupe de ressources | `rg-retail-intelligence-j4`, région West Europe |
| Compte de stockage | `stretailj4pa` |
| Région du compte de stockage | `Italy North` |
| Conteneur | `retail-intelligence` |
| Accès aux données | Microsoft Entra (compte étudiant), jamais la clé d'accès |

## 2. Déroulement réel

| 20/11/2026 | Action | Résultat |
|---|---|---|
| — | Contrôle de l'abonnement | Azure for Students, Actif, Owner |
| — | Création du groupe de ressources `rg-retail-intelligence-j4` | Créé en West Europe |
| — | Première tentative de création du compte `stretailj4pa` en West Europe | **Refusée** : `RequestDisallowedByAzure` (politique de l'abonnement limitant les régions) |
| 17:16:47 | Création du compte de stockage dans une région autorisée | Déploiement réussi (« Your deployment is complete ») |
| — | Vérification du compte | HNS **Enabled**, accès blob anonyme **Disabled**, NFS v3 **Disabled**, SFTP **Disabled**, niveau Hot, suppression récupérable 7 jours (conteneurs et blobs) ; point de terminaison Data Lake Storage `https://stretailj4pa.dfs.core.windows.net/` |
| — | Attribution du rôle **Storage Blob Data Contributor** à l'étudiante, portée : le compte de stockage | Rôle visible dans Access control (IAM) |
| — | Création du conteneur `retail-intelligence` | Créé |
| 17:29–17:30 | Création des répertoires `bronze`, `silver`, `quarantine`, `gold`, `logs`, `documentation`, puis `gold/ca_par_mois` (à 17:30:36) | Créés, méthode d'authentification : Microsoft Entra user account |
| — | Création du répertoire `quality` | Créé (7e répertoire racine) |
| 17:33:49 | Dépôt de `ca_par_mois.parquet` et `_manifest.json` dans `gold/ca_par_mois` | 2,13 KiB (2 182 octets) et 256 octets |
| 17:37 | Accès sans identité (navigation privée) à l'URL du fichier | **Refusé** : `PublicAccessNotPermitted` |
| — | Téléchargement du fichier et recalcul du SHA-256 | **Identique** à celui du manifeste |

## 3. Politique de région (observation)

L'abonnement impose une politique qui limite les régions de déploiement. Régions autorisées relevées : **Italy North, Denmark East, Switzerland North, Poland Central, Austria East**. Le groupe de ressources (simple étiquette de localisation) peut rester en West Europe : un compte de stockage peut se trouver dans une autre région que son groupe.

## 4. Intégrité du fichier de démonstration

| Élément | Valeur |
|---|---|
| Fichier | `gold/ca_par_mois/ca_par_mois.parquet` (60 lignes, extrait Gold calculé sur le **CA brut** `_c15`) |
| Taille locale | 2 182 octets |
| SHA-256 du manifeste | `1ef94fcaa57cdb94d852802e2c0bb89a846720a07001eff7619b5bb3cb9b61ff` |
| SHA-256 du fichier téléchargé depuis Azure | `1ef94fcaa57cdb94d852802e2c0bb89a846720a07001eff7619b5bb3cb9b61ff` — comparaison affichée `Identiques : True` |

