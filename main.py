from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import re
import os
from urllib.parse import urlparse
import uuid
import random
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Supported models and their descriptions with enhanced details
MODELS = {
    # 🏆 Top Photorealistic / Realistic Models
    'dalle3': 'DALL·E 3 (OpenAI, photorealistic state-of-the-art, best text alignment, 4K resolution)',
    'imagen': 'Google Imagen (photorealistic, closed source, studio-quality lighting, ultra-detailed)',
    'midjourney-v5': 'Midjourney V5 (highly artistic photorealistic images, cinematic composition)',
    'stable-diffusion-xl': 'Stable Diffusion XL (latest high-res, detailed open source, 8K sharpness)',
    'realistic-vision-v3': 'Realistic Vision V3 (improved skin textures, cinematic lighting, hyperrealism)',
    'cd-pt': 'CD-PT (cutting-edge photorealistic research model, ultra-fine details)',

    # 🎨 Anime & Artistic Styles
    'anything-v5': 'Anything V5 Anime Style (crisp lines, vibrant colors, expressive character design)',
    'anything-v3': 'Anything V3 (classic anime-style, smooth shading, wide compatibility)',
    'anime-art': 'Anime Art (vibrant, detailed, studio-quality animation style)',
    'dreamshaper': 'DreamShaper (dreamy, semi-anime artistic style, painterly effects)',
    'openjourney': 'OpenJourney (Midjourney-inspired open-source art, cinematic quality)',
    'epi-noir': 'Epi-noir (noir anime and manga style, dramatic shadows, high contrast)',
    'romantic-anime-v1': 'Romantic Anime V1 (soft lighting, delicate features, emotional expressions)',

    # 🧙‍♂️ Fantasy / Niche / Dark Styles
    'fantasy-art-v1': 'Fantasy Art V1 (high-detail fantasy scenes, epic scale, magical lighting)',
    'dark-diffusion': 'Dark Diffusion (gothic atmosphere, horror elements, intense shadows)',
    'evil': 'Evil (macabre themes, unsettling details, psychological horror)',
    'goblin-slayer': 'Goblin Slayer (dark fantasy anime style, gritty textures, dramatic action)',
    'kontext': 'Kontext (semantic generation, theme-aware compositions, narrative focus)',

    # 💘 Romance & Soft Styles
    'love-diffusion': 'Love Diffusion (romantic atmosphere, emotional expressions, soft focus)',
    'romantic-realistic-v1': 'Romantic Realistic V1 (cinematic lighting, intimate moments, film grain)',

    # 🧳 Vintage / Retro / 3D & Stylized
    'vintage-style': 'Vintage Style (authentic retro aesthetic, film grain, analog imperfections)',
    'meinamix': 'MeinaMix (3D anime, semi-real textures, Pixar-like rendering)',
    'revAnimated': 'RevAnimated (hybrid anime-3D look, vibrant colors, dynamic poses)',
    'toonyou': 'ToonYou (crisp cartoon styling, expressive characters, graphic novel quality)',
    'arcane-diffusion': 'Arcane Diffusion (Arcane/League of Legends style, painterly textures)',
    'pastel-mix': 'Pastel Mix (soft 2.5D pastel anime aesthetic, dreamy atmosphere)',
    'cetus-mix': 'Cetus Mix (anime + 3D + fantasy hybrid, detailed magical effects)',

    # ⚡ Performance / Speed Optimized
    'flux': 'Flux (balanced quality/speed, sharp details, optimized rendering)',
    'flux-ultra': 'Flux Ultra (premium quality, enhanced sharpness, fine details)',
    'flux-schnell': 'Flux Schnell (rapid generation, maintains good detail quality)',
    'turbo': 'Turbo (ultra-fast generation, optimized for quick iterations)',

    # 🛠️ Utility / Editing / Variants
    'variation': 'Variation (high-fidelity image variations, consistent style)',
    'inpainting': 'Inpainting (seamless edits, context-aware filling, natural results)',
    'depth2img': 'Depth2Img (3D spatial awareness, dimensional lighting, parallax effects)',
    'latent-couple': 'Latent Couple (natural interactions, relationship dynamics, dual focus)',
    'real-esrgan': 'Real-ESRGAN (4x upscaling, detail enhancement, noise reduction)',

    # 🧪 Experimental / Stylized
    'gptimage': 'GPTImage (context-aware generation, semantic understanding)',
    'pixart': 'Pixart (crisp pixel art, authentic retro game style)',
    'stylegan3': 'StyleGAN3 (photorealistic portraits, flawless skin details)',
}

# Enhanced resolution options with aspect ratios
RESOLUTIONS = [
    '512x512 (1:1)', '768x768 (1:1)', '1024x1024 (1:1)', '1536x1536 (1:1)',
    '512x768 (2:3)', '768x512 (3:2)', '768x1024 (3:4)', '1024x768 (4:3)',
    '1024x1536 (2:3)', '1536x1024 (3:2)', '1152x896 (9:7)', '896x1152 (7:9)'
]

# Load style categories
with open('styles.json', 'r', encoding='utf-8') as f:
    STYLE_CATEGORIES = json.load(f)

# Ensure generated_images folder exists
GENERATED_IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'generated_images')
os.makedirs(GENERATED_IMAGES_FOLDER, exist_ok=True)

@app.route('/generated_images/<filename>')
def serve_generated_image(filename):
    return send_from_directory(GENERATED_IMAGES_FOLDER, filename)

@app.route('/')
def home():
    return render_template('index.html', 
                          models=MODELS, 
                          style_categories=STYLE_CATEGORIES, 
                          resolutions=RESOLUTIONS)

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        resolution = data.get('resolution', '1024x1024')
        quality = data.get('quality', False)
        model = data.get('model', 'flux')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Clean up resolution format if needed
        resolution = re.sub(r'\s*\(.*?\)', '', resolution).strip()
        
        # --- Enhanced style prompt lookup and enrichment ---
        style_prompt = ''
        extra_details = ''
        quality_keywords = "masterpiece, best quality, ultra high resolution, sharp focus, intricate details, professional color grading"
        
        if style:
            # Search for the style in STYLE_CATEGORIES
            for cat in STYLE_CATEGORIES:
                for s in cat.get('styles', []):
                    if s['prompt'] == style or s['name'] == style:
                        style_prompt = s['prompt']
                        
                        # Add style-specific enhancements for detail and quality
                        style_lower = style_prompt.lower()
                        if 'oil painting' in style_lower:
                            extra_details = 'visible brush strokes, canvas texture, gallery lighting, museum quality, varnish sheen'
                        elif 'anime' in style_lower:
                            extra_details = 'anime background, expressive eyes, vibrant colors, dynamic composition, crisp line art'
                        elif 'photorealistic' in style_lower or 'photo' in style_lower:
                            extra_details = 'realistic lighting, depth of field, skin texture, professional photo, sharp focus, lens flare'
                        elif 'pixel art' in style_lower:
                            extra_details = 'pixel grid, 8-bit, retro game style, crisp edges, limited palette, dithering patterns'
                        elif 'watercolor' in style_lower:
                            extra_details = 'soft edges, paper texture, flowing colors, gentle gradients, pigment dispersion'
                        elif 'concept art' in style_lower:
                            extra_details = 'cinematic, dramatic lighting, epic scale, detailed environment, matte painting quality'
                        elif 'cartoon' in style_lower:
                            extra_details = 'bold outlines, flat colors, playful style, exaggerated features, graphic novel quality'
                        elif 'fantasy' in style_lower:
                            extra_details = 'magical lighting, ethereal atmosphere, imaginative elements, epic scenery, mythical details'
                        elif 'cyberpunk' in style_lower:
                            extra_details = 'neon lights, rain reflections, futuristic city, high-tech details, holographic elements'
                        elif 'minimalist' in style_lower:
                            extra_details = 'clean lines, simple shapes, limited palette, modern aesthetic, negative space'
                        elif 'cinematic' in style_lower:
                            extra_details = 'film grain, color grading, widescreen aspect, shallow depth of field, cinematic lighting'
                        elif 'hyperrealism' in style_lower:
                            extra_details = 'ultra-detailed, skin pores, texture detail, macro focus, subsurface scattering'
                        elif 'scientific' in style_lower:
                            extra_details = 'technical precision, labeled details, cross-section view, educational diagram'
                        elif 'steampunk' in style_lower:
                            extra_details = 'brass gears, mechanical details, Victorian elements, steam effects, clockwork precision'
                        elif 'vaporwave' in style_lower:
                            extra_details = 'retro aesthetics, glitch effects, grid patterns, neon gradients, VHS artifacts'
                        # Add more style enrichments as needed...
                        break
        
        # Combine user prompt, style prompt, and extra details
        enhanced_prompt = prompt
        if style_prompt:
            enhanced_prompt += f", {style_prompt}"
        if extra_details:
            enhanced_prompt += f", {extra_details}"
        
        # Add quality keywords if not already present
        if not any(qk in enhanced_prompt.lower() for qk in ["masterpiece", "best quality", "high resolution", "sharp focus"]):
            enhanced_prompt += f", {quality_keywords}"
        
        # Add resolution-based enhancements
        width, height = map(int, resolution.split('x'))
        if width >= 1024 or height >= 1024:
            enhanced_prompt += ", 8K resolution, ultra detailed"
        elif width >= 768 or height >= 768:
            enhanced_prompt += ", 4K resolution, highly detailed"
        
        # Add model-specific enhancements
        if 'dalle3' in model:
            enhanced_prompt += ", sharp focus, studio lighting"
        elif 'midjourney' in model:
            enhanced_prompt += ", intricate details, cinematic composition"
        elif 'realistic' in model:
            enhanced_prompt += ", skin texture, realistic materials, subsurface scattering"
        elif 'anime' in model:
            enhanced_prompt += ", crisp line art, vibrant colors, expressive eyes"
        
        # Build API URL
        seed = random.randint(1, 1000000)
        prompt_encoded = quote(enhanced_prompt)
        api_url = (
            f"https://image.pollinations.ai/prompt/{prompt_encoded}"
            f"?seed={seed}&nologo=true&width={width}&height={height}"
        )
        if quality:
            api_url += "&enhance=true"
        if model:
            api_url += f"&model={model}"
        
        # Generate image with enhanced quality parameters
        response = requests.get(api_url, timeout=60)  # Increased timeout for high-res
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            ext = '.jpg'
            if 'png' in response.headers.get('Content-Type', ''):
                ext = '.png'
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(GENERATED_IMAGES_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            local_url = f"/generated_images/{filename}"
            return jsonify({
                'success': True,
                'image_url': local_url,
                'prompt': enhanced_prompt,
                'model': model,
                'resolution': resolution,
                'quality': quality
            })
        else:
            try:
                error_msg = response.json().get('error', 'Failed to generate image')
            except Exception:
                error_msg = 'Failed to generate image'
            return jsonify({'error': error_msg}), 500
        
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest', methods=['POST'])
def suggest_prompt():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        model = data.get('model', '')
        
        if not prompt:
            return jsonify({'suggestions': []})
        
        # AI-powered prompt suggestions
        suggestions = []
        prompt_lower = prompt.lower()
        
        # Style suggestions
        if 'portrait' in prompt_lower:
            suggestions.append("Add 'cinematic lighting, sharp focus' for professional portraits")
        elif 'landscape' in prompt_lower:
            suggestions.append("Try 'golden hour lighting, atmospheric perspective' for stunning landscapes")
        elif 'anime' in prompt_lower or 'manga' in prompt_lower:
            suggestions.append("Use 'expressive eyes, vibrant colors, dynamic pose' for anime characters")
        elif 'fantasy' in prompt_lower:
            suggestions.append("Add 'epic scale, magical lighting, intricate details' for fantasy scenes")
        
        # Model-specific suggestions
        if 'dalle3' in model:
            suggestions.append("DALL·E 3 excels at: complex scenes, text rendering, photorealistic details")
        elif 'midjourney' in model:
            suggestions.append("Midjourney V5 strengths: artistic styles, painterly effects, cinematic compositions")
        elif 'realistic' in model:
            suggestions.append("Add 'skin texture, realistic materials, subsurface scattering' for hyperrealism")
        
        # Quality suggestions
        if len(prompt.split()) < 5:
            suggestions.append("Add more descriptive details for better results: materials, lighting, composition")
        
        # Enhancement suggestions
        enhancements = [
            "masterpiece, best quality", "ultra high resolution", "sharp focus", 
            "intricate details", "professional color grading", "cinematic lighting",
            "studio lighting", "dramatic shadows", "dynamic composition"
        ]
        
        # Suggest adding enhancements
        if not any(enh in prompt_lower for enh in ["masterpiece", "best quality", "high resolution"]):
            suggestions.append(f"Add quality keywords: '{enhancements[0]}' or '{enhancements[1]}'")
            
        # Resolution suggestions
        if 'detailed' in prompt_lower or 'intricate' in prompt_lower:
            suggestions.append("Use higher resolutions (1024x1024+) for complex details")
            
        # Style selection suggestions
        if not any(style_word in prompt_lower for style_word in ["oil painting", "anime", "cinematic", "photorealistic"]):
            suggestions.append("Consider adding a style descriptor: 'oil painting', 'anime style', or 'cinematic'")
        
        return jsonify({'suggestions': suggestions[:5]})  # Increased to 5 suggestions
        
    except Exception as e:
        app.logger.error(f"Suggestion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)