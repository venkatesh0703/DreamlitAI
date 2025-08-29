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
from typing import Dict, List, Any, Optional

app = Flask(__name__)
CORS(app)

class DataManager:
    """Manages loading and caching of styles and models data with advanced filtering"""
    
    def __init__(self):
        self._styles_cache: Optional[List[Dict]] = None
        self._models_cache: Optional[List[Dict]] = None
        self._models_dict_cache: Optional[Dict[str, str]] = None
        self._compatibility_cache: Optional[Dict] = None
    
    def load_styles(self) -> List[Dict[str, Any]]:
        """Load and cache style categories from JSON file"""
        if self._styles_cache is None:
            try:
                with open('styles.json', 'r', encoding='utf-8') as f:
                    self._styles_cache = json.load(f)
            except FileNotFoundError:
                print("Warning: styles.json not found. Creating default file.")
                self._styles_cache = self._create_default_styles()
                self._save_styles()
        return self._styles_cache
    
    def load_models(self) -> List[Dict[str, Any]]:
        """Load and cache model categories from JSON file"""
        if self._models_cache is None:
            try:
                with open('models.json', 'r', encoding='utf-8') as f:
                    self._models_cache = json.load(f)
            except FileNotFoundError:
                print("Warning: models.json not found. Creating default file.")
                self._models_cache = self._create_default_models()
                self._save_models()
        return self._models_cache
    
    def get_models_dict(self) -> Dict[str, str]:
        """Get flat dictionary of models for backward compatibility"""
        if self._models_dict_cache is None:
            model_categories = self.load_models()
            self._models_dict_cache = {}
            for category in model_categories:
                for model in category.get('models', []):
                    self._models_dict_cache[model['name']] = f"{model['display_name']} ({model['description']})"
        return self._models_dict_cache
    
    def find_style_prompt(self, style: str) -> str:
        """Find style prompt by name or prompt value"""
        styles = self.load_styles()
        for category in styles:
            for s in category.get('styles', []):
                if s['prompt'] == style or s['name'] == style:
                    return s['prompt']
        return ''
    
    def get_style_details(self, style_name: str) -> Optional[Dict]:
        """Get detailed information about a specific style"""
        styles = self.load_styles()
        for category in styles:
            for style in category.get('styles', []):
                if style['name'] == style_name:
                    return {
                        **style,
                        'category_name': category['category'],
                        'category_description': category.get('description', '')
                    }
        return None
    
    def get_model_details(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a specific model"""
        models = self.load_models()
        for category in models:
            for model in category.get('models', []):
                if model['name'] == model_name:
                    return {
                        **model,
                        'category_name': category['category'],
                        'category_description': category.get('description', '')
                    }
        return None
    
    def get_compatible_models_for_style(self, style_name: str) -> List[str]:
        """Get models that work best with a specific style"""
        style_details = self.get_style_details(style_name)
        if style_details and 'compatibility' in style_details:
            return style_details['compatibility'].get('best_models', [])
        return []
    
    def get_compatible_styles_for_model(self, model_name: str) -> List[str]:
        """Get styles that work best with a specific model"""
        model_details = self.get_model_details(model_name)
        if model_details and 'compatibility' in model_details:
            return model_details['compatibility'].get('styles', [])
        return []
    
    def filter_models_by_criteria(self, category: str = None, difficulty: str = None, 
                                 min_quality: float = None, min_speed: float = None) -> List[Dict]:
        """Filter models based on various criteria"""
        models = self.load_models()
        filtered_models = []
        
        for cat in models:
            if category and cat['category'] != category:
                continue
                
            for model in cat.get('models', []):
                # Check difficulty
                if difficulty and model.get('difficulty') != difficulty:
                    continue
                    
                # Check quality rating
                if min_quality and model.get('rating', {}).get('quality', 0) < min_quality:
                    continue
                    
                # Check speed rating
                if min_speed and model.get('rating', {}).get('speed', 0) < min_speed:
                    continue
                    
                filtered_models.append({
                    **model,
                    'category_name': cat['category']
                })
                
        return filtered_models
    
    def filter_styles_by_criteria(self, category: str = None, difficulty: str = None,
                                 complexity_level: str = None, min_popularity: float = None) -> List[Dict]:
        """Filter styles based on various criteria"""
        styles = self.load_styles()
        filtered_styles = []
        
        for cat in styles:
            if category and cat['category'] != category:
                continue
                
            for style in cat.get('styles', []):
                # Check difficulty
                if difficulty and style.get('difficulty') != difficulty:
                    continue
                    
                # Check complexity level
                if complexity_level and style.get('complexity', {}).get('level') != complexity_level:
                    continue
                    
                # Check popularity
                if min_popularity and style.get('popularity', 0) < min_popularity:
                    continue
                    
                filtered_styles.append({
                    **style,
                    'category_name': cat['category']
                })
                
        return filtered_styles
    
    def get_recommendations(self, prompt: str, current_model: str = None, 
                          current_style: str = None) -> Dict[str, List[str]]:
        """Get intelligent recommendations based on prompt analysis"""
        recommendations = {
            'models': [],
            'styles': [],
            'settings': {}
        }
        
        prompt_lower = prompt.lower()
        
        # Analyze prompt for content type
        if any(word in prompt_lower for word in ['portrait', 'person', 'face', 'human']):
            recommendations['models'].extend(['realistic-vision-v3', 'dalle3', 'imagen'])
            recommendations['styles'].extend(['Photorealistic', 'HDR', 'Hyperrealism'])
            recommendations['settings']['resolution'] = '1024x1024'
            
        elif any(word in prompt_lower for word in ['landscape', 'nature', 'mountain', 'ocean']):
            recommendations['models'].extend(['midjourney-v5', 'stable-diffusion-xl', 'dalle3'])
            recommendations['styles'].extend(['Epic Cinematic', 'HDR', 'Golden Hour'])
            recommendations['settings']['resolution'] = '1536x1024'
            
        elif any(word in prompt_lower for word in ['anime', 'manga', 'character']):
            recommendations['models'].extend(['anything-v5', 'anime-art', 'dreamshaper'])
            recommendations['styles'].extend(['Artistic Illustration', 'Digital Art'])
            recommendations['settings']['resolution'] = '1024x1024'
            
        elif any(word in prompt_lower for word in ['cyberpunk', 'futuristic', 'neon', 'sci-fi']):
            recommendations['models'].extend(['midjourney-v5', 'stable-diffusion-xl'])
            recommendations['styles'].extend(['Cyberpunk', 'Epic Cinematic', 'Digital Art'])
            recommendations['settings']['hdr'] = True
            
        elif any(word in prompt_lower for word in ['fantasy', 'dragon', 'magic', 'medieval']):
            recommendations['models'].extend(['fantasy-art-v1', 'midjourney-v5', 'stable-diffusion-xl'])
            recommendations['styles'].extend(['High Fantasy', 'Epic Cinematic', 'Digital Art'])
            recommendations['settings']['quality'] = True
            
        # Remove duplicates and limit to top 3
        recommendations['models'] = list(dict.fromkeys(recommendations['models']))[:3]
        recommendations['styles'] = list(dict.fromkeys(recommendations['styles']))[:3]
        
        return recommendations
    
    def _create_default_styles(self) -> List[Dict]:
        """Create default styles structure"""
        return []
    
    def _create_default_models(self) -> List[Dict]:
        """Create default models structure"""
        return []
    
    def _save_styles(self):
        """Save styles to JSON file"""
        with open('styles.json', 'w', encoding='utf-8') as f:
            json.dump(self._styles_cache, f, indent=2, ensure_ascii=False)
    
    def _save_models(self):
        """Save models to JSON file"""
        with open('models.json', 'w', encoding='utf-8') as f:
            json.dump(self._models_cache, f, indent=2, ensure_ascii=False)

# Initialize advanced data manager
data_manager = DataManager()

# Load data using the manager
STYLE_CATEGORIES = data_manager.load_styles()
MODEL_CATEGORIES = data_manager.load_models()
MODELS = data_manager.get_models_dict()

# Enhanced resolution options with aspect ratios
RESOLUTIONS = [
    '512x512 (1:1)', '768x768 (1:1)', '1024x1024 (1:1)', '1536x1536 (1:1)',
    '512x768 (2:3)', '768x512 (3:2)', '768x1024 (3:4)', '1024x768 (4:3)',
    '1024x1536 (2:3)', '1536x1024 (3:2)', '1152x896 (9:7)', '896x1152 (7:9)',
    '2048x2048 (1:1)', '3072x3072 (1:1)', '4096x4096 (1:1)'
]

# Ensure required directories exist
GENERATED_IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'generated_images')
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
MODELS_FOLDER = os.path.join(STATIC_FOLDER, 'models')
STYLES_FOLDER = os.path.join(STATIC_FOLDER, 'styles')

# Create directories
for folder in [GENERATED_IMAGES_FOLDER, STATIC_FOLDER, MODELS_FOLDER, STYLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Create placeholder images for models if they don't exist
def create_model_placeholders():
    """Create placeholder images for models"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        for category in MODEL_CATEGORIES:
            for model in category.get('models', []):
                model_name = model['name']
                model_path = os.path.join(MODELS_FOLDER, f"{model_name}.jpg")
                if not os.path.exists(model_path):
                    # Create a simple placeholder image
                    img = Image.new('RGB', (400, 300), color='#6366f1')
                    draw = ImageDraw.Draw(img)
                    
                    # Try to use a font, fallback to default if not available
                    try:
                        font = ImageFont.truetype("arial.ttf", 20)
                    except:
                        font = ImageFont.load_default()
                    
                    # Draw model name on image
                    text = model.get('display_name', model_name)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (400 - text_width) // 2
                    y = (300 - text_height) // 2
                    
                    draw.text((x, y), text, fill='white', font=font)
                    img.save(model_path, 'JPEG')
                    
    except ImportError:
        # PIL not available, skip placeholder creation
        print("PIL not available, skipping model placeholder creation")
        pass

# Create placeholder images
create_model_placeholders()

class UltraPromptBuilder:
    """Advanced prompt enhancement with ultra-quality optimization"""
    
    def __init__(self, base_prompt: str, style_prompt: str, model_name: str, quality: bool, hdr: bool, resolution: str):
        self.base_prompt = base_prompt
        self.style_prompt = style_prompt
        self.model_name = model_name
        self.quality = quality
        self.hdr = hdr
        self.resolution = resolution
        self.data_manager = data_manager
    
    def build(self) -> str:
        """Build ultra-optimized prompt with advanced enhancements"""
        prompt_parts = [self.base_prompt]
        
        # Add ultra-enhanced style prompt
        if self.style_prompt:
            prompt_parts.append(self.style_prompt)
        
        # Add model-specific optimization prompts
        model_optimizations = self._get_model_optimizations()
        if model_optimizations:
            prompt_parts.append(model_optimizations)
        
        # Add ultra-quality enhancements
        if self.quality:
            prompt_parts.append(self._get_ultra_quality_keywords())
        
        # Add advanced HDR enhancements
        if self.hdr:
            prompt_parts.append(self._get_advanced_hdr_keywords())
        
        # Add resolution-based ultra enhancements
        resolution_enhancement = self._get_ultra_resolution_enhancement()
        if resolution_enhancement:
            prompt_parts.append(resolution_enhancement)
        
        # Add technical photography specifications
        tech_specs = self._get_technical_specifications()
        if tech_specs:
            prompt_parts.append(tech_specs)
        
        return ", ".join(filter(None, prompt_parts))
    
    def _get_model_optimizations(self) -> str:
        """Get model-specific optimization prompts"""
        model_details = self.data_manager.get_model_details(self.model_name)
        if model_details and 'optimization_prompts' in model_details:
            optimizations = []
            opt_prompts = model_details['optimization_prompts']
            
            if self.quality and 'quality_enhancers' in opt_prompts:
                optimizations.append(opt_prompts['quality_enhancers'])
            
            if 'realism_boosters' in opt_prompts:
                optimizations.append(opt_prompts['realism_boosters'])
            
            if self._is_high_resolution() and 'technical_specs' in opt_prompts:
                optimizations.append(opt_prompts['technical_specs'])
            
            return ", ".join(optimizations)
        return ""
    
    def _get_ultra_quality_keywords(self) -> str:
        """Get ultra-quality enhancement keywords"""
        return "masterpiece, best quality, ultra detailed, 16K HDR, professional photography, award-winning, commercial quality, studio lighting, perfect exposure, razor-sharp focus, microscopic details, color-graded perfection"
    
    def _get_advanced_hdr_keywords(self) -> str:
        """Get advanced HDR enhancement keywords"""
        return "ultra HDR photography, extreme dynamic range, 14-stop latitude, perfectly balanced highlights and shadows, professional tone mapping, Dolby Vision HDR10+, broadcast quality, luminosity masking, color-graded cinematic look"
    
    def _get_ultra_resolution_enhancement(self) -> str:
        """Get ultra resolution-based enhancement text"""
        try:
            width, height = map(int, self.resolution.split('x'))
            if width >= 4096 or height >= 4096:
                return "16K ultra HD masterpiece, extreme microscopic detail, laser-sharp focus, crystal clear definition, Phase One IQ4 150MP quality, zero chromatic aberration, lossless compression"
            elif width >= 2048 or height >= 2048:
                return "8K ultra HD, extreme detail, professional photography quality, medium format camera detail, perfect optical clarity"
            elif width >= 1024 or height >= 1024:
                return "4K ultra detailed, sharp focus, professional quality, DSLR camera standard"
            elif width >= 768 or height >= 768:
                return "high resolution, detailed, sharp focus, professional standard"
        except ValueError:
            pass
        return "high quality, detailed"
    
    def _get_technical_specifications(self) -> str:
        """Get technical photography specifications"""
        if self._is_photographic_style():
            return "shot with professional camera, perfect lighting setup, studio quality, commercial photography standard, color accuracy, professional color grading"
        return ""
    
    def _is_high_resolution(self) -> bool:
        """Check if using high resolution"""
        try:
            width, height = map(int, self.resolution.split('x'))
            return width >= 2048 or height >= 2048
        except ValueError:
            return False
    
    def _is_photographic_style(self) -> bool:
        """Check if using photographic style"""
        photographic_keywords = ['photorealistic', 'photography', 'hdr', 'macro', 'portrait']
        style_lower = self.style_prompt.lower() if self.style_prompt else ''
        return any(keyword in style_lower for keyword in photographic_keywords)
    
    def _has_quality_keywords(self) -> bool:
        """Check if prompt already contains quality keywords"""
        quality_terms = ["masterpiece", "best quality", "ultra detailed", "16k", "professional"]
        return any(term in self.base_prompt.lower() for term in quality_terms)

# Set global reference for prompt builder after class definition
UltraPromptBuilder.data_manager = data_manager

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files including style images, CSS, and JS"""
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/generated_images/<filename>')
def serve_generated_image(filename):
    """Serve generated images"""
    return send_from_directory(GENERATED_IMAGES_FOLDER, filename)

@app.route('/')
def home():
    """Main page route"""
    return render_template('index.html', 
                          models=MODELS,
                          model_categories=MODEL_CATEGORIES, 
                          style_categories=STYLE_CATEGORIES, 
                          resolutions=RESOLUTIONS)

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate image endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        resolution = data.get('resolution', '1024x1024')
        quality = data.get('quality', False)
        hdr = data.get('hdr', False)
        model = data.get('model', 'flux')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Clean up resolution format if needed
        resolution = re.sub(r'\s*\(.*?\)', '', resolution).strip()
        
        # Enhanced style prompt lookup with advanced prompts
        style_details = data_manager.get_style_details(style) if style else None
        if style_details and 'advanced_prompts' in style_details:
            # Use context-aware advanced prompts
            prompt_lower = prompt.lower()
            if 'portrait' in prompt_lower and 'portrait_mode' in style_details['advanced_prompts']:
                style_prompt = style_details['advanced_prompts']['portrait_mode']
            elif 'product' in prompt_lower and 'product_mode' in style_details['advanced_prompts']:
                style_prompt = style_details['advanced_prompts']['product_mode']
            elif 'landscape' in prompt_lower and 'landscape_mode' in style_details['advanced_prompts']:
                style_prompt = style_details['advanced_prompts']['landscape_mode']
            else:
                style_prompt = style_details['prompt']
        else:
            style_prompt = data_manager.find_style_prompt(style) if style else ''
        
        # Build ultra-enhanced prompt
        enhanced_prompt = UltraPromptBuilder(prompt, style_prompt, model, quality, hdr, resolution).build()
        
        # Build API URL
        seed = random.randint(1, 1000000)
        prompt_encoded = quote(enhanced_prompt)
        api_url = (
            f"https://image.pollinations.ai/prompt/{prompt_encoded}"
            f"?seed={seed}&nologo=true&width={resolution.split('x')[0]}&height={resolution.split('x')[1]}"
        )
        if quality:
            api_url += "&enhance=true"
        if hdr:
            api_url += "&hdr=true"
        if model:
            api_url += f"&model={model}"
        
        # Generate image with enhanced quality parameters
        response = requests.get(api_url, timeout=120)  # Increased timeout for high-res
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
                'quality': quality,
                'hdr': hdr
            })
        else:
            try:
                error_msg = response.json().get('error', 'Failed to generate image')
            except Exception:
                error_msg = f'Failed to generate image. Status: {response.status_code}'
            return jsonify({'error': error_msg}), 500
        
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest_prompt', methods=['POST'])
def suggest_prompt():
    """Provide advanced prompt improvement suggestions and intelligent recommendations"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        model = data.get('model', 'flux')
        hdr = data.get('hdr', False)
        
        suggestions = []
        prompt_lower = prompt.lower()
        
        # Get intelligent recommendations
        recommendations = data_manager.get_recommendations(prompt, model, style)
        
        # Basic prompt enhancement suggestions
        if len(prompt) < 20:
            suggestions.append("Add more descriptive details to your prompt for better results")
        
        # Content-specific suggestions
        if 'portrait' in prompt_lower or 'person' in prompt_lower:
            suggestions.append("For portraits, add: 'professional headshot, studio lighting, sharp focus'")
            if not style:
                suggestions.append("Recommended styles: Epic Cinematic, HDR, or Golden Hour")
        elif 'anime' in prompt_lower or 'manga' in prompt_lower:
            suggestions.append("Use 'expressive eyes, vibrant colors, dynamic pose' for anime characters")
            if not style:
                suggestions.append("Recommended styles: Artistic Illustration or Digital Art")
        elif 'fantasy' in prompt_lower:
            suggestions.append("Add 'epic scale, magical lighting, intricate details' for fantasy scenes")
            if not style:
                suggestions.append("Recommended styles: High Fantasy or Epic Cinematic")
        
        # Model-specific advanced suggestions with ultra-quality optimization
        model_details = data_manager.get_model_details(model)
        if model_details:
            if model_details.get('ultra_quality_features'):
                features = model_details['ultra_quality_features']
                if 'hdr_support' in features and not hdr:
                    suggestions.append(f"Enable HDR for {features['hdr_support']} support")
                if 'detail_enhancement' in features and data.get('resolution', '1024x1024') < '2048x2048':
                    suggestions.append(f"Use higher resolution for {features['detail_enhancement']}")
            
            if model_details.get('performance_metrics'):
                metrics = model_details['performance_metrics']
                if metrics.get('detail_score', 0) > 95:
                    suggestions.append("This model excels at ultra-detailed generation - use complex prompts")
                if metrics.get('realism_index', 0) > 95:
                    suggestions.append("Perfect for photorealistic results - enable Quality and HDR modes")
            
            if model_details.get('recommended_settings'):
                settings = model_details['recommended_settings']
                if settings.get('quality') and not data.get('quality'):
                    suggestions.append("Enable Quality mode for this model's optimal performance")
                if settings.get('hdr') and not hdr:
                    suggestions.append("Enable HDR for this model's enhanced dynamic range capabilities")
                if 'cfg_scale' in settings:
                    suggestions.append(f"Optimal CFG scale for this model: {settings['cfg_scale']}")
        
        # Style-specific ultra-quality suggestions
        style_details = data_manager.get_style_details(style)
        if style_details:
            if style_details.get('ultra_quality_specs'):
                specs = style_details['ultra_quality_specs']
                if 'detail_level' in specs:
                    suggestions.append(f"This style supports {specs['detail_level']} - use maximum resolution")
                if 'hdr_optimization' in specs and not hdr:
                    suggestions.append(f"Enable HDR for {specs['hdr_optimization']} support")
                if specs.get('realism_factor', 0) > 95:
                    suggestions.append("Ultra-realistic style detected - enable all quality enhancements")
            
            if style_details.get('advanced_prompts'):
                prompt_lower = prompt.lower()
                if 'portrait' in prompt_lower and 'portrait_mode' in style_details['advanced_prompts']:
                    suggestions.append("Portrait detected - using optimized portrait prompt enhancement")
                elif 'product' in prompt_lower and 'product_mode' in style_details['advanced_prompts']:
                    suggestions.append("Product shot detected - using commercial photography optimization")
                elif 'landscape' in prompt_lower and 'landscape_mode' in style_details['advanced_prompts']:
                    suggestions.append("Landscape detected - using professional landscape photography enhancement")
            
            if style_details.get('complexity', {}).get('level') in ['High', 'Very High']:
                suggestions.append(f"Ultra-complex style detected. Use maximum resolution (2048x2048+) and enable Quality mode")
        
        # Compatibility suggestions
        if model and style:
            compatible_models = data_manager.get_compatible_models_for_style(style)
            if model not in compatible_models and compatible_models:
                suggestions.append(f"For better results with {style}, consider: {', '.join(compatible_models[:2])}")
        
        # Quality and enhancement suggestions
        if len(prompt.split()) < 5:
            suggestions.append("Add more descriptive details: materials, lighting, composition, mood")
        
        # Ultra-technical suggestions based on content analysis
        if any(word in prompt_lower for word in ['detailed', 'intricate', 'microscopic', 'ultra']):
            suggestions.append("Ultra-detailed content detected - use maximum resolution (4096x4096) and enable all quality enhancements")
        
        if any(word in prompt_lower for word in ['professional', 'commercial', 'award-winning']):
            suggestions.append("Professional quality requested - enable Quality mode, HDR, and use photorealistic models")
        
        if any(word in prompt_lower for word in ['dark', 'shadow', 'night', 'moody', 'dramatic']):
            suggestions.append("High contrast scene detected - enable HDR mode for 14-stop dynamic range")
        
        if any(word in prompt_lower for word in ['macro', 'close-up', 'texture', 'surface']):
            suggestions.append("Macro detail detected - use ultra-high resolution and macro photography style")
        
        if any(word in prompt_lower for word in ['16k', '8k', 'ultra hd', 'maximum resolution']):
            suggestions.append("Ultra-high resolution requested - enable all quality enhancements and use premium models")
        
        # Ultra-quality style descriptor suggestions
        if not any(style_word in prompt_lower for style_word in ["photorealistic", "anime", "cinematic", "artistic", "ultra", "masterpiece"]):
            suggestions.append("Add ultra-quality descriptors like 'ultra photorealistic', 'masterpiece quality', or 'professional cinematic'")
        
        # Advanced technical suggestions
        if not any(tech_word in prompt_lower for tech_word in ["hdr", "professional", "studio", "commercial"]):
            suggestions.append("Add technical quality terms like 'HDR photography', 'studio lighting', or 'commercial quality' for best results")
        
        # Helper functions for optimization summary
        def calculate_quality_score(prompt: str, model: str, style: str, quality: bool, hdr: bool) -> int:
            """Calculate expected quality score based on settings"""
            base_score = 70
            
            # Model quality bonus
            model_details = data_manager.get_model_details(model)
            if model_details and 'rating' in model_details:
                base_score += int(model_details['rating'].get('quality', 7) * 3)
            
            # Style quality bonus
            style_details = data_manager.get_style_details(style)
            if style_details and 'ultra_quality_specs' in style_details:
                base_score += 10
            
            # Settings bonus
            if quality:
                base_score += 15
            if hdr:
                base_score += 10
            
            # Prompt complexity bonus
            if len(prompt.split()) > 10:
                base_score += 5
            
            return min(base_score, 100)
        
        def get_optimal_resolution(prompt: str, model: str, style: str) -> str:
            """Get optimal resolution recommendation"""
            if any(word in prompt.lower() for word in ['ultra', '16k', 'maximum', 'detailed']):
                return '4096x4096'
            elif any(word in prompt.lower() for word in ['professional', 'commercial', 'hdr']):
                return '2048x2048'
            else:
                return '1536x1536'
        
        def estimate_generation_time(model: str, quality: bool, hdr: bool) -> str:
            """Estimate generation time"""
            base_time = 15
            
            model_details = data_manager.get_model_details(model)
            if model_details and 'technical_specs' in model_details:
                inference_time = model_details['technical_specs'].get('inference_time', '15-30 seconds')
                if 'slow' in inference_time.lower() or '45' in inference_time:
                    base_time = 45
                elif '30' in inference_time:
                    base_time = 30
            
            if quality:
                base_time += 15
            if hdr:
                base_time += 10
            
            return f"{base_time}-{base_time + 15} seconds"
        
        # Add ultra-quality optimization summary
        optimization_summary = {
            'quality_score': calculate_quality_score(prompt, model, style, data.get('quality', False), hdr),
            'recommended_resolution': get_optimal_resolution(prompt, model, style),
            'estimated_generation_time': estimate_generation_time(model, data.get('quality', False), hdr),
            'optimization_level': 'Ultra-High' if data.get('quality') and hdr else 'Standard'
        }
        
        return jsonify({
            'suggestions': suggestions[:8],  # Increased to 8 suggestions
            'recommendations': recommendations,
            'optimization_summary': optimization_summary
        })
    
    except Exception as e:
        app.logger.error(f"Suggestion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint with detailed statistics"""
    return jsonify({
        'status': 'healthy',
        'models_available': len(MODELS),
        'model_categories': len(MODEL_CATEGORIES),
        'styles_available': sum(len(cat.get('styles', [])) for cat in STYLE_CATEGORIES),
        'style_categories': len(STYLE_CATEGORIES),
        'advanced_features': {
            'model_filtering': True,
            'style_filtering': True,
            'compatibility_matching': True,
            'intelligent_recommendations': True,
            'detailed_metadata': True
        }
    })

@app.route('/api/models/filter', methods=['POST'])
def filter_models():
    """Filter models based on criteria"""
    try:
        data = request.get_json() or {}
        category = data.get('category')
        difficulty = data.get('difficulty')
        min_quality = data.get('min_quality')
        min_speed = data.get('min_speed')
        
        filtered_models = data_manager.filter_models_by_criteria(
            category=category,
            difficulty=difficulty,
            min_quality=min_quality,
            min_speed=min_speed
        )
        
        return jsonify({
            'success': True,
            'models': filtered_models,
            'count': len(filtered_models)
        })
        
    except Exception as e:
        app.logger.error(f"Model filtering error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/styles/filter', methods=['POST'])
def filter_styles():
    """Filter styles based on criteria"""
    try:
        data = request.get_json() or {}
        category = data.get('category')
        difficulty = data.get('difficulty')
        complexity_level = data.get('complexity_level')
        min_popularity = data.get('min_popularity')
        
        filtered_styles = data_manager.filter_styles_by_criteria(
            category=category,
            difficulty=difficulty,
            complexity_level=complexity_level,
            min_popularity=min_popularity
        )
        
        return jsonify({
            'success': True,
            'styles': filtered_styles,
            'count': len(filtered_styles)
        })
        
    except Exception as e:
        app.logger.error(f"Style filtering error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compatibility/<model_name>')
def get_model_compatibility(model_name):
    """Get compatibility information for a specific model"""
    try:
        model_details = data_manager.get_model_details(model_name)
        if not model_details:
            return jsonify({'error': 'Model not found'}), 404
            
        compatible_styles = data_manager.get_compatible_styles_for_model(model_name)
        
        return jsonify({
            'success': True,
            'model': model_details,
            'compatible_styles': compatible_styles
        })
        
    except Exception as e:
        app.logger.error(f"Compatibility error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get intelligent recommendations based on prompt"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        current_model = data.get('model')
        current_style = data.get('style')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
            
        recommendations = data_manager.get_recommendations(prompt, current_model, current_style)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        app.logger.error(f"Recommendations error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def request_too_large(error):
    """Handle request too large errors"""
    return jsonify({'error': 'Request too large'}), 413

# Configure app settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
app.config['JSON_SORT_KEYS'] = False

if __name__ == "__main__":
    # Ensure all directories exist before starting
    for folder in [GENERATED_IMAGES_FOLDER, STATIC_FOLDER, MODELS_FOLDER, STYLES_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # Create default JSON files if they don't exist
    styles_file = 'styles.json'
    if not os.path.exists(styles_file):
        with open(styles_file, 'w', encoding='utf-8') as f:
            json.dump(STYLE_CATEGORIES, f, indent=2, ensure_ascii=False)
        print(f"Created default {styles_file}")
    
    models_file = 'models.json'
    if not os.path.exists(models_file):
        with open(models_file, 'w', encoding='utf-8') as f:
            json.dump(MODEL_CATEGORIES, f, indent=2, ensure_ascii=False)
        print(f"Created default {models_file}")
    
    print("Starting DreamlitAI server...")
    print(f"Generated images will be stored in: {GENERATED_IMAGES_FOLDER}")
    print(f"Static files served from: {STATIC_FOLDER}")
    print(f"Available models: {len(MODELS)}")
    print(f"Available model categories: {len(MODEL_CATEGORIES)}")
    print(f"Available styles: {sum(len(cat.get('styles', [])) for cat in STYLE_CATEGORIES)}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)