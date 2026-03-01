# 🚀 Guide de Déploiement sur Fly.io

Ce guide explique comment déployer votre application Strava Flask sur Fly.io.

---

## 📋 Prérequis

1. **Compte Fly.io** : Créez un compte sur https://fly.io/
2. **Flyctl installé** : L'outil en ligne de commande Fly.io
3. **Git** : Pour gérer votre code

---

## 🔧 Installation de Flyctl

### macOS (avec Homebrew)
```bash
brew install flyctl
```

### Linux/macOS (avec curl)
```bash
curl -L https://fly.io/install.sh | sh
```

### Vérifier l'installation
```bash
flyctl version
```

---

## 🔐 Configuration Initiale

### 1. Connexion à Fly.io

```bash
flyctl auth login
```

Cela ouvrira votre navigateur pour vous connecter.

### 2. Vérifier la connexion

```bash
flyctl auth whoami
```

---

## 🚀 Déploiement de l'Application

### Étape 1 : Initialiser Git (si pas déjà fait)

```bash
cd /Applications/MAMP/htdocs/strava
git init
git add .
git commit -m "Initial commit - Application Strava Flask"
```

### Étape 2 : Configurer les Secrets (Variables d'Environnement)

⚠️ **IMPORTANT** : Ne commitez JAMAIS vos secrets dans Git !

```bash
# Définir vos identifiants Strava comme secrets
flyctl secrets set CLIENT_ID=149497
flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d
flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7
flyctl secrets set INDEX_URL=https://votre-domaine.com/index
```

### Étape 3 : Modifier le nom de l'app (optionnel)

Éditez `fly.toml` et changez le nom de l'application :

```toml
app = "mon-app-strava"  # Choisissez un nom unique
```

### Étape 4 : Lancer le déploiement

```bash
flyctl launch --no-deploy
```

Puis :

```bash
flyctl deploy
```

---

## 🌐 Accéder à votre Application

Une fois déployée, votre application sera accessible à :

```
https://strava-app.fly.dev
```

Ou avec votre nom personnalisé :

```
https://votre-nom-app.fly.dev
```

---

## 📊 Commandes Utiles

### Voir les logs en temps réel
```bash
flyctl logs
```

### Vérifier le statut de l'application
```bash
flyctl status
```

### Ouvrir l'application dans le navigateur
```bash
flyctl open
```

### Voir les secrets configurés
```bash
flyctl secrets list
```

### Mettre à jour un secret
```bash
flyctl secrets set CLIENT_SECRET=nouveau_secret
```

### Redéployer après modifications
```bash
git add .
git commit -m "Mise à jour"
flyctl deploy
```

### Voir la configuration de l'app
```bash
flyctl config show
```

### Augmenter les ressources (si nécessaire)
```bash
flyctl scale memory 512  # Augmenter la RAM à 512 MB
```

---

## 🐛 Dépannage

### L'application ne démarre pas

Vérifiez les logs :
```bash
flyctl logs
```

### Erreur de token Strava

Vérifiez que les secrets sont bien configurés :
```bash
flyctl secrets list
```

Reconfigurez si nécessaire :
```bash
flyctl secrets set REFRESH_TOKEN=votre_token
```

### L'application s'arrête automatiquement

C'est normal ! Fly.io arrête automatiquement les apps inactives (gratuit).
Elle redémarre automatiquement à la prochaine requête.

Pour garder au moins 1 instance active :
```bash
# Éditer fly.toml
min_machines_running = 1  # Au lieu de 0
```

Puis redéployer :
```bash
flyctl deploy
```

### Port incorrect

Assurez-vous que le port dans `fly.toml` correspond au port dans le Dockerfile (8080).

---

## 💰 Tarification Fly.io

### Plan Gratuit (Hobby)
- 3 machines partagées (256 MB RAM)
- 160 GB/mois de transfert
- Arrêt automatique des apps inactives
- **Parfait pour cette application !**

### Si vous dépassez le gratuit
- Environ 2-3 $/mois pour une petite app
- Facturé à l'usage

---

## 🔄 Workflow de Développement

### 1. Développement Local

```bash
cd /Applications/MAMP/htdocs/strava
./start.sh
# Testez sur http://127.0.0.1:5000
```

### 2. Commit des Changements

```bash
git add .
git commit -m "Description des modifications"
```

### 3. Déploiement sur Fly.io

```bash
flyctl deploy
```

### 4. Vérifier le Déploiement

```bash
flyctl logs
flyctl open
```

---

## 📝 Configuration Avancée

### Domaine Personnalisé

Si vous avez votre propre domaine :

```bash
flyctl certs add votre-domaine.com
```

Puis ajoutez les enregistrements DNS fournis par Fly.io.

### Plusieurs Régions

Pour déployer dans plusieurs régions (plus rapide) :

```bash
flyctl regions add cdg  # Paris
flyctl regions add lhr  # Londres
flyctl regions add iad  # USA Est
```

### Mise à l'Échelle Automatique

Éditez `fly.toml` :

```toml
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512  # Augmenter si nécessaire

[http_service]
  min_machines_running = 1
  max_machines_running = 3  # Augmenter si trafic élevé
```

---

## 🔒 Sécurité en Production

### 1. Ne jamais committer .env

Le fichier `.gitignore` est déjà configuré pour ignorer `.env`.

### 2. Utiliser les secrets Fly.io

Toujours utiliser `flyctl secrets set` pour les données sensibles.

### 3. Désactiver le mode debug

L'application utilise automatiquement `debug=False` en production.

### 4. HTTPS automatique

Fly.io fournit automatiquement un certificat SSL/TLS.

---

## 📦 Structure des Fichiers Fly.io

Fichiers nécessaires pour le déploiement :

```
/Applications/MAMP/htdocs/strava/
├── Dockerfile              ✅ Build de l'image Docker
├── .dockerignore          ✅ Fichiers à ignorer dans Docker
├── fly.toml               ✅ Configuration Fly.io
├── requirements.txt       ✅ Dépendances Python (avec gunicorn)
├── app.py                 ✅ Modifié pour production (PORT)
└── .gitignore            ✅ Protection des secrets
```

---

## 🎯 Checklist de Déploiement

Avant de déployer, vérifiez :

- [x] Dockerfile créé
- [x] fly.toml configuré
- [x] requirements.txt mis à jour avec gunicorn
- [x] app.py modifié pour la production
- [x] .dockerignore créé
- [x] .gitignore protège .env
- [ ] Flyctl installé
- [ ] Compte Fly.io créé
- [ ] Secrets configurés avec `flyctl secrets set`
- [ ] Git initialisé et code commité
- [ ] Nom de l'app personnalisé dans fly.toml
- [ ] Déploiement lancé avec `flyctl deploy`

---

## 🚀 Commande Rapide de Déploiement

Une fois tout configuré :

```bash
# 1. Aller dans le répertoire
cd /Applications/MAMP/htdocs/strava

# 2. Initialiser Git (si pas fait)
git init
git add .
git commit -m "Initial commit"

# 3. Se connecter à Fly.io
flyctl auth login

# 4. Configurer les secrets
flyctl secrets set CLIENT_ID=149497
flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d
flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7
flyctl secrets set INDEX_URL=https://votre-domaine.com/index

# 5. Déployer
flyctl launch --no-deploy  # Configure l'app
flyctl deploy              # Déploie l'app

# 6. Ouvrir l'app
flyctl open
```

---

## 📞 Support

### Documentation Fly.io
- https://fly.io/docs/
- https://fly.io/docs/languages-and-frameworks/python/

### Communauté
- Forum : https://community.fly.io/
- Discord : https://fly.io/discord

---

## 🎉 Succès !

Une fois déployée, votre application Strava sera accessible 24/7 sur Internet !

**URL de l'application** : https://strava-app.fly.dev (ou votre nom personnalisé)

Partagez-la avec vos amis sportifs ! 🏃‍♂️🚴‍♂️🏊‍♂️
