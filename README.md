<p align="center">
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Artist%20Palette.png" width="56" alt="DreamlitAI" />
</p>

<h1 align="center">DreamlitAI</h1>

<p align="center">
  <samp>AI-Powered Creative Suite &nbsp;·&nbsp; Images &nbsp;·&nbsp; Text &nbsp;·&nbsp; Audio</samp>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-black?style=flat-square&logo=python&logoColor=white" />
  &nbsp;
  <img src="https://img.shields.io/badge/flask-black?style=flat-square&logo=flask&logoColor=white" />
  &nbsp;
  <img src="https://img.shields.io/badge/tailwind_css-black?style=flat-square&logo=tailwind-css&logoColor=38B2AC" />
  &nbsp;
  <img src="https://img.shields.io/badge/license_MIT-black?style=flat-square" />
</p>

<p align="center">
  <a href="#-get-started">Get Started</a> &nbsp;·&nbsp;
  <a href="#-features">Features</a> &nbsp;·&nbsp;
  <a href="#-models">Models</a> &nbsp;·&nbsp;
  <a href="#-api">API</a> &nbsp;·&nbsp;
  <a href="#-deploy">Deploy</a>
</p>

<br />

---

<br />

## &nbsp;Overview

DreamlitAI transforms a single text prompt into production-ready images, rich written content, or natural-sounding audio — all from one unified interface, powered by [Pollinations.ai](https://pollinations.ai).

<br />

## &nbsp;✦&nbsp; Features

<br />

<table>
  <tr>
    <td width="40"><img src="https://img.icons8.com/fluency/48/image.png" width="28"/></td>
    <td><strong>Image Generation</strong></td>
    <td>8 models &nbsp;·&nbsp; 236+ styles &nbsp;·&nbsp; up to 4K &nbsp;·&nbsp; HDR &nbsp;·&nbsp; negative prompts</td>
  </tr>
  <tr>
    <td><img src="https://img.icons8.com/fluency/48/document.png" width="28"/></td>
    <td><strong>Text Generation</strong></td>
    <td>2 models &nbsp;·&nbsp; 5 personas &nbsp;·&nbsp; temperature control &nbsp;·&nbsp; 5 output formats</td>
  </tr>
  <tr>
    <td><img src="https://img.icons8.com/fluency/48/speaker.png" width="28"/></td>
    <td><strong>Audio Generation</strong></td>
    <td>6 neural voices &nbsp;·&nbsp; rate / pitch / volume &nbsp;·&nbsp; Edge-TTS + gTTS fallback</td>
  </tr>
  <tr>
    <td><img src="https://img.icons8.com/fluency/48/artificial-intelligence.png" width="28"/></td>
    <td><strong>Smart Recommendations</strong></td>
    <td>Auto-selects best model & style based on your prompt context</td>
  </tr>
  <tr>
    <td><img src="https://img.icons8.com/fluency/48/grid.png" width="28"/></td>
    <td><strong>Compatibility Matrix</strong></td>
    <td>Curated pairings of models + styles for guaranteed quality</td>
  </tr>
</table>

<br />

---

<br />

## &nbsp;⚡&nbsp; Get Started

> **Requires** Python 3.9+ and pip

```bash
# Clone
git clone https://github.com/yourusername/dreamlitai.git
cd dreamlitai

# Install
pip install -r requirements.txt

# (Optional) Add API key for higher limits
cp .env.example .env

# Run
python src/main.py
```

Open **`http://localhost:5000`** — fully responsive on mobile.

<br />

---

<br />

## &nbsp;🎨&nbsp; Models

### Image

| Model | Quality | Speed | Best For |
|-------|---------|-------|----------|
| `flux` | ★★★★★ | ★★★★★ | General purpose · fast |
| `kontext` | ★★★★★ | ★★★★☆ | Character consistency |
| `gptimage-lg` | ★★★★★ | ★★★☆☆ | Fine art · high detail |
| `wan-image` | ★★★★★ | ★★★☆☆ | Cinematic · film quality |
| `klein` | ★★★★☆ | ★★★★★ | Quick drafts · low poly |
| `gptimage` | ★★★★☆ | ★★★★☆ | Creative concepts |
| `qwen-image` | ★★★★☆ | ★★★★☆ | Multi-style · Asian art |
| `zimage` | ★★★★☆ | ★★★★★ | Rapid prototyping |

### Text

| Model | Quality | Speed | Best For |
|-------|---------|-------|----------|
| `amazon-nova-micro` | ★★★★☆ | ★★★★★ | Fast, concise responses |
| `qwen3guard-8b` | ★★★★☆ | ★★★★☆ | Safe, guarded output |

<br />

---

<br />

## &nbsp;🖌&nbsp; Style Gallery

**236 unique styles** across 20+ categories.

<details>
<summary><samp>Show all categories →</samp></summary>

<br />

| Category | Styles |
|----------|--------|
| 🎭 **Classical Art** | Renaissance · Baroque · Impressionism · Ukiyo-e · Romanticism · Realism · Rococo · Neoclassicism |
| 🎨 **Digital & Graphic** | Pixel Art · Vector · Low Poly · Glitch Art · Isometric · Flat Design · Neumorphism · HUD |
| 🧱 **Material & Texture** | Claymation · Crystalline · Metallic · Organic · Glass · Wood · Fabric · Stone · Liquid |
| 🎬 **Cinematic** | Noir · Epic Cinematic · Liminal Space · Dramatic Lighting · Golden Hour · Volumetric |
| 🐉 **Fantasy** | Dragons · Phoenix · Griffins · Unicorns · Centaurs · Mermaids · Werewolves · Kraken |
| 👽 **Sci-Fi & Alien** | Grey Aliens · Reptilian · Insectoid · Energy Beings · Silicon-Based · Aquatic |
| ⚔️ **War & Military** | Historical Battle · Modern Warfare · Futuristic Combat · Naval · Aerial Dogfight |
| ⚙️ **Technical** | Quality Enhancement · Color Grading · Depth of Field · Resolution Boost · HDR |

</details>

<br />

---

<br />

## &nbsp;🔌&nbsp; API

**Base URL** &nbsp; `http://localhost:5000`

<br />

**`POST /generate`** &nbsp;&nbsp; Image generation

```json
{
  "prompt": "a majestic dragon over mountains",
  "model": "flux",
  "style": "Epic Cinematic",
  "resolution": "1024x1024",
  "quality": true,
  "hdr": false
}
```

**`POST /generate_text`** &nbsp;&nbsp; Text generation

```json
{
  "prompt": "Explain quantum computing",
  "model": "amazon-nova-micro",
  "temperature": 0.7
}
```

**`POST /generate_audio`** &nbsp;&nbsp; Audio generation

```json
{
  "prompt": "Hello World!",
  "voice": "alloy",
  "rate": "+0%",
  "pitch": "+0Hz",
  "volume": "+0%"
}
```

**Response**

```json
{
  "success": true,
  "image_url": "/generated_images/abc123.jpg",
  "prompt": "enhanced prompt with style keywords...",
  "model": "flux",
  "resolution": "1024x1024"
}
```

<br />

---

<br />

## &nbsp;⚙️&nbsp; Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port |
| `PYTHON_VERSION` | `3.9` | Python runtime |
| `POLLINATIONS_KEY` | — | API key for higher rate limits |
| `FLASK_ENV` | `development` | `development` or `production` |

```
data/models.json       →  AI model definitions
data/styles.json       →  Artistic style definitions
src/main.py            →  Prompt engineering logic
templates/index.html   →  UI customization
```

<br />

---

<br />

## &nbsp;🚀&nbsp; Deploy

### Render.com

1. Push repo to GitHub and connect to [Render](https://render.com)
2. `render.yaml` is auto-detected — no manual config needed
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn -c config/gunicorn_config.py main:app`
5. Health check: `GET /health` &nbsp;→&nbsp; live ✓

### Gunicorn (Manual)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

<br />

---

<br />

## &nbsp;📁&nbsp; Structure

```
dreamlitai/
│
├── src/
│   └── main.py                 # App · DataManager · PromptBuilder · Routes
│
├── data/
│   ├── models.json             # 22 AI model definitions
│   └── styles.json             # 236+ style definitions
│
├── static/
│   ├── style_images/           # Style preview thumbnails
│   ├── model_images/           # Model previews
│   ├── app.js
│   └── style.css
│
├── templates/
│   └── index.html              # UI — Tailwind + Alpine.js
│
├── config/
│   ├── render.yaml
│   ├── gunicorn_config.py
│   └── Procfile
│
├── generated_images/           # Output storage
└── requirements.txt
```

<br />

---

<br />

## &nbsp;🤝&nbsp; Contributing

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

Open a pull request — all contributions are welcome.

<br />

---

<br />

<p align="center">
  <samp>
    Built with ❤️ by developers, for creators
    <br /><br />
    <a href="https://pollinations.ai">Pollinations.ai</a> &nbsp;·&nbsp;
    <a href="https://tailwindcss.com">Tailwind CSS</a> &nbsp;·&nbsp;
    <a href="https://alpinejs.dev">Alpine.js</a> &nbsp;·&nbsp;
    <a href="https://flask.palletsprojects.com">Flask</a>
    <br /><br />
    <sub>© 2025 DreamlitAI &nbsp;·&nbsp; MIT License</sub>
  </samp>
</p># DreamlitAI
# DreamlitAI
