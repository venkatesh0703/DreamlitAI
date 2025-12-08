# DreamlitAI - Production Deployment Guide

## Quick Fix for Worker Timeout

If you're seeing `WORKER TIMEOUT` errors in production, follow these steps:

### 1. Verify Configuration Files

Ensure these files exist in your project root:

- ✅ `gunicorn_config.py` - Gunicorn configuration with 180s timeout
- ✅ `Procfile` - Deployment command for Render
- ✅ `render.yaml` - Render service configuration
- ✅ `requirements.txt` - Updated with edge-tts and gtts

### 2. Deploy to Render

```bash
git add gunicorn_config.py Procfile render.yaml requirements.txt
git commit -m "Fix: Add Gunicorn timeout config for long-running requests"
git push origin main
```

Render will automatically redeploy with the new configuration.

### 3. Verify the Fix

Check your Render logs for:
```
timeout = 180
```

This confirms Gunicorn is using the extended timeout.

## Why This Fixes the Issue

**Problem**: Image generation requests can take up to 120 seconds, but Gunicorn's default worker timeout is only 30 seconds.

**Solution**: 
- Increased worker timeout to **180 seconds** (3 minutes)
- This gives enough time for:
  - Image generation: up to 120 seconds
  - Audio generation: up to 30 seconds
  - Network latency and processing overhead

## Configuration Details

### gunicorn_config.py
```python
timeout = 180  # 3 minutes - handles long image generation
workers = 2    # 2 workers for better concurrency
```

### Procfile
```
web: gunicorn -c gunicorn_config.py main:app
```

### render.yaml
```yaml
services:
  - type: web
    name: dreamlitai
    healthCheckPath: /health
```

## Troubleshooting

### Still seeing timeouts?

1. **Check Render logs** for the actual timeout value being used
2. **Verify Procfile** is being used (check Render dashboard)
3. **Increase timeout further** if needed (edit `gunicorn_config.py`)

### Image generation fails?

- Check if the external API (`pollinations.ai`) is responding
- Verify network connectivity from Render servers
- Check Render logs for specific error messages

## Local Development

For local development, you can run:

```bash
# Development mode (Flask built-in server)
python main.py

# Production mode (with Gunicorn)
gunicorn -c gunicorn_config.py main:app
```

## Health Check

Your app includes a `/health` endpoint that Render uses to verify the service is running:

```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "models_available": 15,
  "styles_available": 50,
  ...
}
```
