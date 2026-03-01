import requests
import time
from flask import url_for
from models import db, User
import logging

logger = logging.getLogger(__name__)

class GoogleFitAuth:
    """Gestion de l'authentification OAuth Google Fit"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.scopes = [
            "https://www.googleapis.com/auth/fitness.activity.read",
            "https://www.googleapis.com/auth/fitness.location.read",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
    
    def get_authorization_url(self, redirect_uri):
        """Génère l'URL d'autorisation Google Fit"""
        scope_string = " ".join(self.scopes)
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope_string,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        query_string = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Échange le code d'autorisation contre un access_token"""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(self.token_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Token Google Fit obtenu")
                return data
            else:
                logger.error(f"❌ Erreur échange token Google Fit: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"⚠️ Exception échange token Google Fit: {e}")
            return None
    
    def refresh_access_token(self, refresh_token):
        """Rafraîchit l'access_token avec le refresh_token"""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(self.token_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Access token Google Fit rafraîchi")
                return data
            else:
                logger.error(f"❌ Erreur refresh token Google Fit: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"⚠️ Exception refresh token Google Fit: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Récupère les informations de profil de l'utilisateur"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erreur récupération profil Google: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"⚠️ Exception récupération profil Google: {e}")
            return None
    
    def link_google_fit_to_user(self, user, token_data):
        """Lie Google Fit à un utilisateur existant"""
        try:
            # Récupérer les infos utilisateur Google
            user_info = self.get_user_info(token_data['access_token'])
            
            if not user_info:
                logger.error("❌ Impossible de récupérer les infos utilisateur Google")
                return False
            
            # Stocker les tokens Google Fit dans les colonnes Strava temporairement
            # (On pourrait créer de nouvelles colonnes spécifiques à Google Fit plus tard)
            user.google_fit_token = token_data['access_token']
            user.google_fit_refresh_token = token_data.get('refresh_token')
            
            # Calculer l'expiration
            expires_in = token_data.get('expires_in', 3600)
            user.google_fit_expires_at = int(time.time()) + expires_in
            
            # Mettre à jour le profil si vide
            if not user.firstname and user_info.get('given_name'):
                user.firstname = user_info.get('given_name', '')
            if not user.lastname and user_info.get('family_name'):
                user.lastname = user_info.get('family_name', '')
            if not user.profile_photo and user_info.get('picture'):
                user.profile_photo = user_info.get('picture', '')
            
            db.session.commit()
            logger.info(f"✅ Google Fit lié à l'utilisateur: {user.email}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erreur liaison Google Fit: {e}")
            return False
    
    def get_valid_token(self, user):
        """Retourne un access_token Google Fit valide"""
        # Vérifier si le token a expiré
        if not hasattr(user, 'google_fit_expires_at') or time.time() >= user.google_fit_expires_at:
            logger.info("🔄 Token Google Fit expiré, rafraîchissement...")
            
            if not hasattr(user, 'google_fit_refresh_token'):
                logger.error("❌ Pas de refresh token Google Fit")
                return None
            
            token_data = self.refresh_access_token(user.google_fit_refresh_token)
            
            if token_data:
                user.google_fit_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                user.google_fit_expires_at = int(time.time()) + expires_in
                
                # Mettre à jour le refresh token s'il est fourni
                if 'refresh_token' in token_data:
                    user.google_fit_refresh_token = token_data['refresh_token']
                
                db.session.commit()
                return user.google_fit_token
            else:
                logger.error("❌ Impossible de rafraîchir le token Google Fit")
                return None
        
        return user.google_fit_token if hasattr(user, 'google_fit_token') else None
