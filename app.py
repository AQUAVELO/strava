from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import logging
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from werkzeug.middleware.proxy_fix import ProxyFix

from models import db, User
from auth import StravaAuth
from strava_api import StravaAPI
from google_fit_auth import GoogleFitAuth

# Configuration de Flask
app = Flask(__name__)

# Forcer HTTPS pour les URL externes (important pour OAuth)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config['SECRET_KEY'] = config('SECRET_KEY', default=os.urandom(24).hex())

# Configuration SQLite
# Utiliser un chemin absolu dans le volume persistant /data sur Fly.io
# En local, ce sera dans le dossier courant
if os.environ.get('FLY_APP_NAME'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/strava.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///strava.db'

app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de la base de données
db.init_app(app)

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# Configuration OAuth Strava
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
strava_auth = StravaAuth(CLIENT_ID, CLIENT_SECRET)

# Configuration OAuth Google Fit
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default="")
google_fit_auth = GoogleFitAuth(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Créer les tables au démarrage (uniquement si elles n'existent pas)
with app.app_context():
    try:
        db.create_all()
        logger.info("✅ Base de données initialisée")
    except Exception as e:
        logger.warning(f"⚠️ Avertissement lors de l'initialisation de la base: {e}")
        logger.info("✅ Tables existantes réutilisées")

@app.route("/")
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Inscription avec email/mot de passe"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        
        if not email or not password:
            flash("Email et mot de passe requis", "danger")
            return render_template("register.html")
        
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé", "danger")
            return render_template("register.html")
        
        # Créer le nouvel utilisateur
        user = User(
            email=email,
            firstname=firstname,
            lastname=lastname
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash(f"Bienvenue {user.get_full_name()} ! 🎉", "success")
        return redirect(url_for('dashboard'))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Connexion avec email/mot de passe ou Strava"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Effacer les anciens messages flash accumulés à chaque visite de la page
    if request.method == "GET":
        session.pop('_flashes', None)

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Email et mot de passe requis", "danger")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenue {user.get_full_name()} ! 👋", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Email ou mot de passe incorrect", "danger")
            return render_template("login.html")
    
    return render_template("login.html")

@app.route("/login/strava")
def login_strava():
    """Redirige vers l'authentification Strava"""
    redirect_uri = url_for('auth_callback', _external=True, _scheme='https')
    auth_url = strava_auth.get_authorization_url(redirect_uri)
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    """Callback OAuth Strava"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f"Erreur d'authentification: {error}", "danger")
        return redirect(url_for('index'))
    
    if not code:
        flash("Code d'autorisation manquant", "danger")
        return redirect(url_for('index'))
    
    # Échanger le code contre un token
    token_data = strava_auth.exchange_code_for_token(code)
    
    if not token_data:
        flash("Erreur lors de l'obtention du token Strava", "danger")
        logger.error(f"Échec échange token - Code: {code}")
        return redirect(url_for('index'))
    
    # Si l'utilisateur est déjà connecté, lier son compte Strava
    if current_user.is_authenticated:
        user = strava_auth.create_or_update_user(token_data, existing_user=current_user)
        if user:
            flash(f"Compte Strava lié avec succès ! 🎉", "success")
        else:
            flash("Ce compte Strava est déjà lié à un autre utilisateur", "danger")
        return redirect(url_for('dashboard'))
    
    # Sinon, créer ou mettre à jour l'utilisateur
    user = strava_auth.create_or_update_user(token_data)
    
    if user:
        login_user(user)
        flash(f"Bienvenue {user.get_full_name()} ! 🎉", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Erreur lors de la création du compte", "danger")
        return redirect(url_for('index'))

@app.route("/login/google")
def login_google():
    """Redirige vers l'authentification Google Fit"""
    redirect_uri = url_for('auth_google_callback', _external=True, _scheme='https')
    auth_url = google_fit_auth.get_authorization_url(redirect_uri)
    return redirect(auth_url)

@app.route("/auth/google/callback")
def auth_google_callback():
    """Callback OAuth Google Fit"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f"Erreur d'authentification Google: {error}", "danger")
        return redirect(url_for('index'))
    
    if not code:
        flash("Code d'autorisation Google manquant", "danger")
        return redirect(url_for('index'))
    
    # Échanger le code contre un token
    redirect_uri = url_for('auth_google_callback', _external=True, _scheme='https')
    token_data = google_fit_auth.exchange_code_for_token(code, redirect_uri)
    
    if not token_data:
        flash("Erreur lors de l'obtention du token Google Fit", "danger")
        return redirect(url_for('index'))
    
    # Si l'utilisateur est déjà connecté, lier son compte Google Fit
    if current_user.is_authenticated:
        success = google_fit_auth.link_google_fit_to_user(current_user, token_data)
        if success:
            flash(f"Google Fit lié avec succès ! 🎉", "success")
        else:
            flash("Erreur lors de la liaison de Google Fit", "danger")
        return redirect(url_for('dashboard'))
    
    # Sinon, on doit d'abord créer un compte
    flash("Veuillez d'abord créer un compte, puis lier Google Fit", "warning")
    return redirect(url_for('register'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard utilisateur avec ses activités"""
    logger.info(f"🏠 Dashboard - Utilisateur: {current_user.get_full_name()}")

    # Vérifier si l'utilisateur a un compte Strava lié
    has_strava = current_user.has_strava_linked()

    if not has_strava:
        flash("Liez votre compte Strava pour voir vos activités", "warning")
        return render_template("dashboard.html", user=current_user, activities=[], monthly_totals={}, no_strava=True)

    activities = []

    # Récupérer les activités Strava si lié
    if has_strava:
        access_token = strava_auth.get_valid_token(current_user)
        if access_token:
            strava_api = StravaAPI(access_token)
            activities.extend(strava_api.get_activities(page=1, per_page=30))

    # TODO: Récupérer les activités Google Fit si lié
    # if has_google_fit:
    #     google_token = google_fit_auth.get_valid_token(current_user)
    #     if google_token:
    #         # Ajouter la récupération Google Fit ici
    #         pass

    if not activities:
        logger.info(f"⚠️ Aucune activité récupérée pour {current_user.get_full_name()}")

    # Calculer les statistiques mensuelles (pour Strava)
    if has_strava:
        strava_api = StravaAPI(strava_auth.get_valid_token(current_user))
        monthly_totals = strava_api.calculate_monthly_totals(activities)
    else:
        monthly_totals = {}

    # Calories aujourd'hui et cette semaine
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Lundi
    calories_today = sum(
        (a['calories'] or 0) for a in activities
        if a['start_date'].date() == today
    )
    calories_week = sum(
        (a['calories'] or 0) for a in activities
        if a['start_date'].date() >= week_start
    )

    return render_template(
        "dashboard.html",
        user=current_user,
        activities=activities,
        monthly_totals=monthly_totals,
        no_strava=False,
        calories_today=calories_today,
        calories_week=calories_week,
    )

@app.route("/history")
@login_required
def history():
    """Page d'historique complet des statistiques mensuelles"""
    logger.info(f"📅 History - Utilisateur: {current_user.get_full_name()}")

    # Vérifier si l'utilisateur a un compte Strava lié
    has_strava = current_user.has_strava_linked()

    if not has_strava:
        flash("Liez votre compte Strava pour voir vos statistiques", "warning")
        return redirect(url_for('dashboard'))

    # Récupérer toutes les activités (beaucoup plus que les 30 du dashboard)
    access_token = strava_auth.get_valid_token(current_user)
    if not access_token:
        flash("Erreur d'authentification Strava", "danger")
        return redirect(url_for('dashboard'))

    strava_api = StravaAPI(access_token)

    # Récupérer jusqu'à 200 activités pour avoir un historique plus complet
    activities = []
    for page in range(1, 5):  # Pages 1 à 4 (200 activités max)
        page_activities = strava_api.get_activities(page=page, per_page=50)
        if not page_activities:
            break
        activities.extend(page_activities)

    if not activities:
        logger.info(f"⚠️ Aucune activité récupérée pour {current_user.get_full_name()}")
        flash("Aucune activité trouvée", "info")
        return redirect(url_for('dashboard'))

    # Calculer les statistiques mensuelles
    monthly_totals = strava_api.calculate_monthly_totals(activities)

    return render_template(
        "history.html",
        user=current_user,
        monthly_totals=monthly_totals,
        total_activities=len(activities)
    )

@app.route("/logout")
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash("Vous avez été déconnecté", "info")
    return redirect(url_for('index'))

@app.route("/support", methods=["GET", "POST"])
def support():
    """Page de support / aide"""
    # Effacer les anciens messages flash accumulés
    if request.method == "GET":
        session.pop('_flashes', None)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sender_email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        try:
            msg = MIMEMultipart()
            msg["From"] = "noreply@scoringfit.fr"
            msg["To"] = "aqua.cannes@gmail.com"
            msg["Subject"] = f"[ScoringFit Support] {subject}"
            body = f"Nom : {name}\nEmail : {sender_email}\nSujet : {subject}\n\nMessage :\n{message}"
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(
                    config("MAIL_USER", default="aqua.cannes@gmail.com"),
                    config("MAIL_PASSWORD", default="")
                )
                smtp.sendmail(msg["From"], msg["To"], msg.as_string())

            flash("✅ Message envoyé ! Nous vous répondrons dans les 48h.", "alert-success")
        except Exception as e:
            logger.error(f"Erreur envoi email support: {e}")
            flash(f"✉️ Message reçu ! Vous pouvez aussi nous écrire directement à aqua.cannes@gmail.com", "alert-success")

        return redirect(url_for("support"))

    return render_template("support.html")

@app.route("/send-activity-email", methods=["POST"])
@login_required
def send_activity_email():
    """Envoie les résultats d'une séance par email à l'utilisateur"""
    # Récupérer les données du formulaire
    activity_name  = request.form.get("activity_name", "")
    activity_type  = request.form.get("activity_type", "")
    activity_date  = request.form.get("activity_date", "")
    distance       = request.form.get("distance", "")
    duration       = request.form.get("duration", "")
    calories       = request.form.get("calories", "")
    avg_hr         = request.form.get("avg_hr", "")
    max_hr         = request.form.get("max_hr", "")
    time_50m       = request.form.get("time_50m", "")

    recipient = current_user.email
    prenom    = current_user.firstname or current_user.get_full_name()

    # Construction des lignes de stats
    stats_rows = ""
    if distance:
        stats_rows += f"<tr><td style='padding:10px 16px;color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Distance</td><td style='padding:10px 16px;color:#f0f2f8;font-size:18px;font-weight:700;'>{distance}</td></tr>"
    if duration:
        stats_rows += f"<tr><td style='padding:10px 16px;color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Durée</td><td style='padding:10px 16px;color:#f0f2f8;font-size:18px;font-weight:700;'>{duration}</td></tr>"
    if calories:
        stats_rows += f"<tr style='background:rgba(255,255,255,0.03)'><td style='padding:10px 16px;color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Calories</td><td style='padding:10px 16px;color:#f0f2f8;font-size:18px;font-weight:700;'>{calories} kcal</td></tr>"
    if time_50m:
        stats_rows += f"<tr><td style='padding:10px 16px;color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>Temps / 50m</td><td style='padding:10px 16px;color:#f0f2f8;font-size:18px;font-weight:700;'>{time_50m}</td></tr>"
    if avg_hr:
        hr_text = f"Moy {avg_hr}"
        if max_hr:
            hr_text += f" · Max {max_hr}"
        stats_rows += f"<tr style='background:rgba(239,71,111,0.08)'><td style='padding:10px 16px;color:#ef476f;font-size:13px;text-transform:uppercase;letter-spacing:1px;'>❤️ Pulsations / min</td><td style='padding:10px 16px;color:#f0f2f8;font-size:18px;font-weight:700;'>{hr_text}</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#07090f;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#07090f;padding:40px 20px;">
        <tr><td align="center">
          <table width="580" cellpadding="0" cellspacing="0" style="background:#0f1220;border-radius:20px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">

            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg,#FF5733,#FF8C42);padding:32px 36px;">
                <p style="margin:0;color:rgba(255,255,255,0.8);font-size:12px;text-transform:uppercase;letter-spacing:2px;">ScoringFit · Résultat de séance</p>
                <h1 style="margin:8px 0 0;color:#fff;font-size:26px;font-weight:800;letter-spacing:-0.5px;">{activity_name}</h1>
                <p style="margin:6px 0 0;color:rgba(255,255,255,0.75);font-size:14px;">{activity_type} &nbsp;·&nbsp; {activity_date}</p>
              </td>
            </tr>

            <!-- Intro -->
            <tr>
              <td style="padding:28px 36px 8px;">
                <p style="margin:0;color:#9ca3af;font-size:15px;line-height:1.6;">
                  Bonjour <strong style="color:#f0f2f8;">{prenom}</strong>,<br>
                  voici le récapitulatif de ta séance du {activity_date}.
                </p>
              </td>
            </tr>

            <!-- Stats -->
            <tr>
              <td style="padding:16px 36px 32px;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.04);border-radius:14px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">
                  {stats_rows}
                </table>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="padding:20px 36px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
                <p style="margin:0;color:#6b7280;font-size:12px;">ScoringFit · Propulsé par Strava</p>
              </td>
            </tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = "noreply@scoringfit.fr"
        msg["To"]      = recipient
        msg["Subject"] = f"Ta séance : {activity_name} – {activity_date}"
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(
                config("MAIL_USER", default="aqua.cannes@gmail.com"),
                config("MAIL_PASSWORD", default="")
            )
            smtp.sendmail(msg["From"], recipient, msg.as_string())

        flash(f"✅ Email envoyé à {recipient}", "success")
    except Exception as e:
        logger.error(f"Erreur envoi email séance: {e}")
        flash("❌ Impossible d'envoyer l'email, vérifiez la configuration SMTP.", "danger")

    return redirect(url_for("dashboard"))


@app.route("/profile")
@login_required
def profile():
    """Profil utilisateur"""
    return render_template("profile.html", user=current_user)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False") == "True"
    
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
