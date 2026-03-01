import requests
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

# Icônes et labels pour chaque type d'activité Strava
ACTIVITY_TYPES = {
    "Swim":             {"label": "Natation",        "icon": "🏊‍♂️", "css": "swim"},
    "Ride":             {"label": "Vélo",             "icon": "🚴‍♂️", "css": "ride"},
    "Run":              {"label": "Course",           "icon": "🏃‍♂️", "css": "run"},
    "Walk":             {"label": "Marche",           "icon": "🚶‍♂️", "css": "walk"},
    "Hike":             {"label": "Randonnée",        "icon": "🥾",   "css": "hike"},
    "WeightTraining":   {"label": "Musculation",      "icon": "🏋️",   "css": "weight"},
    "Workout":          {"label": "Entraînement",     "icon": "💪",   "css": "workout"},
    "Yoga":             {"label": "Yoga",             "icon": "🧘",   "css": "yoga"},
    "Elliptical":       {"label": "Aquavelo",         "icon": "🚴💧", "css": "ride"},
    "EBikeRide":        {"label": "Vélo électrique",  "icon": "⚡🚴", "css": "ride"},
    "VirtualRide":      {"label": "Vélo virtuel",     "icon": "🖥️🚴", "css": "ride"},
    "VirtualRun":       {"label": "Course virtuelle", "icon": "🖥️🏃", "css": "run"},
    "NordicSki":        {"label": "Ski nordique",     "icon": "⛷️",   "css": "ski"},
    "AlpineSki":        {"label": "Ski alpin",        "icon": "🎿",   "css": "ski"},
    "Snowboard":        {"label": "Snowboard",        "icon": "🏂",   "css": "ski"},
    "Kayaking":         {"label": "Kayak",            "icon": "🛶",   "css": "swim"},
    "Rowing":           {"label": "Aviron",           "icon": "🚣",   "css": "swim"},
    "StandUpPaddling":  {"label": "Stand Up Paddle",  "icon": "🏄",   "css": "swim"},
    "Surfing":          {"label": "Surf",             "icon": "🏄‍♂️", "css": "swim"},
    "IceSkate":         {"label": "Patinage",         "icon": "⛸️",   "css": "walk"},
    "InlineSkate":      {"label": "Roller",           "icon": "🛼",   "css": "ride"},
    "RockClimbing":     {"label": "Escalade",         "icon": "🧗",   "css": "workout"},
    "Golf":             {"label": "Golf",             "icon": "⛳",   "css": "walk"},
    "Soccer":           {"label": "Football",         "icon": "⚽",   "css": "workout"},
    "Tennis":           {"label": "Tennis",           "icon": "🎾",   "css": "workout"},
    "Other":            {"label": "Autre",            "icon": "🏅",   "css": "other"},
}

class StravaAPI:
    """Client pour l'API Strava"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"
    
    def get_activities(self, page=1, per_page=30):
        """Récupère les activités de l'utilisateur"""
        url = f"{self.base_url}/athlete/activities"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {'page': page, 'per_page': per_page}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                activities = response.json()
                logger.info(f"📥 {len(activities)} activités récupérées")
                return self._process_activities(activities)
            else:
                logger.error(f"❌ Erreur API: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"⚠️ Exception get_activities: {e}")
            return []
    
    def _process_activities(self, activities):
        """Traite toutes les activités sans filtre de type"""
        filtered_activities = []
        seen_ids = set()
        seen_signatures = set()
        swim_times_by_date = defaultdict(list)
        
        for activity in activities:
            activity_type = activity.get("sport_type") or activity.get("type", "Other")
            activity_id = activity.get("id")
            
            start_date = datetime.strptime(
                activity.get("start_date_local"), "%Y-%m-%dT%H:%M:%SZ"
            )
            signature = (activity_type, start_date.date(), activity.get("distance"))
            
            if activity_id in seen_ids or signature in seen_signatures:
                continue

            seen_ids.add(activity_id)
            seen_signatures.add(signature)

            type_info = ACTIVITY_TYPES.get(activity_type, {"label": activity_type, "icon": "🏅", "css": "other"})

            # Remplacer "Vélo elliptique" par "Aquavelo" dans le nom
            activity_name = activity.get("name", "")
            if activity_name:
                activity_name = activity_name.replace("Vélo elliptique", "Aquavelo")
                activity_name = activity_name.replace("vélo elliptique", "Aquavelo")
                activity_name = activity_name.replace("VÉLO ELLIPTIQUE", "AQUAVELO")
                activity_name = activity_name.replace("Velo elliptique", "Aquavelo")
                activity_name = activity_name.replace("velo elliptique", "Aquavelo")

            # Calculer les calories (+5% pour Aquavelo/Elliptical)
            calories = activity.get("calories") or self._estimate_calories(activity)
            if activity_type == "Elliptical":
                calories = int(calories * 1.05)  # Majoration de 5%

            activity_data = {
                "id": activity_id,
                "type": activity_type,
                "type_label": type_info["label"],
                "type_icon": type_info["icon"],
                "type_css": type_info["css"],
                "name": activity_name,
                "distance": activity.get("distance", 0),
                "moving_time": activity.get("moving_time", 0),
                "elapsed_time": activity.get("elapsed_time", 0),
                "total_elevation_gain": activity.get("total_elevation_gain", 0),
                "calories": calories,
                "start_date": start_date,
                "average_speed": activity.get("average_speed", 0),
                "max_speed": activity.get("max_speed", 0),
                "average_heartrate": activity.get("average_heartrate", None),
                "max_heartrate": activity.get("max_heartrate", None),
                "time_per_50m": None,
                "best_time_per_50m": None,
            }

            if activity_type == "Swim" and activity_data["distance"] > 0:
                time_per_50m = activity_data["moving_time"] / (activity_data["distance"] / 50)
                activity_data["time_per_50m"] = time_per_50m
                swim_times_by_date[start_date.strftime("%Y-%m-%d")].append(time_per_50m)

            filtered_activities.append(activity_data)
        
        best_times_by_date = {d: min(t) for d, t in swim_times_by_date.items()}
        for activity in filtered_activities:
            if activity["type"] == "Swim":
                activity["best_time_per_50m"] = best_times_by_date.get(
                    activity["start_date"].strftime("%Y-%m-%d")
                )
        
        return filtered_activities
    
    def _estimate_calories(self, activity):
        """Estime les calories brûlées"""
        moving_time = activity.get("moving_time", 0)
        rates = {"Swim": 400, "Ride": 600, "Run": 800, "Walk": 300, "Hike": 400, "WeightTraining": 350}
        rate = rates.get(activity.get("sport_type") or activity.get("type"), 300)
        return int(rate * (moving_time / 3600))
    
    def calculate_monthly_totals(self, activities):
        """Calcule les totaux mensuels par sport"""
        monthly_totals = defaultdict(lambda: defaultdict(lambda: {"distance": 0, "moving_time": 0}))
        
        for activity in activities:
            month_year = activity["start_date"].strftime("%Y-%m")
            activity_type = activity["type"]
            monthly_totals[month_year][activity_type]["distance"] += activity["distance"] / 1000
            monthly_totals[month_year][activity_type]["moving_time"] += activity["moving_time"] / 3600
        
        return monthly_totals
