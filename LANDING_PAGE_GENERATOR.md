# Générateur de Landing Pages

Un outil CLI pour générer des landing pages promotionnelles modernes et responsives.

## 🚀 Installation

Aucune installation supplémentaire requise ! Le générateur utilise des dépendances déjà présentes dans le projet :
- Python 3.x
- Jinja2 (installé avec Flask)

## 📖 Utilisation

### Mode arguments CLI

```bash
python generate_landing_page.py \
  --url "https://myapp.com" \
  --title "MyApp - Best Productivity Tool" \
  --headline "Work Smarter, Not Harder" \
  --description "Join thousands of professionals using MyApp" \
  --cta "Start Free Trial"
```

### Mode fichier de configuration

Créez un fichier `landing_config.json` :

```json
{
  "url": "https://myapp.com",
  "title": "MyApp",
  "headline": "Amazing Product",
  "description": "Transform your workflow",
  "cta": "Get Started",
  "features": [
    "Fast performance",
    "Secure by design",
    "24/7 support"
  ],
  "logo": "./static/logo.png",
  "output": "landing_pages/myapp.html"
}
```

Puis exécutez :

```bash
python generate_landing_page.py --config landing_config.json
```

## 📋 Arguments

### Arguments requis

| Argument | Description |
|----------|-------------|
| `--url` | URL cible du produit/service |
| `--title` | Titre de la page HTML (onglet navigateur) |
| `--headline` | Titre principal affiché |
| `--description` | Description/pitch du produit |

### Arguments optionnels

| Argument | Défaut | Description |
|----------|--------|-------------|
| `--cta` | "Learn More" | Texte du bouton d'action |
| `--output` | "landing_page.html" | Nom du fichier de sortie |
| `--features` | - | Liste de features séparées par virgules |
| `--logo` | - | Chemin vers le logo (encodé en base64) |
| `--gradient-start` | #0f0c29 | Couleur de début du gradient |
| `--gradient-mid` | #302b63 | Couleur du milieu du gradient |
| `--gradient-end` | #24243e | Couleur de fin du gradient |
| `--accent-color` | #667eea | Couleur d'accent (boutons, liens) |
| `--config` | - | Fichier de configuration JSON |

## 💡 Exemples

### Exemple 1 : Landing page basique

```bash
python generate_landing_page.py \
  --url "https://scoringfit.app" \
  --title "ScoringFit" \
  --headline "Track Your Fitness Progress" \
  --description "Connect your Strava account and get insights" \
  --cta "Get Started"
```

### Exemple 2 : Avec liste de features

```bash
python generate_landing_page.py \
  --url "https://myapp.com" \
  --title "MyApp" \
  --headline "Complete Project Management" \
  --description "Everything you need in one place" \
  --cta "Start Free Trial" \
  --features "Task Management,Team Collaboration,Real-time Updates,Mobile Apps" \
  --output "landing_pages/myapp.html"
```

### Exemple 3 : Personnalisation complète avec logo

```bash
python generate_landing_page.py \
  --url "https://brand.com" \
  --title "Brand Name" \
  --headline "Premium Service" \
  --description "Excellence delivered" \
  --logo "./static/logo.png" \
  --gradient-start "#1a1a2e" \
  --gradient-mid "#16213e" \
  --gradient-end "#0f3460" \
  --accent-color "#e94560" \
  --cta "Discover More" \
  --output "landing_pages/brand.html"
```

### Exemple 4 : Override d'un fichier de config

```bash
# Utilise le config mais override le titre et la sortie
python generate_landing_page.py \
  --config landing_config.json \
  --title "New Title" \
  --output "landing_pages/custom.html"
```

## 🎨 Design

Les landing pages générées utilisent le même design moderne que l'application :

- ✨ **Glassmorphism** : Effets de verre avec backdrop-filter
- 🎨 **Gradients** : Arrière-plans animés avec dégradés
- 📱 **Responsive** : Optimisé pour mobile, tablette et desktop
- ⚡ **Animations** : Effets de fade-in et particules animées
- 🎯 **Performance** : HTML autonome avec CSS inline (pas de dépendances externes sauf Google Fonts)

## 📦 Format de sortie

Les landing pages générées sont :

- **Auto-contenues** : Tout le CSS et JavaScript est inline
- **Portables** : Un seul fichier HTML à héberger
- **Optimisées** : Taille réduite (7-10KB sans logo, 100-150KB avec logo)
- **Prêtes pour production** : Peuvent être hébergées immédiatement

## 🔧 Structure du fichier de configuration

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "headline": "Main Headline",
  "description": "Product description",
  "cta": "Call to Action",
  "features": [
    "Feature 1",
    "Feature 2",
    "Feature 3"
  ],
  "logo": "./path/to/logo.png",
  "colors": {
    "gradient_start": "#0f0c29",
    "gradient_mid": "#302b63",
    "gradient_end": "#24243e",
    "accent_color": "#667eea"
  },
  "output": "landing_pages/output.html"
}
```

### Note sur les couleurs

Dans le fichier JSON, utilisez `gradient_start` (avec underscore) plutôt que `gradient-start` (avec tiret).

## ⚠️ Avertissements

### Taille du logo

Si vous utilisez un logo, il sera encodé en base64 et embarqué dans le HTML. Cela augmente la taille du fichier :

- **Recommandé** : Logo < 100KB
- **Format optimal** : SVG (vectoriel, taille réduite)
- **Alternatifs** : PNG ou JPG optimisés

Si votre logo est > 100KB, vous recevrez un avertissement.

### Format des couleurs

Les couleurs doivent être au format hexadécimal :
- ✅ `#667eea` (6 caractères)
- ✅ `#fff` (3 caractères)
- ❌ `rgb(102, 126, 234)` (non supporté)
- ❌ `blue` (non supporté)

## 📁 Fichiers générés

Par défaut, les fichiers sont générés dans le répertoire `landing_pages/` :

```
strava/
├── generate_landing_page.py
├── example_landing_config.json
├── templates/
│   └── landing_page_template.html
└── landing_pages/
    ├── .gitkeep
    ├── test_basic.html
    ├── test_with_features.html
    └── scoringfit_promo.html
```

## 🛠️ Aide

Pour voir toutes les options disponibles :

```bash
python generate_landing_page.py --help
```

## 📝 Exemple complet

Voir le fichier `example_landing_config.json` pour un exemple de configuration complète incluant :
- Logo
- Features
- Couleurs personnalisées
- Textes optimisés

## 🚀 Workflow recommandé

1. **Créer un fichier de configuration** pour chaque produit/service
2. **Générer la landing page** avec `--config`
3. **Tester dans un navigateur** pour vérifier le rendu
4. **Héberger le fichier HTML** sur votre serveur/CDN
5. **Partager l'URL** de la landing page

## 🎯 Use cases

- Landing pages promotionnelles pour produits
- Pages de lancement de nouvelles fonctionnalités
- Pages de capture d'emails
- Pages d'événements ou webinars
- Portfolio de projets
- Pages de téléchargement d'applications

## 🔗 Ressources

- Template source : `templates/landing_page_template.html`
- Design de référence : `templates/index.html`
- Exemple de config : `example_landing_config.json`

---

**Créé avec ❤️ pour le projet ScoringFit**
