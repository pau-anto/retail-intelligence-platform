# Erreur contrôlée NiFi

## 1. Test réalisé

Dans `GetFile`, la propriété **Input Directory** a été changée de `/data/nifi/input` en `/data/nifi/inexistant`, un dossier qui n'existe pas. Aucun droit n'a été modifié, et rien n'a été touché dans HDFS.

## 2. Comportement observé

- `GetFile` passe à l'état **invalide** : une icône d'avertissement jaune remplace le carré rouge (arrêté).
- Le message affiché au survol est :
  `'Input Directory' validated against '/data/nifi/inexistant' is invalid because Directory does not exist`
- Le flux ne peut pas démarrer tant que le processeur est invalide : aucun fichier n'est lu et rien n'est envoyé à HDFS.
- Recherche dans le journal : `grep -i "inexistant" /opt/nifi/logs/nifi-app.log | tail -n 5` (17:14:40) ne renvoie **aucune ligne**. L'erreur est détectée par la validation du processeur, avant toute exécution : NiFi ne l'écrit donc pas dans `nifi-app.log`.

## 3. Comment l'échec est identifiable

| Où | Ce qu'on voit |
|---|---|
| Canevas | Icône d'avertissement sur `GetFile`, et message au survol qui nomme la propriété fautive, la valeur et la cause |
| Journal `nifi-app.log` | Rien : c'est une erreur de configuration, pas d'exécution |
| Provenance | Rien : aucun FlowFile n'a été créé |

Cette erreur est donc visible uniquement sur le canevas. Pour une erreur qui laisse une trace dans le journal et la provenance, il faut une erreur d'exécution (par exemple un conflit de nom dans HDFS avec `PutHDFS`), qui n'a pas été provoquée ici.

## 4. Correction

Input Directory a été rétabli à `/data/nifi/input` et validé avec Apply. L'avertissement disparaît et `GetFile` redevient valide (arrêté).

## 5. Preuves

| Capture | Contenu |
|---|---|
| `P31_nifi_erreur-getfile-dossier-inexistant.png` | Avertissement sur `GetFile` avec le message d'erreur |
| `P32_nifi_erreur-journal-vide.png` | `grep` sans résultat dans `nifi-app.log` |
