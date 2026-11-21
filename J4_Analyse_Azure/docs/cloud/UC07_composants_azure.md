# UC-07 – Composants Azure et relations

**Parcours choisi : A – Azure.** Compte Azure for Students vérifié, crédit de 100 $, sans carte bancaire associée.

## 1. Les composants et leur rôle dans le projet

| Composant | Rôle général | Rôle dans Retail Intelligence Platform | 
|---|---|---|---|
| **Abonnement Azure** | Contrat de facturation et périmètre de gestion des ressources | Contient toutes nos ressources et porte le crédit de 100 $ | 
| **Groupe de ressources** | Conteneur logique qui regroupe des ressources liées | Regroupe tout le projet (compte de stockage…) ; sa suppression nettoie tout en une fois |
| **Compte de stockage** | Ressource de stockage Azure, point d'entrée (nom unique mondial) | Héberge le data lake | 
| **Conteneur** | Racine de rangement dans un compte de stockage | Un conteneur pour le projet (ex. `retail-intelligence`) qui porte les zones | 
| **Azure Data Lake Storage Gen2 (ADLS Gen2)** | Compte de stockage avec le Hierarchical Namespace activé, conçu pour l'analytique | Stocke Bronze, Silver et Gold sous forme de fichiers Parquet |
| **Hierarchical Namespace (HNS)** | Système de fichiers hiérarchique : vrais répertoires, opérations sur les chemins, ACL | Permet de gérer les droits et les déplacements par zone (voir étape 3) | 
| **Microsoft Entra ID** | Annuaire d'identités et service d'authentification | Identifie les personnes et les traitements qui accèdent au lac | 
| **Azure RBAC** | Droits par rôle, attribués à une identité sur un périmètre | Donne à chaque profil son niveau d'accès global (lecture, écriture, gestion) | 
| **ACL (listes de contrôle d'accès)** | Droits fins sur les répertoires et fichiers d'un compte à HNS | Affine l'accès zone par zone (ex. Gold lisible par les analystes, Bronze fermé) | 


## 2. Comment ces composants s'emboîtent

```
Locataire Microsoft Entra ID          ← qui sont les identités ?
        │
Abonnement Azure                      ← qui paie, quel périmètre
        │
Groupe de ressources                  ← regroupe les ressources du projet
        │
Compte de stockage (HNS activé = ADLS Gen2)
        │
Conteneur  « retail-intelligence »
        │
Répertoires  bronze/ silver/ gold/ …   ← ACL possibles ici (grâce au HNS)
        │
Fichiers  (Parquet, etc.)
```

À retenir :
- **Entra ID** répond à « qui est-ce ? » ; **RBAC** et **ACL** répondent à « que peut-il faire ? ».
- Le HNS se choisit à la **création** du compte de stockage : sans lui, le compte est un stockage d'objets classique, et pas un ADLS Gen2.
- Un seul compte de stockage peut contenir plusieurs conteneurs ; ici un seul suffit.
- Supprimer le groupe de ressources supprime tout ce qu'il contient : c'est notre moyen de nettoyage en fin de TP.