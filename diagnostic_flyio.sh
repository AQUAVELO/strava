#!/bin/bash

# Script de Diagnostic et Déploiement Fly.io
# Résout l'erreur : "Could not find a Dockerfile"

echo "🔍 DIAGNOSTIC FLY.IO - Application Strava"
echo "=========================================="
echo ""

# 1. Vérifier le répertoire
echo "📁 Étape 1 : Vérification du répertoire..."
CURRENT_DIR=$(pwd)
echo "   Répertoire actuel : $CURRENT_DIR"

if [[ ! "$CURRENT_DIR" == *"strava"* ]]; then
    echo "   ⚠️  Vous n'êtes pas dans le répertoire strava"
    echo "   Allez dans le bon répertoire :"
    echo "   cd /Applications/MAMP/htdocs/strava"
    exit 1
fi
echo "   ✅ Répertoire correct"
echo ""

# 2. Vérifier les fichiers essentiels
echo "📦 Étape 2 : Vérification des fichiers..."

if [ ! -f "Dockerfile" ]; then
    echo "   ❌ ERREUR : Dockerfile introuvable !"
    echo "   Le Dockerfile devrait être dans : $(pwd)"
    exit 1
fi
echo "   ✅ Dockerfile trouvé ($(wc -c < Dockerfile) octets)"

if [ ! -f "fly.toml" ]; then
    echo "   ❌ ERREUR : fly.toml introuvable !"
    exit 1
fi
echo "   ✅ fly.toml trouvé"

if [ ! -f "app.py" ]; then
    echo "   ❌ ERREUR : app.py introuvable !"
    exit 1
fi
echo "   ✅ app.py trouvé"

if [ ! -f "requirements.txt" ]; then
    echo "   ❌ ERREUR : requirements.txt introuvable !"
    exit 1
fi
echo "   ✅ requirements.txt trouvé"
echo ""

# 3. Afficher le contenu du Dockerfile
echo "📄 Étape 3 : Contenu du Dockerfile..."
echo "----------------------------------------"
head -5 Dockerfile
echo "   ..."
echo "----------------------------------------"
echo ""

# 4. Vérifier flyctl
echo "🔧 Étape 4 : Vérification de flyctl..."
if ! command -v flyctl &> /dev/null; then
    echo "   ❌ flyctl n'est pas installé"
    echo ""
    echo "   Installez-le avec :"
    echo "   brew install flyctl"
    exit 1
fi
echo "   ✅ flyctl installé : $(flyctl version | head -1)"
echo ""

# 5. Vérifier la connexion
echo "🔐 Étape 5 : Vérification de la connexion Fly.io..."
if ! flyctl auth whoami &> /dev/null; then
    echo "   ❌ Non connecté à Fly.io"
    echo ""
    echo "   Connectez-vous avec :"
    echo "   flyctl auth login"
    exit 1
fi
echo "   ✅ Connecté à Fly.io : $(flyctl auth whoami)"
echo ""

# 6. Vérifier si l'app existe déjà
echo "🔍 Étape 6 : Vérification de l'application..."
APP_NAME=$(grep "^app = " fly.toml | cut -d'"' -f2)
echo "   Nom de l'app dans fly.toml : $APP_NAME"

if flyctl status -a "$APP_NAME" &> /dev/null; then
    echo "   ⚠️  L'application '$APP_NAME' existe déjà sur Fly.io"
    echo ""
    read -p "   Voulez-vous redéployer l'app existante ? (o/n) : " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo ""
        echo "🚀 REDÉPLOIEMENT DE L'APPLICATION..."
        echo "=========================================="
        flyctl deploy
        exit $?
    else
        echo ""
        echo "   Changez le nom de l'app dans fly.toml, puis relancez ce script"
        exit 1
    fi
else
    echo "   ✅ L'application n'existe pas encore (nouveau déploiement)"
fi
echo ""

# 7. Proposer le déploiement
echo "=========================================="
echo "🎯 TOUT EST PRÊT POUR LE DÉPLOIEMENT !"
echo "=========================================="
echo ""
echo "Fichiers vérifiés :"
echo "  ✅ Dockerfile"
echo "  ✅ fly.toml"
echo "  ✅ app.py"
echo "  ✅ requirements.txt"
echo ""
echo "Environnement :"
echo "  ✅ flyctl installé"
echo "  ✅ Connecté à Fly.io"
echo "  ✅ Répertoire correct"
echo ""

read -p "Voulez-vous déployer maintenant ? (o/n) : " -n 1 -r
echo ""
echo ""

if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Déploiement annulé"
    echo ""
    echo "Pour déployer plus tard, exécutez :"
    echo "   flyctl deploy"
    exit 0
fi

# 8. Vérifier les secrets
echo "🔐 Vérification des secrets..."
SECRET_COUNT=$(flyctl secrets list -a "$APP_NAME" 2>/dev/null | grep -c "CLIENT_ID\|CLIENT_SECRET\|REFRESH_TOKEN")

if [ "$SECRET_COUNT" -lt 3 ]; then
    echo "   ⚠️  Les secrets ne sont pas tous configurés"
    echo ""
    echo "   Configurez-les maintenant avec ces commandes :"
    echo ""
    echo "   flyctl secrets set CLIENT_ID=149497"
    echo "   flyctl secrets set CLIENT_SECRET=ce7f00ae80b9cfa3ca9cd503b15c73c368a3c97d"
    echo "   flyctl secrets set REFRESH_TOKEN=1fc5f46d8e959312e0b994af8d2e1f57ac419cf7"
    echo "   flyctl secrets set INDEX_URL=https://votre-domaine.com/index"
    echo ""
    read -p "   Les avez-vous configurés ? (o/n) : " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        echo "   ❌ Veuillez configurer les secrets d'abord"
        exit 1
    fi
fi
echo ""

# 9. Déploiement
echo "🚀 DÉPLOIEMENT EN COURS..."
echo "=========================================="
echo ""

# Utiliser directement flyctl deploy (pas launch)
flyctl deploy --config fly.toml

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "🎉 DÉPLOIEMENT RÉUSSI !"
    echo "=========================================="
    echo ""
    echo "Votre application est maintenant en ligne !"
    echo ""
    echo "URL : https://$APP_NAME.fly.dev"
    echo ""
    echo "Commandes utiles :"
    echo "  flyctl open       - Ouvrir dans le navigateur"
    echo "  flyctl logs       - Voir les logs"
    echo "  flyctl status     - Vérifier le statut"
    echo ""
    
    read -p "Ouvrir l'application maintenant ? (o/n) : " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        flyctl open
    fi
else
    echo ""
    echo "=========================================="
    echo "❌ ERREUR DE DÉPLOIEMENT"
    echo "=========================================="
    echo ""
    echo "Consultez les logs ci-dessus pour plus de détails"
    echo ""
    exit 1
fi
