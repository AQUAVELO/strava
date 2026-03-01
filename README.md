# Application Strava Flask

Cette application récupère et affiche vos activités Strava (natation, vélo, course à pied).

## 🚀 Installation

1. **L'environnement virtuel est déjà créé** avec toutes les dépendances installées.

2. **Si vous devez réinstaller les dépendances** :

```bash
source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org Flask requests python-decouple
```

3. **Configuration des identifiants** :

Les identifiants Strava sont déjà configurés dans le fichier `.env`. Assurez-vous que ce fichier est présent dans le répertoire racine.

## 📦 Dépendances

- **Flask** : Framework web Python
- **requests** : Pour les appels API vers Strava
- **python-decouple** : Pour gérer les variables d'environnement

## 🎯 Fonctionnalités

✅ Récupération automatique des activités Strava (natation, vélo, course)  
✅ Calcul du temps au 50m pour la natation  
✅ Affichage des pulsations cardiaques (moyenne et max)  
✅ Statistiques mensuelles par sport  
✅ Estimation des calories brûlées  
✅ Badge "Meilleur temps du jour" pour la natation  
✅ Interface moderne et responsive  
✅ Gestion automatique du refresh token Strava  

## 🎨 Interface

L'application affiche :
- **Statistiques mensuelles** : Distance et temps total par sport et par mois
- **Liste des activités** : Cartes détaillées avec toutes les informations
- **Design moderne** : Interface colorée et responsive avec des dégradés

## 🔧 Utilisation

### Option 1 : Utiliser le script de lancement (recommandé) :

```bash
./start.sh
```

### Option 2 : Lancer manuellement :

```bash
source venv/bin/activate
python3 app.py
```

L'application sera accessible sur : **http://127.0.0.1:5000**

Pour arrêter l'application, appuyez sur `CTRL+C` dans le terminal.

### Structure du projet :

```
strava/
├── app.py                 # Application Flask principale
├── .env                   # Variables d'environnement (identifiants Strava)
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
└── templates/
    └── index.html        # Template HTML avec CSS intégré
```

## 🔐 Sécurité

⚠️ **Important** : Le fichier `.env` contient vos identifiants Strava. Ne le partagez jamais publiquement et ne le commitez pas dans un dépôt Git public.

Pour protéger vos identifiants, ajoutez `.env` à votre `.gitignore` :

```bash
echo ".env" >> .gitignore
```

## 🏊‍♂️ Types d'activités supportées

- **Natation (Swim)** : Avec calcul du temps au 50m
- **Vélo (Ride)** : Distance et durée
- **Course (Run)** : Distance et durée

## 📊 API Strava

L'application utilise l'API Strava v3 pour récupérer les activités. Le token d'accès est automatiquement renouvelé grâce au refresh token.

## 🐛 Dépannage

Si l'application ne récupère pas les activités :

1. Vérifiez que les identifiants dans `.env` sont corrects
2. Vérifiez que le refresh token est toujours valide
3. Consultez les logs dans la console pour identifier l'erreur

## 📝 Logs

L'application affiche des logs détaillés dans la console :
- ✅ Succès des opérations
- ❌ Erreurs rencontrées
- 📥 Nombre d'activités récupérées
- 🔄 Renouvellement du token

## 🌐 Configuration MAMP

Si vous utilisez MAMP, l'application est déjà dans le bon répertoire (`/Applications/MAMP/htdocs/strava/`).

Pour utiliser Python avec MAMP, vous pouvez soit :
- Lancer l'application directement avec Python (recommandé)
- Configurer MAMP pour utiliser Python/WSGI (plus complexe)

## 🎉 Profitez de vos statistiques Strava !
