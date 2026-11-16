# Petit Cocon sur Coolify

Ajoute l’archive serveur officielle `Petit-Cocon-serveur-3.0.0.zip` à la racine du dépôt. Le build extrait les fichiers, adapte le formulaire et teste la création de deux carnets sans code de création.

Dans Coolify, sélectionne **Docker Compose** avec `/compose.yaml`, puis associe le domaine HTTPS `cocon.app.donosoft.ovh` au service `cocon` sur le port interne `8080`. Le volume `cocon-data` stocke les comptes et les carnets. La variable facultative `COCON_MAX_FAMILIES` règle le nombre de carnets, fixé à 20 par défaut.

Une fois le service disponible, ouvre `https://cocon.app.donosoft.ovh` et choisis **Plus → Entre parents → Créer mon compte**. Le compte créé sur le site permet de se connecter dans l’APK Android 3.0.0.
