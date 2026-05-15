# Photo → Vidéo AI

Application Flask qui transforme une description (et optionnellement une photo) en vidéo cinématique via **Claude** + **Higgsfield AI**.

## Fonctionnement

```
Description utilisateur
        │
        ▼
  Claude Sonnet 4.6            ← optimise le prompt
        │
        ▼
  Higgsfield API               ← génère la vidéo (5 s, 24 fps)
  (image-to-video ou
   text-to-video)
        │
        ▼
  Vidéo affichée dans le navigateur
```

## Installation

```bash
cd video_app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Remplir ANTHROPIC_API_KEY et HIGGSFIELD_API_KEY dans .env
```

## Clés API

| Service | Où l'obtenir |
|---------|-------------|
| Anthropic (Claude) | https://console.anthropic.com |
| Higgsfield | https://cloud.higgsfield.ai |

## Lancement

```bash
python app.py
# → http://localhost:5001
```

Production :
```bash
gunicorn -w 2 -b 0.0.0.0:5001 app:app
```

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Clé Anthropic pour Claude |
| `HIGGSFIELD_API_KEY` | Clé Higgsfield (format `key:secret` ou clé unique) |
| `PORT` | Port HTTP (défaut : 5001) |
| `FLASK_DEBUG` | Mode debug (true/false) |
