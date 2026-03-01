# 🎨 Guide de Personnalisation

Ce guide vous explique comment personnaliser votre application Strava.

---

## 🔧 Modifications Simples

### 1. Changer le Nombre d'Activités Affichées

**Fichier** : `app.py`  
**Ligne** : 192

```python
# Par défaut : 30 activités
activities = get_activities(page=1, per_page=30)

# Pour afficher 50 activités
activities = get_activities(page=1, per_page=50)

# Pour afficher 100 activités
activities = get_activities(page=1, per_page=100)
```

### 2. Changer le Port de l'Application

**Fichier** : `app.py`  
**Ligne** : 203

```python
# Par défaut : port 5000
app.run(debug=True, use_reloader=False)

# Pour utiliser le port 8080
app.run(debug=True, use_reloader=False, port=8080)

# Pour utiliser le port 3000
app.run(debug=True, use_reloader=False, port=3000)
```

### 3. Ajouter d'Autres Types d'Activités

**Fichier** : `app.py`  
**Ligne** : 64

```python
# Par défaut : Swim, Ride, Run
if activity.get("type") in ["Swim", "Ride", "Run"]:

# Ajouter la marche (Walk)
if activity.get("type") in ["Swim", "Ride", "Run", "Walk"]:

# Ajouter plusieurs activités
if activity.get("type") in ["Swim", "Ride", "Run", "Walk", "Hike", "Yoga"]:
```

**Pensez aussi à mettre à jour** :
- Le calcul des calories (fonction `estimate_calories`)
- Les statistiques mensuelles
- L'interface HTML (couleurs, icônes)

### 4. Modifier les Couleurs de l'Interface

**Fichier** : `templates/index.html`

#### Couleur de fond (dégradé principal)

**Ligne** : 18

```css
/* Par défaut : violet-bleu */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Bleu océan */
background: linear-gradient(135deg, #2E3192 0%, #1BFFFF 100%);

/* Orange-rouge */
background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);

/* Vert forêt */
background: linear-gradient(135deg, #134E5E 0%, #71B280 100%);
```

#### Couleurs par Sport

**Natation** (ligne 77) :
```css
.sport-card.swim {
    border-left: 4px solid #00BCD4;  /* Cyan par défaut */
}
```

**Vélo** (ligne 81) :
```css
.sport-card.ride {
    border-left: 4px solid #FF6B6B;  /* Rouge par défaut */
}
```

**Course** (ligne 85) :
```css
.sport-card.run {
    border-left: 4px solid #4CAF50;  /* Vert par défaut */
}
```

### 5. Changer les Estimations de Calories

**Fichier** : `app.py`  
**Fonction** : `estimate_calories` (ligne 130)

```python
def estimate_calories(activity):
    """Estime les calories brûlées."""
    if activity["type"] == "Swim":
        return int(400 * (activity["moving_time"] / 3600))  # 400 kcal/h
    elif activity["type"] == "Ride":
        return int(600 * (activity["moving_time"] / 3600))  # 600 kcal/h
    elif activity["type"] == "Run":
        return int(800 * (activity["moving_time"] / 3600))  # 800 kcal/h
    return 0
```

**Ajustez les valeurs selon vos besoins** :
- Natation légère : 300-400 kcal/h
- Natation intense : 500-700 kcal/h
- Vélo léger : 400-500 kcal/h
- Vélo intense : 700-900 kcal/h
- Course légère : 600-700 kcal/h
- Course intense : 900-1200 kcal/h

---

## 🚀 Modifications Avancées

### 1. Ajouter un Filtre par Date

**Fichier** : `app.py`  
**Fonction** : `get_activities`

Ajoutez après la ligne 54 :

```python
from datetime import datetime, timedelta

# Activités des 7 derniers jours
week_ago = (datetime.now() - timedelta(days=7)).timestamp()
ACTIVITIES_URL += f"&after={int(week_ago)}"

# Activités du mois en cours
month_start = datetime.now().replace(day=1).timestamp()
ACTIVITIES_URL += f"&after={int(month_start)}"
```

### 2. Ajouter un Endpoint API JSON

**Fichier** : `app.py`

Ajoutez avant la ligne 200 :

```python
@app.route("/api/activities")
def api_activities():
    """Retourne les activités au format JSON."""
    from flask import jsonify
    activities = get_activities(page=1, per_page=30)
    
    # Convertir datetime en string pour JSON
    serializable = []
    for activity in activities:
        act_copy = activity.copy()
        act_copy["start_date"] = activity["start_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
        serializable.append(act_copy)
    
    return jsonify(serializable)
```

**Accès** : http://127.0.0.1:5000/api/activities

### 3. Ajouter des Graphiques avec Chart.js

**Fichier** : `templates/index.html`

Ajoutez avant `</head>` :

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Ajoutez dans le `<body>`, après les statistiques mensuelles :

```html
<div class="chart-container">
    <canvas id="distanceChart"></canvas>
</div>

<script>
const ctx = document.getElementById('distanceChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Natation', 'Vélo', 'Course'],
        datasets: [{
            label: 'Distance (km)',
            data: [/* vos données */],
            backgroundColor: ['#00BCD4', '#FF6B6B', '#4CAF50']
        }]
    }
});
</script>
```

### 4. Ajouter une Page de Détails d'Activité

**Fichier** : `app.py`

Ajoutez une nouvelle route :

```python
@app.route("/activity/<int:activity_id>")
def activity_detail(activity_id):
    """Affiche les détails d'une activité."""
    # Récupérer les détails complets depuis l'API Strava
    global ACCESS_TOKEN
    
    DETAIL_URL = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(DETAIL_URL, headers=headers)
    if response.status_code == 200:
        activity = response.json()
        return render_template("detail.html", activity=activity)
    else:
        return "Activité non trouvée", 404
```

Créez `templates/detail.html` avec les détails complets.

### 5. Ajouter un Cache pour les Activités

**Fichier** : `app.py`

Ajoutez en haut du fichier :

```python
from functools import lru_cache
from datetime import datetime

@lru_cache(maxsize=1)
def get_activities_cached(timestamp):
    """Cache les activités pendant 5 minutes."""
    return get_activities(page=1, per_page=30)

@app.route("/")
def home():
    # Timestamp par tranche de 5 minutes
    cache_key = int(time.time() / 300)
    activities = get_activities_cached(cache_key)
    # ... reste du code
```

---

## 🎨 Personnalisation de l'Interface

### 1. Changer la Police de Caractères

**Fichier** : `templates/index.html`  
**Ligne** : 12

```css
/* Police actuelle : Segoe UI */
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

/* Police Google Fonts (ajoutez d'abord le lien dans <head>) */
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">

font-family: 'Roboto', sans-serif;
```

### 2. Ajouter des Animations

Ajoutez dans la section `<style>` :

```css
.activity-card {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### 3. Mode Sombre

Ajoutez un bouton dans le `<body>` :

```html
<button onclick="toggleDarkMode()">🌙 Mode Sombre</button>

<script>
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}
</script>
```

Ajoutez dans le CSS :

```css
body.dark-mode {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

body.dark-mode .activity-card {
    background: #333;
    color: white;
}
```

---

## 📊 Ajouter de Nouvelles Statistiques

### 1. Vitesse Moyenne

**Fichier** : `app.py`

Dans la fonction `get_activities`, ajoutez :

```python
activity_data["average_speed"] = activity_data["distance"] / activity_data["moving_time"]
```

Affichez dans `templates/index.html` :

```html
<div class="stat-item">
    <div class="stat-label">Vitesse moy.</div>
    <div class="stat-value">{{ "%.1f"|format(activity.average_speed * 3.6) }} km/h</div>
</div>
```

### 2. Dénivelé Total

Récupérez depuis l'API :

```python
activity_data["elevation_gain"] = activity.get("total_elevation_gain", 0)
```

### 3. Nombre Total d'Activités

```python
@app.route("/")
def home():
    activities = get_activities(page=1, per_page=30)
    total_count = len(activities)
    # Passez total_count au template
```

---

## 🔧 Configuration Avancée

### 1. Variables d'Environnement Supplémentaires

**Fichier** : `.env`

Ajoutez :

```env
APP_PORT=5000
DEBUG_MODE=True
ACTIVITIES_PER_PAGE=30
CACHE_DURATION=300
```

Utilisez dans `app.py` :

```python
APP_PORT = config("APP_PORT", default=5000, cast=int)
DEBUG_MODE = config("DEBUG_MODE", default=True, cast=bool)

app.run(debug=DEBUG_MODE, port=APP_PORT)
```

### 2. Logs dans un Fichier

**Fichier** : `app.py`

Modifiez la configuration du logging :

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strava_app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🎯 Exemples de Personnalisation Complète

### Exemple 1 : Application pour Coureurs Uniquement

```python
# app.py - ligne 64
if activity.get("type") == "Run":  # Seulement la course

# templates/index.html - Supprimer les autres sports
```

### Exemple 2 : Focus sur les Records

Ajoutez une section records :

```python
def get_personal_records(activities):
    """Trouve les records personnels."""
    records = {
        "longest_distance": max(activities, key=lambda x: x["distance"]),
        "longest_time": max(activities, key=lambda x: x["moving_time"]),
        "most_calories": max(activities, key=lambda x: x["calories"])
    }
    return records
```

### Exemple 3 : Comparaison Année par Année

```python
def compare_years(activities):
    """Compare les statistiques par année."""
    by_year = defaultdict(lambda: {"distance": 0, "time": 0})
    for activity in activities:
        year = activity["start_date"].year
        by_year[year]["distance"] += activity["distance"]
        by_year[year]["time"] += activity["moving_time"]
    return by_year
```

---

## 📱 Responsive et Mobile

L'application est déjà responsive, mais vous pouvez améliorer :

```css
@media (max-width: 480px) {
    .activity-card {
        padding: 15px;
    }
    
    .activity-stats {
        grid-template-columns: 1fr;
    }
}
```

---

## 🔒 Sécurité Supplémentaire

### 1. Limiter l'Accès par IP

```python
from flask import request, abort

@app.before_request
def limit_remote_addr():
    allowed_ips = ['127.0.0.1', '::1']
    if request.remote_addr not in allowed_ips:
        abort(403)
```

### 2. Ajouter un Mot de Passe Simple

```python
from flask import session, redirect, url_for

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == "votre_mot_de_passe":
            session["logged_in"] = True
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # ... reste du code
```

---

## 🎉 Besoin d'Aide ?

Consultez la documentation complète dans `README.md` et `API_DOCUMENTATION.md`.

**Bonne personnalisation ! 🚀**
