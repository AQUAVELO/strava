# 📚 Application Strava Flask - Index de la Documentation

Bienvenue dans votre application Python Flask pour récupérer et afficher vos activités Strava !

---

## 🚀 Démarrage Rapide

**Pour commencer immédiatement, lisez** : [`QUICKSTART.md`](QUICKSTART.md)

**Commande de lancement** :
```bash
./start.sh
```

**URL de l'application** : http://127.0.0.1:5000

---

## 📖 Documentation Complète

### 1. Guide de Démarrage
- **[QUICKSTART.md](QUICKSTART.md)** - Guide rapide pour lancer l'application (2 min)
- **[INSTALL_SUCCESS.md](INSTALL_SUCCESS.md)** - Résumé de l'installation et statut

### 2. Documentation Technique
- **[README.md](README.md)** - Documentation technique complète
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentation de l'API et des endpoints

### 3. Fichiers de Configuration
- **[.env](.env)** - Identifiants Strava (⚠️ Confidentiel)
- **[requirements.txt](requirements.txt)** - Liste des dépendances Python
- **[.gitignore](.gitignore)** - Fichiers à ignorer par Git

---

## 📁 Structure du Projet

```
/Applications/MAMP/htdocs/strava/
│
├── 🚀 FICHIERS DE LANCEMENT
│   ├── start.sh                    # Script de lancement rapide
│   └── app.py                      # Application Flask principale (8.1 KB)
│
├── 🔐 CONFIGURATION
│   ├── .env                        # Identifiants Strava (secret)
│   ├── requirements.txt            # Dépendances Python
│   └── .gitignore                 # Protection des fichiers sensibles
│
├── 📚 DOCUMENTATION
│   ├── INDEX.md                   # Ce fichier - Index de la doc
│   ├── QUICKSTART.md              # Guide de démarrage rapide
│   ├── README.md                  # Documentation technique
│   ├── API_DOCUMENTATION.md       # Documentation API
│   └── INSTALL_SUCCESS.md         # Résumé de l'installation
│
├── 🎨 INTERFACE
│   └── templates/
│       └── index.html             # Template HTML avec CSS (11.3 KB)
│
└── 🐍 ENVIRONNEMENT PYTHON
    └── venv/                      # Environnement virtuel Python
        ├── bin/                   # Exécutables Python
        ├── lib/                   # Bibliothèques installées
        └── ...
```

---

## 🎯 Fonctionnalités Principales

✅ **Récupération automatique** des activités Strava  
✅ **3 types d'activités** : Natation 🏊‍♂️, Vélo 🚴‍♂️, Course 🏃‍♂️  
✅ **Statistiques mensuelles** par sport  
✅ **Temps au 50m** pour la natation  
✅ **Pulsations cardiaques** (moyenne et max)  
✅ **Calories brûlées** par activité  
✅ **Interface moderne** et responsive  
✅ **Gestion automatique** du token Strava  

---

## 🛠️ Technologies Utilisées

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| Python | 3.14.2 | Langage principal |
| Flask | 3.1.2 | Framework web |
| Requests | 2.32.5 | Requêtes HTTP |
| Python Decouple | 3.8 | Variables d'environnement |
| HTML5 + CSS3 | - | Interface utilisateur |

---

## 📊 Données Affichées

### Pour Chaque Activité :
- Type d'activité (Natation, Vélo, Course)
- Nom de l'activité
- Date et heure
- Distance (km)
- Durée (heures et minutes)
- Calories brûlées
- Pulsations (moyenne et max)
- Temps au 50m (natation uniquement)
- Badge "Meilleur temps du jour" (natation)

### Statistiques Mensuelles :
- Distance totale par sport (km)
- Temps total par sport (heures)
- Regroupement par mois

---

## 🔐 Sécurité et Confidentialité

⚠️ **IMPORTANT** : Le fichier `.env` contient vos identifiants Strava.

**Protections en place** :
- ✅ `.env` dans `.gitignore` (non committé)
- ✅ Token renouvelé automatiquement
- ✅ Pas de logs sensibles

**Ne jamais partager** :
- Client ID
- Client Secret
- Refresh Token
- Access Token

---

## 🚀 Commandes Utiles

### Démarrer l'application
```bash
./start.sh
```

### Démarrer manuellement
```bash
source venv/bin/activate
python3 app.py
```

### Arrêter l'application
```
CTRL + C
```

### Réinstaller les dépendances
```bash
source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org Flask requests python-decouple
```

### Vérifier la structure
```bash
ls -lah
```

---

## 📈 Statut de l'Installation

| Élément | Statut |
|---------|--------|
| Application Flask | ✅ Installée |
| Environnement virtuel | ✅ Créé |
| Dépendances | ✅ Installées |
| Identifiants Strava | ✅ Configurés |
| Interface web | ✅ Prête |
| Test de connexion | ✅ Réussi (29 activités) |

---

## ❓ Aide et Support

### Problèmes Fréquents

**L'application ne démarre pas**
- Vérifiez que vous êtes dans le bon répertoire
- Utilisez `source venv/bin/activate`

**Aucune activité affichée**
- Vérifiez les identifiants dans `.env`
- Consultez les logs dans le terminal

**Port 5000 déjà utilisé**
- Modifiez le port dans `app.py` (ligne finale)

**Erreur de module**
- Réactivez l'environnement : `source venv/bin/activate`

### Où Trouver de l'Aide ?

1. **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage
2. **[README.md](README.md)** - Documentation complète
3. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Détails techniques
4. **Logs dans le terminal** - Messages d'erreur détaillés

---

## 🎨 Aperçu de l'Interface

L'interface web affiche :

1. **En-tête**
   - Titre "Mes Activités Strava"
   - Sous-titre avec les sports

2. **Statistiques Mensuelles**
   - Tableau récapitulatif par mois
   - Distance et temps par sport
   - Code couleur par activité

3. **Liste des Activités**
   - Cartes colorées et interactives
   - Toutes les informations détaillées
   - Badges pour les records
   - Design responsive (mobile + desktop)

---

## 📊 Exemple de Données Récupérées

Au premier lancement, l'application a récupéré :
- **29 activités** depuis l'API Strava
- Types : Natation, Vélo, Course
- Données : Distance, durée, calories, pulsations
- Token valide jusqu'au : 15 février 2026, 20h54

---

## 🔄 Mises à Jour Futures

Idées d'améliorations possibles :
- Graphiques de progression
- Filtres par date/sport
- Export des données (CSV/JSON)
- Comparaison de performances
- Notifications de records
- Support multi-utilisateurs
- Déploiement web

---

## 📞 Informations Projet

- **Nom** : Application Strava Flask
- **Version** : 1.0.0
- **Date de création** : 15 février 2026
- **Langage** : Python 3.14.2
- **Framework** : Flask 3.1.2
- **Statut** : ✅ Opérationnelle et testée

---

## 🎉 Prêt à Commencer ?

**Lancez l'application maintenant** :

```bash
cd /Applications/MAMP/htdocs/strava
./start.sh
```

Puis ouvrez votre navigateur : **http://127.0.0.1:5000**

---

**Bonne visualisation de vos activités Strava ! 🏃‍♂️🚴‍♂️🏊‍♂️**
