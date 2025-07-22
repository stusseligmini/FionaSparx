#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Image Generator - Fallback compatible version
Works with or without GPU, handles missing dependencies gracefully
"""

import logging
import time
import random
from typing import List, Optional, Dict, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Try to import AI libraries, fallback if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False

class AdvancedImageGenerator:
    """
    Advanced Image Generator with robust fallback system
    Works even without GPU or AI libraries installed
    """
    
    def __init__(self, config: Dict[str, Any], performance_monitor=None):
        self.config = config
        self.performance_monitor = performance_monitor
        self.device = "cpu"
        self.pipe = None
        
        # Performance stats
        self.stats = {
            "generated": 0,
            "errors": 0,
            "fallbacks": 0,
            "total_time": 0
        }
        
        # Try to initialize real pipeline
        if TORCH_AVAILABLE and DIFFUSERS_AVAILABLE:
            try:
                self._initialize_pipeline()
                logger.info("✅ Advanced image generator ready with AI models")
            except Exception as e:
                logger.warning(f"AI model initialization failed: {e}")
                logger.info("🔄 Running in fallback mode")
        else:
            logger.info("🔄 AI libraries not available, running in fallback mode")
    
    def _initialize_pipeline(self):
        """Initialize AI pipeline if available"""
        if not TORCH_AVAILABLE or not DIFFUSERS_AVAILABLE:
            return
        
        try:
            # Detect device
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("🚀 Using CUDA GPU")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps" 
                logger.info("🍎 Using Apple Metal")
            else:
                self.device = "cpu"
                logger.info("💻 Using CPU")
            
            # Load model
            model_id = self.config.get("image_model", "runwayml/stable-diffusion-v1-5")
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            self.pipe = self.pipe.to(self.device)
            
            logger.info(f"✅ Pipeline loaded on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            self.pipe = None
    
    def generate_enhanced_image(
        self, 
        prompt: str, 
        style: str = "realistic", 
        quality: str = "medium",
        num_images: int = 1
    ) -> List[Image.Image]:
        """Generate images with AI or fallback"""
        return self.generate_safe_image(prompt, style, quality, num_images)
    
    def generate_safe_image(
        self, 
        prompt: str, 
        style: str = "realistic", 
        quality: str = "medium",
        num_images: int = 1
    ) -> List[Image.Image]:
        """
        Generate images safely with fallback
        """
        start_time = time.time()
        
        try:
            # Try AI generation first
            if self.pipe is not None and TORCH_AVAILABLE:
                images = self._generate_with_ai(prompt, style, quality, num_images)
            else:
                # Fallback to placeholder generation
                images = self._generate_placeholder_images(prompt, num_images)
                self.stats["fallbacks"] += 1
            
            # Update stats
            generation_time = time.time() - start_time
            self.stats["generated"] += len(images)
            self.stats["total_time"] += generation_time
            
            logger.info(f"✅ Generated {len(images)} images in {generation_time:.2f}s")
            return images
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Image generation failed: {e}")
            return self._generate_placeholder_images(prompt, num_images)
    
    def _generate_with_ai(
        self, 
        prompt: str, 
        style: str, 
        quality: str, 
        num_images: int
    ) -> List[Image.Image]:
        """Generate with AI pipeline"""
        
        # Enhance prompt
        enhanced_prompt = self._enhance_prompt(prompt, style, quality)
        
        # Generation parameters
        params = {
            "prompt": enhanced_prompt,
            "num_images_per_prompt": num_images,
            "num_inference_steps": 20 if quality == "medium" else 15,
            "guidance_scale": 7.5,
            "width": self.config.get("image_size", [512, 512])[0],
            "height": self.config.get("image_size", [512, 512])[1]
        }
        
        logger.info(f"🎨 AI generating: {prompt[:50]}...")
        
        # Generate
        with torch.autocast(self.device, enabled=self.device != "cpu"):
            result = self.pipe(**params)
        
        return result.images
    
    def _enhance_prompt(self, prompt: str, style: str, quality: str) -> str:
        """Enhance prompt with style and quality"""
        style_modifiers = {
            "realistic": "photorealistic, high quality, professional photography",
            "artistic": "artistic, creative, beautiful composition",
            "cinematic": "cinematic lighting, dramatic",
            "lifestyle": "lifestyle photography, natural, candid"
        }
        
        quality_modifiers = {
            "high": "8k, ultra detailed, masterpiece",
            "medium": "4k, detailed, good quality", 
            "fast": "good quality"
        }
        
        enhanced = f"{prompt}, {style_modifiers.get(style, '')}, {quality_modifiers.get(quality, '')}"
        enhanced += ", no blur, no artifacts, clean"
        
        return enhanced
    
    def _generate_placeholder_images(self, prompt: str, num_images: int) -> List[Image.Image]:
        """Generate beautiful placeholder images"""
        images = []
        
        # Color schemes for different prompts
        color_schemes = {
            "landscape": [(135, 206, 235), (255, 218, 185), (144, 238, 144)],
            "portrait": [(255, 182, 193), (221, 160, 221), (176, 196, 222)],
            "fashion": [(0, 0, 0), (255, 255, 255), (128, 128, 128)],
            "lifestyle": [(255, 239, 213), (250, 128, 114), (152, 251, 152)]
        }
        
        # Detect content type from prompt
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["landscape", "sunset", "nature"]):
            colors = color_schemes["landscape"]
        elif any(word in prompt_lower for word in ["portrait", "face", "person"]):
            colors = color_schemes["portrait"] 
        elif any(word in prompt_lower for word in ["fashion", "clothing", "style"]):
            colors = color_schemes["fashion"]
        else:
            colors = color_schemes["lifestyle"]
        
        size = tuple(self.config.get("image_size", [512, 512]))
        
        for i in range(num_images):
            # Create gradient background
            image = Image.new("RGB", size, colors[i % len(colors)])
            
            # Add subtle gradient effect
            draw = ImageDraw.Draw(image)
            
            # Create geometric pattern
            for j in range(0, size[0], 50):
                for k in range(0, size[1], 50):
                    if (j + k) % 100 == 0:
                        # Add subtle squares
                        square_color = tuple(max(0, c - 20) for c in colors[i % len(colors)])
                        draw.rectangle([j, k, j+30, k+30], fill=square_color)
            
            # Add text overlay
            try:
                font_size = max(20, size[0] // 25)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Create content text
                content_lines = [
                    "FionaSparx AI",
                    "Generated Content",
                    f"Style: {prompt[:20]}...",
                    f"Image {i+1}/{num_images}"
                ]
                
                # Calculate text position
                y_offset = size[1] // 3
                for line in content_lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (size[0] - text_width) // 2
                    
                    # Add text shadow
                    draw.text((x+2, y_offset+2), line, fill=(0, 0, 0, 128), font=font)
                    # Add main text
                    draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
                    y_offset += font_size + 10
                    
            except Exception as e:
                logger.debug(f"Text overlay failed: {e}")
            
            images.append(image)
        
        logger.info(f"📦 Generated {num_images} placeholder images")
        return images
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.stats.copy()
        stats.update({
            "device": self.device,
            "ai_available": self.pipe is not None,
            "torch_available": TORCH_AVAILABLE,
            "diffusers_available": DIFFUSERS_AVAILABLE
        })
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.pipe is not None:
                del self.pipe
                self.pipe = None
            
            if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ Image generator cleanup completed")
            
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

# Alias for compatibility
EnhancedImageGenerator = AdvancedImageGenerator
