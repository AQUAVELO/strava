# 🔌 Documentation API - Application Strava

## 📡 Endpoints Disponibles

### 1. Page Principale

**Route** : `/`  
**Méthode** : `GET`  
**Description** : Affiche la page principale avec toutes les activités Strava

**Réponse** : Page HTML avec :
- Statistiques mensuelles par sport
- Liste des 30 dernières activités
- Détails de chaque activité (distance, durée, calories, etc.)

**Exemple d'utilisation** :
```
http://127.0.0.1:5000/
```

---

## 🔐 Configuration API Strava

### Variables d'Environnement (.env)

```env
CLIENT_ID=149497
CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d
REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7
INDEX_URL=https://votre-domaine.com/index
```

### Obtention du Token d'Accès

L'application gère automatiquement le renouvellement du token via la fonction :

```python
def get_new_access_token()
```

**Endpoint Strava utilisé** :
```
POST https://www.strava.com/oauth/token
```

**Paramètres** :
- `client_id` : ID de votre application Strava
- `client_secret` : Secret de votre application
- `grant_type` : "refresh_token"
- `refresh_token` : Token de renouvellement

**Réponse** :
```json
{
  "access_token": "f602e7aef0b1f3842f3ce655745936645beca3fb",
  "expires_at": 1771190044
}
```

---

## 📥 Récupération des Activités

### Fonction : `get_activities(page=1, per_page=30)`

**Endpoint Strava** :
```
GET https://www.strava.com/api/v3/athlete/activities
```

**Paramètres** :
- `page` : Numéro de page (défaut : 1)
- `per_page` : Nombre d'activités par page (défaut : 30)

**Headers** :
```
Authorization: Bearer {access_token}
```

**Types d'activités récupérées** :
- `Swim` : Natation
- `Ride` : Vélo
- `Run` : Course à pied

### Structure des Données Récupérées

```json
{
  "id": 17403479760,
  "type": "Swim",
  "name": "Morning Swim",
  "distance": 2000,
  "moving_time": 1800,
  "calories": 400,
  "start_date": "2026-02-15T08:30:00Z",
  "average_heartrate": 145,
  "max_heartrate": 165,
  "time_per_50m": 90.0,
  "best_time_per_50m": 90.0
}
```

### Champs Calculés

1. **time_per_50m** (natation uniquement) :
```python
time_per_50m = moving_time / (distance / 50)
```

2. **calories** (si non fourni par Strava) :
```python
# Natation : 400 kcal/heure
# Vélo : 600 kcal/heure
# Course : 800 kcal/heure
calories = base_rate * (moving_time / 3600)
```

3. **best_time_per_50m** (natation) :
- Meilleur temps au 50m parmi toutes les séances du même jour

---

## 📊 Calculs Statistiques

### Fonction : `calculate_monthly_totals(activities)`

**Calcule pour chaque mois** :
- Distance totale par sport (km)
- Temps total par sport (heures)

**Structure de retour** :
```python
{
  "2026-02": {
    "Swim": {"distance": 45.5, "moving_time": 12.5},
    "Ride": {"distance": 120.0, "moving_time": 8.0},
    "Run": {"distance": 30.0, "moving_time": 3.5}
  }
}
```

---

## 🔄 Envoi des Données (Optionnel)

### Fonction : `send_to_index(data)`

Envoie les données vers une URL externe configurée dans `INDEX_URL`.

**Endpoint** : Défini dans `.env` (actuellement : exemple)  
**Méthode** : `POST`  
**Content-Type** : `application/json`

**Format des données** :
```json
[
  {
    "id": 17403479760,
    "type": "Swim",
    "name": "Morning Swim",
    "distance": 2000,
    "moving_time": 1800,
    "start_date": "2026-02-15T08:30:00Z"
  }
]
```

⚠️ **Note** : Cette fonctionnalité nécessite une URL valide. Actuellement, l'URL d'exemple génère une erreur 405 (normal).

---

## 🛡️ Gestion des Erreurs

### Token Expiré
```python
if not ACCESS_TOKEN or time.time() >= EXPIRES_AT:
    get_new_access_token()
```

### Erreur API Strava
```python
if response.status_code != 200:
    logger.error(f"❌ Erreur API Strava : {response.status_code}")
    return []
```

### Exception Générale
```python
try:
    # Code
except Exception as e:
    logger.error(f"⚠️ Erreur : {e}")
    return []
```

---

## 📝 Logs et Débogage

### Format des Logs

```
INFO:__main__:✅ Nouvel access token obtenu : [token]
INFO:__main__:⏳ Expire à : 2026-02-15 20:54:04
INFO:__main__:🏠 Début de la route principale - Call ID: [timestamp]
INFO:__main__:📥 Nombre d'activités brutes reçues : 30
INFO:__main__:📤 Activités filtrées : 29 - IDs : [liste des IDs]
INFO:__main__:✅ Fin de la route principale - Call ID: [timestamp]
```

### Types de Logs

- ✅ Succès : Opérations réussies
- ❌ Erreur : Problèmes critiques
- ⚠️ Avertissement : Problèmes non-bloquants
- 🔄 Info : Opérations en cours
- 📥 Données : Réception de données
- 📤 Données : Envoi de données

---

## 🔧 Extension de l'API

### Ajouter un Nouvel Endpoint

```python
@app.route("/api/activities")
def api_activities():
    activities = get_activities(page=1, per_page=30)
    return jsonify(activities)
```

### Ajouter des Paramètres

```python
from flask import request

@app.route("/api/activities")
def api_activities():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    activities = get_activities(page=page, per_page=per_page)
    return jsonify(activities)
```

**Exemple d'utilisation** :
```
http://127.0.0.1:5000/api/activities?page=2&per_page=50
```

---

## 📚 Ressources API Strava

### Documentation Officielle
- **API Reference** : https://developers.strava.com/docs/reference/
- **Getting Started** : https://developers.strava.com/docs/getting-started/
- **Authentication** : https://developers.strava.com/docs/authentication/

### Endpoints Strava Disponibles

1. **Athlete Activities** :
```
GET /athlete/activities
```

2. **Activity Details** :
```
GET /activities/{id}
```

3. **Activity Streams** :
```
GET /activities/{id}/streams
```

4. **Athlete Stats** :
```
GET /athletes/{id}/stats
```

---

## 🎯 Exemples d'Utilisation

### Récupérer Plus d'Activités

Modifiez dans `app.py` :
```python
activities = get_activities(page=1, per_page=100)  # Au lieu de 30
```

### Filtrer par Date

Ajoutez dans la fonction `get_activities()` :
```python
from datetime import datetime, timedelta

# Activités des 7 derniers jours
week_ago = (datetime.now() - timedelta(days=7)).timestamp()
ACTIVITIES_URL += f"&after={int(week_ago)}"
```

### Ajouter un Type d'Activité

Dans la condition :
```python
if activity.get("type") in ["Swim", "Ride", "Run", "Walk"]:
    # Traitement
```

---

## 🔐 Sécurité API

### Protection du Token

✅ Token stocké dans `.env` (non committé)  
✅ Token renouvelé automatiquement  
✅ Logs ne montrent pas le secret  

### Rate Limiting Strava

Strava impose des limites :
- **15 minutes** : 100 requêtes
- **24 heures** : 1000 requêtes

L'application actuelle reste largement en dessous de ces limites.

---

## 📊 Performances

### Temps de Réponse Typique

- Renouvellement du token : ~1-2 secondes
- Récupération des activités : ~1-2 secondes
- Génération de la page HTML : <100ms

**Total** : ~3-4 secondes pour le chargement initial

---

**Version** : 1.0.0  
**Dernière mise à jour** : 15 février 2026
