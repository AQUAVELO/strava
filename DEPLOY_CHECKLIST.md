# ✅ Checklist de Déploiement Fly.io

## 📋 Avant le Déploiement

### Fichiers Requis
- [x] Dockerfile créé
- [x] .dockerignore créé
- [x] fly.toml configuré
- [x] requirements.txt mis à jour (avec gunicorn)
- [x] app.py modifié pour la production
- [x] .gitignore protège .env

### Installation Locale
- [x] Python installé
- [x] Flask installé
- [x] Application testée localement
- [x] Token Strava fonctionnel

---

## 🚀 Installation Fly.io

### À Faire par l'Utilisateur

- [ ] **Installer flyctl**
  ```bash
  brew install flyctl
  ```
  
- [ ] **Créer un compte Fly.io**
  - Allez sur https://fly.io/
  - Créez un compte gratuit
  
- [ ] **Se connecter**
  ```bash
  flyctl auth login
  ```

---

## 🔐 Configuration des Secrets

### À Faire par l'Utilisateur

Exécutez ces commandes **une seule fois** :

- [ ] **CLIENT_ID**
  ```bash
  flyctl secrets set CLIENT_ID=149497
  ```

- [ ] **CLIENT_SECRET**
  ```bash
  flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d
  ```

- [ ] **REFRESH_TOKEN**
  ```bash
  flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7
  ```

- [ ] **INDEX_URL**
  ```bash
  flyctl secrets set INDEX_URL=https://votre-domaine.com/index
  ```

---

## 📝 Personnalisation (Optionnel)

- [ ] **Modifier le nom de l'app dans fly.toml**
  ```toml
  app = "mon-strava-app"  # Changez "strava-app" par votre nom
  ```

- [ ] **Choisir une autre région**
  Régions disponibles : ams (Amsterdam), cdg (Paris), lhr (Londres), etc.
  ```toml
  primary_region = "cdg"  # Paris au lieu d'Amsterdam
  ```

---

## 🚢 Déploiement

### Option A : Script Automatique (Recommandé)

- [ ] **Exécuter le script de déploiement**
  ```bash
  cd /Applications/MAMP/htdocs/strava
  ./deploy_flyio.sh
  ```

### Option B : Déploiement Manuel

- [ ] **Initialiser Git (si pas déjà fait)**
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  ```

- [ ] **Lancer l'application**
  ```bash
  flyctl launch --no-deploy
  ```

- [ ] **Déployer**
  ```bash
  flyctl deploy
  ```

---

## ✅ Vérification Post-Déploiement

- [ ] **Vérifier le statut**
  ```bash
  flyctl status
  ```

- [ ] **Voir les logs**
  ```bash
  flyctl logs
  ```

- [ ] **Ouvrir l'application**
  ```bash
  flyctl open
  ```

- [ ] **Tester dans le navigateur**
  - L'application doit afficher vos activités Strava
  - Vérifier que les statistiques sont correctes
  - Tester sur mobile (responsive)

---

## 🐛 En Cas de Problème

### Erreur de Déploiement

- [ ] Vérifier les logs : `flyctl logs`
- [ ] Vérifier que les secrets sont configurés : `flyctl secrets list`
- [ ] Consulter DEPLOY_FLYIO.md section Dépannage

### Aucune Activité Affichée

- [ ] Vérifier les logs : `flyctl logs`
- [ ] Vérifier le REFRESH_TOKEN : `flyctl secrets list`
- [ ] Reconfigurer si nécessaire : `flyctl secrets set REFRESH_TOKEN=...`

### L'Application ne Démarre Pas

- [ ] Vérifier que le port 8080 est bien configuré
- [ ] Vérifier que gunicorn est dans requirements.txt
- [ ] Redéployer : `flyctl deploy`

---

## 📊 Résultat Final

Une fois terminé, vous aurez :

✅ Application accessible 24/7 sur Internet  
✅ URL publique : https://strava-app.fly.dev  
✅ HTTPS automatique (certificat SSL)  
✅ Arrêt/démarrage automatique (économie)  
✅ Logs en temps réel accessibles  
✅ Facile à mettre à jour (flyctl deploy)  

---

## 🎯 Prochaines Étapes (Optionnel)

Après le déploiement, vous pouvez :

- [ ] Configurer un domaine personnalisé
- [ ] Ajouter plusieurs régions pour plus de rapidité
- [ ] Augmenter les ressources si nécessaire
- [ ] Configurer des alertes de monitoring
- [ ] Ajouter une base de données
- [ ] Mettre en place un CI/CD avec GitHub Actions

---

## 📚 Documentation de Référence

- **Guide rapide** : DEPLOY_QUICK.md
- **Guide complet** : DEPLOY_FLYIO.md
- **Documentation Fly.io** : https://fly.io/docs/
- **Support Fly.io** : https://community.fly.io/

---

## 🎉 Félicitations !

Une fois cette checklist complétée, votre application Strava sera en ligne et accessible depuis n'importe où dans le monde ! 🌍🏃‍♂️🚴‍♂️🏊‍♂️
