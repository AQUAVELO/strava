# Photo → Vidéo AI (Higgsfield scraper)

Application Flask qui transforme une description + photo optionnelle en vidéo cinématique.

**Pipeline :**
```
Description utilisateur
        │
        ▼
  Claude Sonnet 4.6        ← optimise le prompt en 2-4 phrases cinématiques
        │
        ▼
  Playwright (Chromium)    ← ouvre higgsfield.ai, se connecte, colle le prompt,
                              upload l'image, clique Générer, récupère l'URL vidéo
        │
        ▼
  URL vidéo → lecteur intégré + téléchargement
```

## Installation

```bash
cd video_app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # télécharge le navigateur Chromium
```

## Configuration

```bash
cp .env.example .env
# Remplir les variables dans .env (voir ci-dessous)
```

### Authentification Higgsfield

**Option A — Email + mot de passe** (si votre compte Higgsfield utilise email/password) :
```
HIGGSFIELD_EMAIL=votre@email.com
HIGGSFIELD_PASSWORD=votre_mot_de_passe
```

**Option B — Cookies** (si vous vous connectez via Google, Microsoft ou Apple) :

1. Connectez-vous à [higgsfield.ai](https://higgsfield.ai) dans votre navigateur
2. Ouvrez DevTools (F12) → onglet **Application** → **Cookies** → `higgsfield.ai`
3. Ouvrez la console (onglet **Console**) et exécutez ce script :

```javascript
// Copie les cookies au format JSON dans le presse-papier
const cookies = document.cookie.split('; ').map(c => {
  const [name, ...v] = c.split('=');
  return { name, value: v.join('='), domain: 'higgsfield.ai', path: '/' };
});
copy(JSON.stringify(cookies));
console.log('Cookies copiés !', cookies.length, 'cookies');
```

4. Collez le résultat dans `.env` :
```
HIGGSFIELD_COOKIES=[{"name":"...","value":"...","domain":"higgsfield.ai","path":"/"}]
```

> **Note :** Après la première connexion réussie, la session est sauvegardée dans
> `.session.json`. Vous n'aurez plus besoin de les fournir à chaque fois.

## Lancement

```bash
python app.py
# → http://localhost:5001
```

Production :
```bash
gunicorn -w 1 -b 0.0.0.0:5001 app:app
# ⚠ Un seul worker (Playwright lance un vrai navigateur — pas thread-safe avec plusieurs workers)
```

## Variables d'environnement

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Clé Anthropic pour Claude (prompt enhancement) |
| `HIGGSFIELD_EMAIL` | Email de votre compte Higgsfield |
| `HIGGSFIELD_PASSWORD` | Mot de passe Higgsfield |
| `HIGGSFIELD_COOKIES` | Cookies JSON (alternative au login email/mot de passe) |
| `PORT` | Port HTTP (défaut : 5001) |
| `FLASK_DEBUG` | Mode debug Flask (true/false) |

## Modèle vidéo

Par défaut : **Seedance 2.0** (`/create/video?model=seedance_2_0`)

Pour changer de modèle, modifiez `VIDEO_URL` dans `higgsfield_scraper.py`.
