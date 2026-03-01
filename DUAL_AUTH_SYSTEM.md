# 🔐 Système d'Authentification Double - CRÉÉ !

Votre application supporte maintenant **2 méthodes de connexion** :

1. ✅ **Email + Mot de passe** (classique)
2. ✅ **Connexion Strava** (OAuth)

---

## 🎯 Fonctionnalités Ajoutées

### **1. Inscription Classique**
- Créer un compte avec **email + mot de passe**
- Prénom et nom optionnels
- Mot de passe hashé sécurisé (bcrypt)

### **2. Connexion Classique**
- Se connecter avec **email + mot de passe**
- Session persistante

### **3. Connexion Strava**
- Se connecter directement avec Strava OAuth
- Création automatique du compte

### **4. Liaison de Compte**
- **Lier son compte Strava** après inscription email
- Transférer ses données Strava sur son compte existant
- Utilisateurs peuvent avoir les deux : email ET Strava

---

## 📋 Routes Disponibles

| Route | Description |
|-------|-------------|
| `/` | Page d'accueil (2 boutons de connexion) |
| `/register` | Inscription email/mot de passe |
| `/login` | Connexion email/mot de passe |
| `/login/strava` | Connexion OAuth Strava |
| `/auth/callback` | Callback OAuth (liaison auto si déjà connecté) |
| `/dashboard` | Dashboard (avec bouton "Lier Strava" si non lié) |
| `/logout` | Déconnexion |

---

## 🔄 Flux Utilisateur

### **Scénario 1 : Inscription Email puis Liaison Strava**

1. Visite `/` → Clic "S'inscrire"
2. Remplit le formulaire `/register`
3. **Compte créé** (email + mot de passe)
4. Redirigé vers `/dashboard`
5. Voit le message : "Vous devez lier votre compte Strava"
6. Clic "Connecter mon compte Strava"
7. **Strava OAuth** → Compte lié
8. Voit ses activités Strava !

### **Scénario 2 : Connexion Directe Strava**

1. Visite `/` → Clic "Se connecter avec Strava"
2. **Strava OAuth** → Compte créé automatiquement
3. Redirigé vers `/dashboard`
4. Voit ses activités immédiatement

### **Scénario 3 : Connexion Email Existant**

1. Visite `/` → Clic "Se connecter avec Email"
2. Entre email + mot de passe
3. **Connecté** → Dashboard
4. Voit ses activités (si Strava déjà lié)

---

## 🗄️ Modifications Base de Données

### **Table `users` - Mise à Jour**

```sql
- email (UNIQUE, NOT NULL) -- Maintenant obligatoire
- password_hash (NULLABLE) -- Null si connexion Strava uniquement
- strava_id (NULLABLE) -- Null si pas encore lié
- access_token (NULLABLE)
- refresh_token (NULLABLE)
- expires_at (NULLABLE)
```

### **Nouvelles Méthodes User**

```python
user.set_password(password)      # Définir mot de passe
user.check_password(password)    # Vérifier mot de passe
user.has_strava_linked()         # Vérifie si Strava lié
```

---

## 📝 Fichiers Créés/Modifiés

### **Créés**
- ✅ `templates/login.html` - Page de connexion email
- ✅ `templates/register.html` - Page d'inscription

### **Modifiés**
- ✅ `models.py` - Support email/password + liaison Strava
- ✅ `auth.py` - Liaison de compte existant
- ✅ `app.py` - Routes register/login + liaison auto
- ✅ `templates/index.html` - 2 boutons de connexion
- ✅ `templates/dashboard.html` - Bouton "Lier Strava"

---

## 🚀 Déployer les Changements

```bash
# Aller dans le répertoire
cd /Applications/MAMP/htdocs/strava

# Déployer sur Fly.io
flyctl deploy
```

---

## 🎨 Interface Utilisateur

### **Page d'Accueil**
```
┌─────────────────────────────────────┐
│     🏃‍♂️ Strava Stats              │
│                                     │
│  [📧 Se connecter avec Email]      │
│  [🔗 Se connecter avec Strava]     │
│                                     │
│  Pas de compte ? S'inscrire         │
└─────────────────────────────────────┘
```

### **Dashboard (Sans Strava)**
```
┌─────────────────────────────────────┐
│  Bienvenue Claude ! 👋              │
│  [🔗 Lier Strava] [Déconnexion]    │
├─────────────────────────────────────┤
│                                     │
│  🔗 Liez votre compte Strava        │
│                                     │
│  Pour voir vos activités, connectez │
│  votre compte Strava                │
│                                     │
│  [Connecter mon compte Strava]      │
│                                     │
└─────────────────────────────────────┘
```

### **Dashboard (Avec Strava)**
```
┌─────────────────────────────────────┐
│  Bienvenue Claude ! 👋              │
│  [Actualiser] [Déconnexion]         │
├─────────────────────────────────────┤
│  📊 Statistiques Mensuelles         │
│  📝 Vos Activités...                │
└─────────────────────────────────────┘
```

---

## 🔐 Sécurité

### **Mots de Passe**
- ✅ Hashés avec **Werkzeug** (bcrypt)
- ✅ Jamais stockés en clair
- ✅ Vérification sécurisée

### **Sessions**
- ✅ Flask-Login gère les sessions
- ✅ SECRET_KEY sécurisé
- ✅ HTTPS sur Fly.io

### **OAuth Strava**
- ✅ Tokens stockés en base
- ✅ Refresh automatique
- ✅ Isolés par utilisateur

---

## ❓ Questions Fréquentes

### **Puis-je avoir email ET Strava ?**
Oui ! Vous pouvez créer un compte email, puis lier votre Strava après.

### **Que se passe-t-il si je me connecte avec Strava sans compte ?**
Un nouveau compte est créé automatiquement avec votre email Strava.

### **Puis-je me connecter sans Strava ?**
Oui ! Créez un compte avec email/mot de passe. Vous lierez Strava plus tard.

### **Mes données Strava sont-elles transférées ?**
Oui ! Une fois Strava lié, toutes vos activités apparaissent dans votre dashboard.

---

## 🎉 C'est Prêt !

Déployez maintenant pour tester :

```bash
flyctl deploy
```

Votre app supportera :
- ✅ Inscription email/password
- ✅ Connexion email/password
- ✅ Connexion OAuth Strava
- ✅ Liaison de compte Strava
- ✅ Gestion multi-utilisateurs

🚀
