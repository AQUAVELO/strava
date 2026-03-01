#!/bin/bash

# Script de vérification de l'installation

echo "🔍 Vérification de l'installation de l'application Strava..."
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Erreur : Vous n'êtes pas dans le bon répertoire"
    echo "📁 Allez dans : cd /Applications/MAMP/htdocs/strava"
    exit 1
fi

echo "✅ Répertoire correct"

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Erreur : L'environnement virtuel n'existe pas"
    exit 1
fi

echo "✅ Environnement virtuel présent"

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo "❌ Erreur : Le fichier .env n'existe pas"
    exit 1
fi

echo "✅ Fichier .env présent"

# Vérifier les templates
if [ ! -f "templates/index.html" ]; then
    echo "❌ Erreur : Le template HTML n'existe pas"
    exit 1
fi

echo "✅ Template HTML présent"

# Activer l'environnement et vérifier Flask
source venv/bin/activate

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Erreur : Flask n'est pas installé"
    echo "🔧 Exécutez : pip install Flask requests python-decouple"
    exit 1
fi

echo "✅ Flask installé"

if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ Erreur : Requests n'est pas installé"
    exit 1
fi

echo "✅ Requests installé"

if ! python3 -c "from decouple import config" 2>/dev/null; then
    echo "❌ Erreur : Python-decouple n'est pas installé"
    exit 1
fi

echo "✅ Python-decouple installé"

echo ""
echo "🎉 Toutes les vérifications sont passées avec succès !"
echo ""
echo "📊 Récapitulatif :"
echo "   - Application Flask : ✅"
echo "   - Environnement virtuel : ✅"
echo "   - Dépendances : ✅"
echo "   - Configuration : ✅"
echo "   - Templates : ✅"
echo ""
echo "🚀 Vous pouvez maintenant lancer l'application avec :"
echo "   ./start.sh"
echo ""
echo "🌐 L'application sera accessible sur : http://127.0.0.1:5000"
echo ""
