# 🎉 Application Multi-Utilisateurs Créée !

Votre application Strava est maintenant **multi-utilisateurs** avec PostgreSQL !

---

## ✅ Ce Qui a Été Créé

### **Nouveaux Fichiers**

1. **models.py** - Modèles de base de données (User, Activity)
2. **auth.py** - Authentification OAuth Strava
3. **strava_api.py** - Client API Strava
4. **app.py** - Application Flask multi-utilisateurs
5. **templates/index.html** - Page d'accueil avec bouton "Se connecter"
6. **templates/dashboard.html** - Dashboard personnel par utilisateur

### **Fichiers Mis à Jour**

- **requirements.txt** - Ajout de PostgreSQL, SQLAlchemy, Flask-Login
- **app.py** - Complètement refactorisé pour multi-utilisateurs

---

## 🔧 Configuration Requise

### **Étape 1 : Créer la Base PostgreSQL sur Fly.io**

```bash
# Créer la base de données
flyctl postgres create --name strava-db --region ams

# Attacher à votre app
flyctl postgres attach strava-db -a strava-app-old-sun-7399
```

### **Étape 2 : Configurer l'App Strava (OAuth)**

1. Allez sur : https://www.strava.com/settings/api
2. **Authorization Callback Domain** : `strava-app-old-sun-7399.fly.dev`
3. **Authorization Callback URL** : `https://strava-app-old-sun-7399.fly.dev/auth/callback`

### **Étape 3 : Configurer les Secrets Fly.io**

```bash
# SECRET_KEY pour Flask (générer une clé aléatoire)
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)

# Les secrets Strava sont déjà configurés (CLIENT_ID, CLIENT_SECRET)
# Mais vous n'avez PLUS besoin de REFRESH_TOKEN (chaque utilisateur aura le sien)
```

### **Étape 4 : Déployer**

```bash
flyctl deploy
```

---

## 🎯 Comment Ça Marche

### **Flux Utilisateur**

1. **Visite** : `https://strava-app-old-sun-7399.fly.dev`
2. **Clic** : "Se connecter avec Strava"
3. **Autorisation** : Strava demande l'autorisation
4. **Redirection** : L'utilisateur revient sur votre app
5. **Compte créé** : Son profil et ses tokens sont stockés en base
6. **Dashboard** : Il voit SES activités

### **Chaque Utilisateur**

- A son propre compte
- Voit seulement SES activités
- Ses tokens sont stockés en base de données
- Peut se déconnecter/reconnecter

---

## 📊 Structure de la Base de Données

### **Table users**

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | ID unique |
| strava_id | BIGINT | ID Strava (unique) |
| firstname | STRING | Prénom |
| lastname | STRING | Nom |
| email | STRING | Email |
| access_token | STRING | Token d'accès Strava |
| refresh_token | STRING | Token de rafraîchissement |
| expires_at | BIGINT | Date d'expiration du token |
| created_at | DATETIME | Date de création |
| last_login | DATETIME | Dernière connexion |

### **Table activities (optionnel - cache local)**

Vous pouvez stocker les activités en base pour :
- Cache local (moins d'appels API)
- Historique
- Analyses avancées

---

## 🚀 Routes Disponibles

| Route | Description |
|-------|-------------|
| `/` | Page d'accueil (bouton "Se connecter") |
| `/login` | Redirection vers OAuth Strava |
| `/auth/callback` | Callback OAuth (ne pas modifier) |
| `/dashboard` | Dashboard utilisateur (authentifié) |
| `/logout` | Déconnexion |

---

## 🔐 Sécurité

✅ **Tokens isolés** - Chaque utilisateur a ses propres tokens  
✅ **Sessions sécurisées** - Flask-Login gère les sessions  
✅ **Refresh automatique** - Les tokens expirent et se rafraîchissent  
✅ **Base PostgreSQL** - Données sécurisées et persistantes  
✅ **HTTPS** - Fly.io fournit SSL automatiquement  

---

## 📝 Commandes de Déploiement

```bash
# 1. Créer la base PostgreSQL
flyctl postgres create --name strava-db --region ams
flyctl postgres attach strava-db -a strava-app-old-sun-7399

# 2. Configurer SECRET_KEY
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)

# 3. Déployer
flyctl deploy

# 4. Voir les logs
flyctl logs

# 5. Ouvrir l'app
flyctl open
```

---

## 🎨 Personnalisation

### **Ajouter d'Autres Sports**

Dans `strava_api.py`, ligne 45 :

```python
if activity.get("type") in ["Swim", "Ride", "Run", "Walk", "Hike"]:
```

### **Modifier les Couleurs**

Dans `templates/dashboard.html`, modifiez les classes CSS.

### **Ajouter des Statistiques**

Modifiez `strava_api.py` pour ajouter d'autres calculs.

---

## ❓ Questions Fréquentes

### **Puis-je garder l'ancienne version ?**

Oui ! L'ancien fichier est sauvegardé dans `templates/index_old.html`.

### **Combien d'utilisateurs peuvent s'inscrire ?**

Illimité ! PostgreSQL sur Fly.io supporte des milliers d'utilisateurs.

### **Les activités sont-elles stockées ?**

Non, elles sont récupérées en temps réel de Strava. Mais vous pouvez activer le cache (voir models.py).

### **Que se passe-t-il si un token expire ?**

L'app le rafraîchit automatiquement (voir `auth.py` fonction `get_valid_token`).

---

## 🎉 Prêt à Déployer !

Suivez les étapes ci-dessus pour déployer votre app multi-utilisateurs !

**URL finale** : https://strava-app-old-sun-7399.fly.dev

Chaque utilisateur pourra se connecter avec son propre compte Strava ! 🚀
