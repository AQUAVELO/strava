import requests
import time
from flask import url_for, session
from models import db, User
import logging

logger = logging.getLogger(__name__)

class StravaAuth:
    """Gestion de l'authentification OAuth Strava"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://www.strava.com/oauth/authorize"
        self.token_url = "https://www.strava.com/oauth/token"
    
    def get_authorization_url(self, redirect_uri):
        """
        Génère l'URL d'autorisation Strava
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'read,activity:read_all,profile:read_all'
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    def exchange_code_for_token(self, code):
        """
        Échange le code d'autorisation contre un access_token
        """
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(self.token_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Token obtenu pour l'athlète {data.get('athlete', {}).get('id')}")
                return data
            else:
                logger.error(f"❌ Erreur échange token: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"⚠️ Exception échange token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token):
        """
        Rafraîchit l'access_token avec le refresh_token
        """
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
                logger.info("✅ Access token rafraîchi")
                return data
            else:
                logger.error(f"❌ Erreur refresh token: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"⚠️ Exception refresh token: {e}")
            return None
    
    def create_or_update_user(self, token_data, existing_user=None):
        """
        Crée ou met à jour un utilisateur à partir des données Strava
        Si existing_user est fourni, lie le compte Strava à cet utilisateur
        """
        athlete = token_data.get('athlete', {})
        strava_id = athlete.get('id')
        
        if not strava_id:
            logger.error("❌ Pas de strava_id dans les données")
            return None
        
        # Si un utilisateur existant est fourni, lier son compte Strava
        if existing_user:
            # Vérifier si ce strava_id est déjà lié à un autre utilisateur
            existing_strava_user = User.query.filter_by(strava_id=strava_id).first()
            
            if existing_strava_user and existing_strava_user.id != existing_user.id:
                logger.error(f"❌ Ce compte Strava est déjà lié à un autre utilisateur")
                return None
            
            existing_user.strava_id = strava_id
            existing_user.access_token = token_data['access_token']
            existing_user.refresh_token = token_data['refresh_token']
            existing_user.expires_at = token_data['expires_at']
            
            # Mettre à jour le profil si vide
            if not existing_user.firstname:
                existing_user.firstname = athlete.get('firstname', '')
            if not existing_user.lastname:
                existing_user.lastname = athlete.get('lastname', '')
            if not existing_user.profile_photo:
                existing_user.profile_photo = athlete.get('profile', '')
            
            try:
                db.session.commit()
                logger.info(f"✅ Compte Strava lié à l'utilisateur: {existing_user.email}")
                return existing_user
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ Erreur lors de la liaison du compte Strava: {e}")
                return None
        
        # Chercher l'utilisateur existant par strava_id
        user = User.query.filter_by(strava_id=strava_id).first()
        
        if user:
            # Mettre à jour les tokens
            user.access_token = token_data['access_token']
            user.refresh_token = token_data['refresh_token']
            user.expires_at = token_data['expires_at']
            logger.info(f"✅ Utilisateur mis à jour: {user.get_full_name()}")
        else:
            # Créer un nouvel utilisateur (connexion Strava uniquement)
            email = athlete.get('email', f"strava_{strava_id}@temp.com")
            
            user = User(
                email=email,
                strava_id=strava_id,
                firstname=athlete.get('firstname', ''),
                lastname=athlete.get('lastname', ''),
                profile_photo=athlete.get('profile', ''),
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_at=token_data['expires_at']
            )
            db.session.add(user)
            logger.info(f"✅ Nouvel utilisateur créé: {user.get_full_name()}")
        
        db.session.commit()
        return user
    
    def get_valid_token(self, user):
        """
        Retourne un access_token valide, le rafraîchit si nécessaire
        """
        # Vérifier si le token a expiré
        if time.time() >= user.expires_at:
            logger.info("🔄 Token expiré, rafraîchissement...")
            token_data = self.refresh_access_token(user.refresh_token)
            
            if token_data:
                user.access_token = token_data['access_token']
                user.refresh_token = token_data['refresh_token']
                user.expires_at = token_data['expires_at']
                db.session.commit()
                return user.access_token
            else:
                logger.error("❌ Impossible de rafraîchir le token")
                return None
        
        return user.access_token
