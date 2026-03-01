#!/bin/bash

# Script de déploiement automatique sur Fly.io

echo "🚀 Script de Déploiement Fly.io - Application Strava"
echo "=================================================="
echo ""

# Vérifier que flyctl est installé
if ! command -v flyctl &> /dev/null; then
    echo "❌ Erreur : flyctl n'est pas installé"
    echo ""
    echo "Installez-le avec :"
    echo "  macOS : brew install flyctl"
    echo "  Linux/macOS : curl -L https://fly.io/install.sh | sh"
    exit 1
fi

echo "✅ flyctl est installé"

# Vérifier que l'utilisateur est connecté
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Erreur : Vous n'êtes pas connecté à Fly.io"
    echo ""
    echo "Connectez-vous avec :"
    echo "  flyctl auth login"
    exit 1
fi

echo "✅ Connecté à Fly.io"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Erreur : Fichier app.py introuvable"
    echo "Assurez-vous d'être dans le répertoire de l'application"
    exit 1
fi

echo "✅ Répertoire correct"

# Vérifier que le Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo "❌ Erreur : Dockerfile introuvable"
    echo "Le Dockerfile devrait avoir été créé automatiquement"
    exit 1
fi

echo "✅ Dockerfile présent"

# Vérifier que fly.toml existe
if [ ! -f "fly.toml" ]; then
    echo "❌ Erreur : fly.toml introuvable"
    exit 1
fi

echo "✅ fly.toml présent"
echo ""

# Demander si les secrets ont été configurés
echo "⚠️  IMPORTANT : Avez-vous configuré vos secrets Fly.io ?"
echo ""
echo "Si ce n'est pas fait, exécutez d'abord :"
echo "  flyctl secrets set CLIENT_ID=149497"
echo "  flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d"
echo "  flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7"
echo "  flyctl secrets set INDEX_URL=https://votre-domaine.com/index"
echo ""
read -p "Les secrets sont-ils configurés ? (o/n) : " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Veuillez d'abord configurer les secrets, puis relancez ce script"
    exit 1
fi

echo "✅ Secrets configurés"
echo ""

# Vérifier si Git est initialisé
if [ ! -d ".git" ]; then
    echo "📦 Initialisation de Git..."
    git init
    git add .
    git commit -m "Initial commit - Application Strava Flask"
    echo "✅ Git initialisé et premier commit effectué"
else
    echo "📦 Git déjà initialisé"
    
    # Vérifier s'il y a des changements
    if [[ -n $(git status -s) ]]; then
        echo "📝 Changements détectés, commit en cours..."
        git add .
        read -p "Message de commit : " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Mise à jour application"
        fi
        git commit -m "$commit_msg"
        echo "✅ Commit effectué"
    else
        echo "✅ Aucun changement à commiter"
    fi
fi

echo ""
echo "🚀 Déploiement sur Fly.io..."
echo ""

# Déployer l'application
flyctl deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "🎉 Déploiement réussi !"
    echo "=================================================="
    echo ""
    echo "Votre application est maintenant en ligne !"
    echo ""
    echo "Commandes utiles :"
    echo "  flyctl open       - Ouvrir l'application dans le navigateur"
    echo "  flyctl logs       - Voir les logs en temps réel"
    echo "  flyctl status     - Voir le statut de l'application"
    echo ""
    
    # Proposer d'ouvrir l'application
    read -p "Voulez-vous ouvrir l'application dans le navigateur ? (o/n) : " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        flyctl open
    fi
else
    echo ""
    echo "=================================================="
    echo "❌ Erreur lors du déploiement"
    echo "=================================================="
    echo ""
    echo "Consultez les logs pour plus d'informations :"
    echo "  flyctl logs"
    echo ""
    exit 1
fi
