# 🎨 DreamlitAI

**Lightweight local media-generation server for images, text, and audio**

A Flask-powered application with configurable model and style catalogs for creative AI generation.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Gunicorn](https://img.shields.io/badge/Gunicorn-Latest-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20%2B%20gTTS-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

---

## 📸 Screenshots

### Chat Window
![Chat Window](https://media.licdn.com/dms/image/v2/D562DAQEZT4v16Y0CTQ/profile-treasury-image-shrink_800_800/B56ZswzvoRGgAY-/0/1766050429972?e=1766988000&v=beta&t=2LNaIErdjdHQFiPc-WysVyD8G6Utb6C_XbjTuL4bba8)

### Select Style
![Select Style](https://media.licdn.com/dms/image/v2/D562DAQG3gv3AZyteKA/profile-treasury-image-shrink_800_800/B56ZswzrELIcAY-/0/1766050412473?e=1766988000&v=beta&t=xXhEyAWDmhGJcowjhGQxjNT2uQAwXGRY81W8DCH7ok8)

### Select Model
![Select Model](https://media.licdn.com/dms/image/v2/D562DAQGd0s92af_JTw/profile-treasury-image-shrink_800_800/B56Zswzl8wHAAc-/0/1766050391192?e=1766988000&v=beta&t=Duwf1bv1gSx-JqpzYh9aP5-7uaWWlppZW7bRpVFu1Ng)

### Prompt to Text
![Prompt to Text](https://media.licdn.com/dms/image/v2/D562DAQEoXJqiUKiOUA/profile-treasury-image-shrink_800_800/B56ZswzgybHkAY-/0/1766050369218?e=1766988000&v=beta&t=heWyFyqRJ2oFiGttvnfQYQXMIlnKcbxZVgfPAEVyA8o)

### Generated Text
![Generated Text](https://media.licdn.com/dms/image/v2/D562DAQFN_82nM27vGg/profile-treasury-image-shrink_800_800/B56Zswzcc1JsAc-/0/1766050351610?e=1766988000&v=beta&t=7CJ3LbWsxeJVsqWmS-o6N5YZNbQ66dcGaRI7LQs4qtg)

### Text to Speech
![Text to Speech](https://media.licdn.com/dms/image/v2/D562DAQHKMyYVUHY7_Q/profile-treasury-image-shrink_800_800/B56ZswzYTQJoAc-/0/1766050334788?e=1766988000&v=beta&t=GlLL49kP7l-BNj7aArLKtOHJqQIj0byvDvj25LDm8Cg)

### Text to Image
![Text to Image](https://media.licdn.com/dms/image/v2/D562DAQF5fEFUV6s1KQ/profile-treasury-image-shrink_800_800/B56ZswzM76J4Ac-/0/1766050288862?e=1766988000&v=beta&t=tINhEQvG-4QZc4lQqjp1Bme-ycspDXJonyoRL6T_0cY)

---

## ✨ Key Features

- 🖼️ **Image Generation** — Multiple models and styles configured in `models.json` and `styles.json`
- 📝 **Text Generation** — Flexible endpoints for application integration
- 🎙️ **Text-to-Speech** — Uses `edge-tts` with automatic `gTTS` fallback
- 🌐 **Simple Frontend** — SPA-style web interface served from `templates/` and `static/`

---

## 📋 Prerequisites

- Python 3.10 or newer
- Virtual environment recommended

---

## 🚀 Quick Start (Development)

**1. Clone the repository**

```powershell
git clone <repo-url>
cd ImageGen
```

**2. Create and activate virtualenv (optional)**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**3. Install dependencies**

```powershell
python -m pip install -r requirements.txt
```

**4. Run the application**

```powershell
python main.py
```

**5. Open in browser**

Navigate to **http://localhost:8080**

---

## 🏭 Production (Gunicorn)

Run with Gunicorn using the included configuration:

```bash
gunicorn -c gunicorn_config.py main:app
```

The repository includes a `Procfile` for easy deployment to PaaS platforms.

---

## 📁 Project Layout

**Important Files**

- `main.py` — Flask application, API endpoints and server entrypoint
- `requirements.txt` — Runtime dependencies
- `models.json` — Model catalog & metadata used by the UI
- `styles.json`, `styles_enhanced.json` — Style categories and prompts
- `templates/` — HTML templates (frontend)
- `static/` — JavaScript, CSS, and image assets
- `generated_images/` — Directory where generated images are saved
- `gunicorn_config.py`, `Procfile`, `DEPLOYMENT.md` — Deployment and config guidance

---

## 🔌 API Endpoints

### 🖼️ Generate Image

```http
POST /generate
Content-Type: application/json
```

Request example:
```json
{
  "prompt": "A cinematic golden hour portrait of a woman",
  "model": "flux",
  "style": "Photorealistic",
  "resolution": "1536x1536",
  "quality": true,
  "hdr": true
}
```

Response example:
```json
{
  "success": true,
  "image_url": "/generated_images/flux_1234567890.png",
  "prompt": "A cinematic golden hour portrait...",
  "model": "flux"
}
```

### 📝 Generate Text

```http
POST /generate_text
Content-Type: application/json
```

Request example:
```json
{
  "prompt": "Write a short product description for a modern lamp",
  "model": "openai"
}
```

### 🎙️ Generate Audio (TTS)

```http
POST /generate_audio
Content-Type: application/json
```

Request example:
```json
{
  "prompt": "Welcome to DreamlitAI",
  "voice": "alloy"
}
```

### 💚 Health Check

```http
GET /health
```

Response: `{ "status": "healthy" }`

---

## 💻 Usage Examples

### Python (requests)

```python
import requests

resp = requests.post('http://localhost:8080/generate', json={
    'prompt': 'Sunset over mountains',
    'model': 'flux',
    'style': 'Cinematic'
})
print(resp.json())
```

### JavaScript (fetch)

```javascript
const res = await fetch('/generate_text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    prompt: 'Explain quantum computing', 
    model: 'openai' 
  })
});
const data = await res.json();
console.log(data);
```

### cURL

```bash
curl -X POST http://localhost:8080/generate_audio \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello World","voice":"alloy"}'
```

---

## ⚙️ Configuration

**Default Settings**

- Runtime port: `8080` (when starting with `python main.py`)
- The app creates `models.json` and `styles.json` defaults if missing
- Edit these files to customize available models, display names, and recommended styles

**Environment Variables**

```bash
export PORT=8080           # Custom port
export FLASK_DEBUG=true    # Enable debug mode
```

---

## 📦 Dependencies

Main packages (see `requirements.txt`):

- `flask`, `flask-cors` — Web server and CORS
- `requests` — Outgoing HTTP calls
- `edge-tts`, `gtts` — Text-to-speech engines
- `gunicorn` — Production WSGI server

**Optional (Recommended)**

- `Pillow` — Creates placeholder model images if missing

```bash
pip install pillow
```

---

## 🔧 Troubleshooting

### ⏱️ Long-running image generation timeouts

Increase Gunicorn `timeout` in `gunicorn_config.py`:

```python
timeout = 180  # 3 minutes
```

### 🎤 TTS fails on Windows

- Ensure `edge-tts` has network access
- Check `main.py` logging for specific errors
- Fallback to `gTTS` happens automatically

### 🔌 Port 8080 already in use (Windows)

```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### 🖼️ Missing Pillow warnings

Only affects placeholder generation. Install with:

```bash
pip install pillow
```

---

## 🧪 Development

**Running Tests**

```bash
pytest tests/
pytest --cov=main tests/  # With coverage
```

**Code Quality**

```bash
black main.py     # Format
flake8 main.py    # Lint
```

---

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a branch: `git checkout -b feature/your-feature`
3. 💾 Commit and push your changes
4. 🎉 Open a Pull Request

Please follow the existing code style in `main.py` and add tests where appropriate.

---

## 📄 License

This project is licensed under the MIT License — see `LICENSE` for details.

---

## 📧 Contact

For questions or support: **venkatesancse37@gmail.com**

---

Made with ❤️ by the DreamlitAI Team