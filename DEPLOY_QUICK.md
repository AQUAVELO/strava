# 🚀 Déploiement Rapide sur Fly.io

## ✅ Fichiers Créés pour le Déploiement

Tous les fichiers nécessaires ont été créés :

- ✅ `Dockerfile` - Configuration Docker
- ✅ `.dockerignore` - Exclusions Docker
- ✅ `fly.toml` - Configuration Fly.io
- ✅ `requirements.txt` - Mis à jour avec gunicorn
- ✅ `app.py` - Modifié pour la production
- ✅ `deploy_flyio.sh` - Script de déploiement automatique

## 🎯 Déploiement en 5 Minutes

### Étape 1 : Installer Flyctl

```bash
# macOS avec Homebrew
brew install flyctl

# Ou avec curl (Linux/macOS)
curl -L https://fly.io/install.sh | sh
```

### Étape 2 : Se Connecter à Fly.io

```bash
flyctl auth login
```

### Étape 3 : Configurer les Secrets

```bash
flyctl secrets set CLIENT_ID=149497
flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d
flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7
flyctl secrets set INDEX_URL=https://votre-domaine.com/index
```

### Étape 4 : Déployer avec le Script

```bash
./deploy_flyio.sh
```

**Ou manuellement** :

```bash
flyctl launch --no-deploy
flyctl deploy
```

### Étape 5 : Accéder à l'Application

```bash
flyctl open
```

Votre app sera accessible sur : `https://strava-app.fly.dev`

---

## 📋 Commandes Utiles

```bash
# Voir les logs en temps réel
flyctl logs

# Vérifier le statut
flyctl status

# Ouvrir l'app
flyctl open

# Voir les secrets
flyctl secrets list

# Redéployer
flyctl deploy
```

---

## 🐛 Résolution de Problèmes

### Erreur : "Could not find Dockerfile"

✅ **Résolu** - Le Dockerfile a été créé automatiquement.

### L'application ne démarre pas

Vérifiez les logs :
```bash
flyctl logs
```

### Erreur de token Strava

Reconfigurez les secrets :
```bash
flyctl secrets set REFRESH_TOKEN=votre_nouveau_token
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez : **[DEPLOY_FLYIO.md](DEPLOY_FLYIO.md)**

---

**Votre application sera en ligne en quelques minutes ! 🎉**
