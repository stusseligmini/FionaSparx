import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageEnhance, ImageFilter
import random
import logging

logger = logging.getLogger(__name__)

class AdvancedImageGenerator:
    """Avansert AI bildegenerator med kvalitetsforbedringer"""
    
    def __init__(self, config):
        self.config = config
        self.device = self._setup_device()
        self.model_id = config.get("image_model", "stabilityai/stable-diffusion-2-1")
        self.performance_stats = {"generated": 0, "errors": 0}
        self.setup_pipeline()
    
    def _setup_device(self):
        """Smart enhetshåndtering"""
        device_config = self.config.get("device", "auto")
        
        if device_config == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info("🚀 Bruker CUDA GPU")
            elif torch.backends.mps.is_available():
                device = "mps"
                logger.info("🍎 Bruker Apple Metal")
            else:
                device = "cpu"
                logger.info("💻 Bruker CPU")
        else:
            device = device_config
            
        return device
    
    def setup_pipeline(self):
        """Sett opp optimalisert pipeline"""
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                safety_checker=None if not self.config.get("safety_checker", True) else None,
                requires_safety_checker=False
            )
            
            # Optimaliseringer
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
            self.pipe = self.pipe.to(self.device)
            
            if self.device == "cuda":
                self.pipe.enable_memory_efficient_attention()
                self.pipe.enable_xformers_memory_efficient_attention()
            
            logger.info(f"✅ Pipeline klar på {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Feil ved oppsett av pipeline: {e}")
            raise
    
    def generate_enhanced_image(self, prompt, style="realistic", quality="high", num_images=1):
        """Generer forbedrede bilder med stilkontroll"""
        try:
            # Forbedre prompt basert på stil
            enhanced_prompt = self._enhance_prompt(prompt, style, quality)
            
            # Genereringsparametere
            params = self._get_generation_params(quality)
            
            logger.info(f"🎨 Genererer bilde: {prompt[:50]}...")
            
            with torch.autocast(self.device):
                result = self.pipe(
                    prompt=enhanced_prompt,
                    num_images_per_prompt=num_images,
                    **params
                )
            
            # Post-prosessering
            enhanced_images = []
            for img in result.images:
                enhanced_img = self._post_process_image(img, quality)
                enhanced_images.append(enhanced_img)
            
            self.performance_stats["generated"] += len(enhanced_images)
            logger.info("✅ Bilde generert og forbedret")
            
            return enhanced_images
            
        except Exception as e:
            self.performance_stats["errors"] += 1
            logger.error(f"❌ Feil ved bildegenerering: {e}")
            return []
    
    def _enhance_prompt(self, prompt, style, quality):
        """Forbedre prompt med stil og kvalitet"""
        style_modifiers = {
            "realistic": "photorealistic, high quality, detailed, professional photography",
            "artistic": "artistic, creative, beautiful composition, aesthetic",
            "cinematic": "cinematic lighting, dramatic, film photography, high quality",
            "fashion": "fashion photography, professional, studio lighting, high fashion",
            "lifestyle": "lifestyle photography, natural, candid, authentic"
        }
        
        quality_modifiers = {
            "high": "8k, ultra detailed, sharp focus, masterpiece",
            "medium": "4k, detailed, good quality",
            "fast": "good quality"
        }
        
        enhanced = f"{prompt}, {style_modifiers.get(style, '')}, {quality_modifiers.get(quality, '')}"
        enhanced += ", no blur, no artifacts, clean"
        
        return enhanced
    
    def _get_generation_params(self, quality):
        """Hent parametere basert på kvalitet"""
        size = self.config.get("image_size", [768, 768])
        
        params = {
            "width": size[0],
            "height": size[1],
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
        
        if quality == "high":
            params.update({
                "guidance_scale": 8.5,
                "num_inference_steps": 50
            })
        elif quality == "fast":
            params.update({
                "guidance_scale": 7.0,
                "num_inference_steps": 20
            })
        
        return params
    
    def _post_process_image(self, image, quality):
        """Post-prosesser bilde for forbedret kvalitet"""
        if quality == "high":
            # Forbedre skarphet
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Forbedre kontrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Forbedre farger
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)
        
        return image
    
    def get_performance_stats(self):
        """Hent ytelsesstatistikk"""
        return self.performance_stats
    
    def cleanup(self):
        """Rydd opp ressurser"""
        try:
            if hasattr(self, 'pipe'):
                del self.pipe
            torch.cuda.empty_cache()
        except:
            pass
