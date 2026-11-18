# Fiche de découverte de NiFi (UC-04, étape 6)

Livrable : **Fiche de découverte de NiFi**
Date : 17/11/2026

## 1. Environnement NiFi relevé

| Élément | Valeur | Source |
|---|---|---|
| Version de NiFi | 2.12.0 | `nifi-api-2.12.0.jar` dans `/opt/nifi/lib` |
| Installation | `/opt/nifi` (propriétaire `pauline`) | `environnement-j2.md` |
| Java | 21 (Hadoop utilise Java 17 ; Java 21 est le défaut du système) | `environnement-j2.md` |
| Adresse de l'interface | `https://localhost:8443/nifi` (écoute sur 127.0.0.1 uniquement) | `ss -ltn` |
| État de l'instance | UP (`Command Status [SUCCESS] HTTP 200`, 14:03:34), processus 278874 | `nifi.sh status` |
| Journaux | `/opt/nifi/logs/nifi-app.log` | |
| Dossiers de travail | `/data/nifi/input`, `/data/nifi/archive`, `/data/nifi/error` | |
| Sécurité | HTTPS avec certificat auto-signé ; identifiants générés au premier démarrage, non versionnés dans le dépôt | |
| Composants nécessaires à l'ingestion | `GetFile` (lecture locale) et `PutHDFS` (écriture HDFS) ; disponibilité de `PutHDFS` à confirmer dans l'interface | TP §12.3.4 |
| Services nécessaires | HDFS démarré (NameNode `hdfs://localhost:9000`), fichiers `core-site.xml` et `hdfs-site.xml` lisibles par NiFi | |

```bash
date
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
/opt/nifi/bin/nifi.sh status
ls /opt/nifi/lib | grep -i -E "hadoop|hdfs"
ls -l /data/nifi

Tue Nov 17 04:28:28 PM CET 2026

JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
NIFI_HOME=/opt/nifi

2026-11-17 16:28:29,525 INFO [main] org.apache.nifi.bootstrap.Command Application Process [278874] Command Status [SUCCESS] HTTP 200
2026-11-17 16:28:29,527 INFO [main] org.apache.nifi.bootstrap.Command Status: UP

total 12
drwxr-xr-x 2 pauline pauline 4096 Nov 17 13:07 archive
drwxr-xr-x 2 pauline pauline 4096 Nov 17 13:07 error
drwxr-xr-x 2 pauline pauline 4096 Nov 17 13:07 input
```

L’installation NiFi 2.12.0 fournie ne contenait pas les modules Hadoop : la recherche de hadoop ou hdfs dans /opt/nifi/lib ne renvoyait rien, ce qui rendait le processeur PutHDFS indisponible.
Les deux modules nécessaires, nifi-hadoop-libraries-nar et nifi-hadoop-nar, ont été téléchargés depuis Maven Central dans leur version 2.12.0, identique à celle de NiFi (nifi-framework-api-2.12.0), puis déposés dans /opt/nifi/extensions. La disponibilité de PutHDFS reste est confirmée dans par l'interface (cf P20).

### Commandes exécutées

Version de NiFi, pour choisir la version des modules :

```bash
ls /opt/nifi/lib | grep -o "nifi-framework-api-[0-9.]*" | head -1
```

Téléchargement dans le dossier des extensions :

```bash
cd /opt/nifi/extensions
wget https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-libraries-nar/2.12.0/nifi-hadoop-libraries-nar-2.12.0.nar
wget https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-nar/2.12.0/nifi-hadoop-nar-2.12.0.nar
ls -lh /opt/nifi/extensions
```

Vérification dans le journal de NiFi :

```bash
grep -iE "nifi-hadoop|Loaded extensions" /opt/nifi/logs/nifi-app.log | tail -5
```

### Résultats

| Contrôle | Résultat |
|---|---|
| Version de NiFi | 2.12.0 (`nifi-framework-api-2.12.0`) |
| Fichiers téléchargés | `nifi-hadoop-libraries-nar-2.12.0.nar` (57 Mo) et `nifi-hadoop-nar-2.12.0.nar` (17 Mo) |
| Chargement par NiFi | `Loaded extensions for org.apache.nifi:nifi-hadoop-libraries-nar:2.12.0` (16:33:59) et `…nifi-hadoop-nar:2.12.0` (16:34:05) |
| Interface NiFi | `PutHDFS` 2.12.0 (module `nifi-hadoop-nar`) apparaît dans Add Processor |

## 2. Les six concepts de NiFi et leur rôle dans le flux prévu GetFile → PutHDFS

| Concept | Définition | Rôle dans le flux GetFile → PutHDFS |
|---|---|---|
| **FlowFile** | Unité de donnée qui circule : un contenu (le fichier) et des attributs (nom, chemin, taille, date, identifiant unique) | Le fichier de test lu dans `/data/nifi/input` devient un FlowFile |
| **Processor** | Bloc qui effectue une opération sur les FlowFiles : lire, transformer, router, écrire | `GetFile` lit le dossier d'entrée ; `PutHDFS` écrit dans HDFS |
| **Connection** | Lien orienté entre deux processeurs, qui transporte les FlowFiles selon une relation (ex. `success`) et contient une file d'attente | La connexion `success` relie `GetFile` à `PutHDFS` |
| **Process Group** | Conteneur qui regroupe des processeurs pour organiser et isoler un flux | Le flux sera construit dans le groupe racine `NiFi Flow` du canevas (vide au 17/11/2026 à 16:26) |
| **Controller Service** | Service partagé et configurable, utilisé par plusieurs processeurs (connexion à une base, jeu de ressources, etc.) | Aucun n'est obligatoire pour ce flux : `PutHDFS` lit directement les fichiers de configuration Hadoop (`Hadoop Configuration Resources`) |
| **Provenance Repository** | Registre qui enregistre chaque événement subi par un FlowFile (réception, envoi, échec, avec heure et identifiant) | Permet de reconstituer le parcours du fichier de `/data/nifi/input` jusqu'à `/retail-lake/raw/nifi` (étape 11) |

Éléments complémentaires vus sur le canevas : la **Queue** (file d'attente visible sur une connexion, avec le nombre de FlowFiles en attente) et les compteurs de chaque processeur (entrées, sorties, octets).

## 3. Pourquoi NiFi après le dépôt manuel de l'UC-03

- Dans l'UC-03, `hdfs dfs -put` est manuel : un opérateur lance une commande pour chaque fichier.
- Avec NiFi, le transfert est automatique : un fichier qui arrive dans `/data/nifi/input` est pris en charge sans commande, avec une trace de provenance.
- La destination est distincte (`/retail-lake/raw/nifi`) pour comparer les deux méthodes sans écraser le dépôt de l'UC-03.

## 4. Contraintes et points d'attention

- NiFi n'écoute qu'en local (127.0.0.1:8443) : l'interface n'est pas exposée sur le réseau.
- `Keep Source File = false` dans `GetFile` : le fichier est retiré du dossier d'entrée après lecture. Seule une copie de travail doit y être placée ; l'original du kit reste dans `retail_project`.

