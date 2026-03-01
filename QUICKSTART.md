# 🚀 Guide de Démarrage Rapide - Application Strava

## ✅ Tout est prêt !

Votre application Strava est complètement configurée et prête à être utilisée.

## 🎯 Lancement de l'application

### Méthode simple (recommandée) :

```bash
./start.sh
```

### Ou manuellement :

```bash
source venv/bin/activate
python3 app.py
```

## 🌐 Accéder à l'application

Une fois lancée, ouvrez votre navigateur et allez sur :

**http://127.0.0.1:5000**

Vous devriez voir vos activités Strava s'afficher automatiquement !

## 📊 Ce que vous verrez

✅ **Statistiques mensuelles** par sport (natation, vélo, course)  
✅ **Liste détaillée** de vos 30 dernières activités  
✅ **Temps au 50m** pour la natation  
✅ **Pulsations cardiaques** (moyenne et max)  
✅ **Calories brûlées** par activité  
✅ **Interface moderne** et responsive  

## 🛑 Arrêter l'application

Dans le terminal où l'application tourne, appuyez sur :

```
CTRL + C
```

## 🔐 Sécurité

⚠️ Le fichier `.env` contient vos identifiants Strava. Ne le partagez jamais !

## 📝 Structure créée

```
strava/
├── app.py                 # Application Flask
├── .env                   # Identifiants Strava (secret !)
├── requirements.txt       # Liste des dépendances
├── start.sh              # Script de lancement
├── README.md             # Documentation complète
├── QUICKSTART.md         # Ce fichier
├── .gitignore            # Fichiers à ignorer par Git
├── venv/                 # Environnement virtuel Python
└── templates/
    └── index.html        # Interface web
```

## ❓ En cas de problème

1. **L'application ne démarre pas** : Vérifiez que vous êtes dans le bon répertoire
2. **Erreur de module** : Réactivez l'environnement virtuel avec `source venv/bin/activate`
3. **Pas d'activités** : Vérifiez vos identifiants dans `.env`
4. **Port déjà utilisé** : Un autre programme utilise le port 5000, arrêtez-le d'abord

## 🎉 C'est tout !

Votre application est prête à l'emploi. Profitez de vos statistiques Strava !

---

Pour plus de détails techniques, consultez le fichier **README.md**.
