# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Installer gunicorn pour la production
RUN pip install --no-cache-dir gunicorn

# Copier le reste de l'application
COPY . .

# Exposer le port sur lequel l'application va tourner
EXPOSE 8080

# Commande pour démarrer l'application avec gunicorn (1 worker pour économiser la RAM)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
