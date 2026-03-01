from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentification classique
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Null si connexion Strava uniquement
    
    # Profil
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    profile_photo = db.Column(db.String(500))
    
    # Strava OAuth (optionnel - peut être lié plus tard)
    strava_id = db.Column(db.BigInteger, unique=True, nullable=True)
    access_token = db.Column(db.String(255), nullable=True)
    refresh_token = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.BigInteger, nullable=True)
    
    # Google Fit OAuth (optionnel - peut être lié plus tard)
    google_fit_token = db.Column(db.String(500), nullable=True)
    google_fit_refresh_token = db.Column(db.String(500), nullable=True)
    google_fit_expires_at = db.Column(db.BigInteger, nullable=True)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    activities = db.relationship('Activity', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email} (Strava ID: {self.strava_id})>'
    
    def get_full_name(self):
        return f"{self.firstname} {self.lastname}".strip() if self.firstname or self.lastname else self.email.split('@')[0]
    
    def set_password(self, password):
        """Définir le mot de passe (hashé)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifier le mot de passe"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def has_strava_linked(self):
        """Vérifie si un compte Strava est lié"""
        return self.strava_id is not None
    
    def has_google_fit_linked(self):
        """Vérifie si un compte Google Fit est lié"""
        return self.google_fit_token is not None


class Activity(db.Model):
    """Modèle activité (cache local)"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strava_activity_id = db.Column(db.BigInteger, unique=True, nullable=False)
    
    # Données de l'activité
    type = db.Column(db.String(50), nullable=False)  # Swim, Ride, Run
    name = db.Column(db.String(255))
    distance = db.Column(db.Float)  # en mètres
    moving_time = db.Column(db.Integer)  # en secondes
    elapsed_time = db.Column(db.Integer)
    total_elevation_gain = db.Column(db.Float)
    
    # Statistiques
    calories = db.Column(db.Float)
    average_speed = db.Column(db.Float)
    max_speed = db.Column(db.Float)
    average_heartrate = db.Column(db.Float)
    max_heartrate = db.Column(db.Float)
    
    # Natation spécifique
    time_per_50m = db.Column(db.Float)
    best_time_per_50m = db.Column(db.Float)
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False)
    start_date_local = db.Column(db.DateTime)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Activity {self.name} ({self.type})>'
