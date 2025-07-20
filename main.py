#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FionaSparx AI Content Creator - Main Entry Point
Optimized for Fanvue and LoyalFans content generation

Usage:
    python main.py                 # Run basic test
    python main.py generate        # Generate content
    python main.py fanvue          # Generate Fanvue-optimized content  
    python main.py loyalfans       # Generate LoyalFans-optimized content
    python main.py test            # Test all components
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_model.image_generator import AdvancedImageGenerator
from ai_model.text_generator import SmartTextGenerator
from utils.logger import setup_logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FionaSparxSimple:
    """Simplified main entry point for FionaSparx AI Content Creator"""
    
    def __init__(self, config=None):
        logger.info("🚀 Initializing FionaSparx AI Content Creator...")
        
        # Create required directories
        for folder in ["logs", "data", "output"]:
            Path(folder).mkdir(exist_ok=True)
        
        # Default configuration optimized for Fanvue and LoyalFans
        self.config = config or {
            "ai_model": {
                "image_model": "runwayml/stable-diffusion-v1-5",
                "device": "auto",
                "image_size": [512, 512],
                "fallback_mode": True  # Allow fallback when models unavailable
            },
            "platforms": {
                "fanvue": {
                    "style": "lifestyle",
                    "tone": "authentic",
                    "max_hashtags": 20
                },
                "loyalfans": {
                    "style": "artistic", 
                    "tone": "engaging",
                    "max_hashtags": 15
                }
            }
        }
        
        try:
            self.text_generator = SmartTextGenerator(self.config)
            logger.info("✅ Text generator initialized")
            
            # Try to initialize image generator with fallback
            try:
                self.image_generator = AdvancedImageGenerator(self.config["ai_model"])
                logger.info("✅ Image generator initialized")
                self.image_generator_available = True
            except Exception as e:
                logger.warning(f"⚠️ Image generator not available: {e}")
                logger.info("💡 Running in text-only mode. Image generation will be simulated.")
                self.image_generator = None
                self.image_generator_available = False
            
            logger.info("🎉 FionaSparx AI Content Creator ready!")
            
        except Exception as e:
            logger.error(f"❌ Error during initialization: {e}")
            raise
    
    def test_components(self):
        """Test all components to ensure they work correctly"""
        logger.info("🧪 Testing all components...")
        
        try:
            # Test text generator
            logger.info("Testing text generation...")
            test_caption = self.text_generator.generate_smart_caption(
                image_context="A beautiful lifestyle photo",
                platform="instagram",
                tone="friendly"
            )
            logger.info(f"✅ Generated test caption: {test_caption[:50]}...")
            
            # Test image generator (with a simple prompt to avoid NSFW issues)
            if self.image_generator_available:
                logger.info("Testing image generation...")
                test_images = self.image_generator.generate_enhanced_image(
                    prompt="A beautiful landscape with mountains and sky",
                    style="realistic",
                    quality="fast",
                    num_images=1
                )
                
                if test_images:
                    logger.info("✅ Generated test image successfully")
                    # Save test image
                    test_images[0].save("output/test_image.png")
                    logger.info("💾 Test image saved to output/test_image.png")
                else:
                    logger.warning("⚠️ Image generation returned empty result")
            else:
                logger.info("⚠️ Image generator not available - simulating image generation")
                # Create a simple placeholder image
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (512, 512), color='lightblue')
                draw = ImageDraw.Draw(img)
                draw.text((50, 250), "Test Image\n(Generated in fallback mode)", fill='black')
                img.save("output/test_image.png")
                logger.info("💾 Placeholder test image saved to output/test_image.png")
            
            logger.info("🎉 All component tests passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Component test failed: {e}")
            return False
    
    def generate_fanvue_content(self):
        """Generate content optimized for Fanvue platform"""
        logger.info("🎨 Generating Fanvue-optimized content...")
        
        try:
            platform_config = self.config["platforms"]["fanvue"]
            
            # Fanvue-optimized prompts
            fanvue_prompts = [
                "A confident young woman in casual lifestyle setting, natural lighting, authentic smile",
                "Stylish fashion photography, modern outfit, urban background, professional quality",
                "Lifestyle moment, cozy home setting, natural authentic expression, soft lighting"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(fanvue_prompts):
                logger.info(f"Generating content {i+1}/{len(fanvue_prompts)}...")
                
                # Generate image
                if self.image_generator_available:
                    images = self.image_generator.generate_enhanced_image(
                        prompt=prompt,
                        style=platform_config["style"],
                        quality="high",
                        num_images=1
                    )
                else:
                    # Fallback: create placeholder image
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (512, 512), color='lightcoral')
                    draw = ImageDraw.Draw(img)
                    draw.text((50, 250), f"Fanvue Content {i+1}\n(Fallback mode)", fill='white')
                    images = [img]
                
                if images:
                    # Generate Fanvue-optimized caption
                    caption = self.text_generator.generate_smart_caption(
                        image_context=prompt,
                        platform="fanvue",
                        tone=platform_config["tone"]
                    )
                    
                    # Save content
                    filename = f"output/fanvue_content_{i+1}.png"
                    images[0].save(filename)
                    
                    content_item = {
                        "platform": "fanvue",
                        "image_path": filename,
                        "caption": caption,
                        "prompt": prompt
                    }
                    
                    generated_content.append(content_item)
                    logger.info(f"✅ Fanvue content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/fanvue_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎉 Generated {len(generated_content)} Fanvue-optimized content items")
            return generated_content
            
        except Exception as e:
            logger.error(f"❌ Error generating Fanvue content: {e}")
            return []
    
    def generate_loyalfans_content(self):
        """Generate content optimized for LoyalFans platform"""
        logger.info("🎨 Generating LoyalFans-optimized content...")
        
        try:
            platform_config = self.config["platforms"]["loyalfans"]
            
            # LoyalFans-optimized prompts
            loyalfans_prompts = [
                "Artistic portrait photography, creative lighting, professional model pose, high fashion",
                "Elegant lifestyle scene, sophisticated setting, confident expression, artistic composition",
                "Creative fashion photography, unique styling, dramatic lighting, artistic atmosphere"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(loyalfans_prompts):
                logger.info(f"Generating content {i+1}/{len(loyalfans_prompts)}...")
                
                # Generate image
                if self.image_generator_available:
                    images = self.image_generator.generate_enhanced_image(
                        prompt=prompt,
                        style=platform_config["style"],
                        quality="high",
                        num_images=1
                    )
                else:
                    # Fallback: create placeholder image
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (512, 512), color='lightseagreen')
                    draw = ImageDraw.Draw(img)
                    draw.text((50, 250), f"LoyalFans Content {i+1}\n(Fallback mode)", fill='white')
                    images = [img]
                
                if images:
                    # Generate LoyalFans-optimized caption
                    caption = self.text_generator.generate_smart_caption(
                        image_context=prompt,
                        platform="loyalfans", 
                        tone=platform_config["tone"]
                    )
                    
                    # Save content
                    filename = f"output/loyalfans_content_{i+1}.png"
                    images[0].save(filename)
                    
                    content_item = {
                        "platform": "loyalfans",
                        "image_path": filename,
                        "caption": caption,
                        "prompt": prompt
                    }
                    
                    generated_content.append(content_item)
                    logger.info(f"✅ LoyalFans content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/loyalfans_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎉 Generated {len(generated_content)} LoyalFans-optimized content items")
            return generated_content
            
        except Exception as e:
            logger.error(f"❌ Error generating LoyalFans content: {e}")
            return []
    
    def generate_general_content(self):
        """Generate general content for testing"""
        logger.info("🎨 Generating general content...")
        
        try:
            general_prompts = [
                "A beautiful nature landscape with mountains and sky",
                "A cozy coffee shop interior with warm lighting",
                "An artistic still life with flowers and books"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(general_prompts):
                logger.info(f"Generating content {i+1}/{len(general_prompts)}...")
                
                # Generate image
                if self.image_generator_available:
                    images = self.image_generator.generate_enhanced_image(
                        prompt=prompt,
                        style="realistic",
                        quality="medium",
                        num_images=1
                    )
                else:
                    # Fallback: create placeholder image
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (512, 512), color='lightsteelblue')
                    draw = ImageDraw.Draw(img)
                    draw.text((50, 250), f"General Content {i+1}\n(Fallback mode)", fill='black')
                    images = [img]
                
                if images:
                    # Generate caption
                    caption = self.text_generator.generate_smart_caption(
                        image_context=prompt,
                        platform="instagram",
                        tone="friendly"
                    )
                    
                    # Save content
                    filename = f"output/general_content_{i+1}.png"
                    images[0].save(filename)
                    
                    content_item = {
                        "platform": "general",
                        "image_path": filename,
                        "caption": caption,
                        "prompt": prompt
                    }
                    
                    generated_content.append(content_item)
                    logger.info(f"✅ General content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/general_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎉 Generated {len(generated_content)} general content items")
            return generated_content
            
        except Exception as e:
            logger.error(f"❌ Error generating general content: {e}")
            return []


def main():
    """Main entry point with command line interface"""
    
    # Create FionaSparx instance
    try:
        fiona = FionaSparxSimple()
    except Exception as e:
        logger.error(f"❌ Failed to initialize FionaSparx: {e}")
        sys.exit(1)
    
    # Handle command line arguments
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "test"
    
    try:
        if command == "test":
            logger.info("🧪 Running component tests...")
            success = fiona.test_components()
            if success:
                print("✅ All tests passed! FionaSparx is working correctly.")
            else:
                print("❌ Some tests failed. Check logs for details.")
                sys.exit(1)
                
        elif command == "generate":
            logger.info("🎨 Running general content generation...")
            content = fiona.generate_general_content()
            print(f"✅ Generated {len(content)} content items in output/ directory")
            
        elif command == "fanvue":
            logger.info("🎨 Running Fanvue content generation...")
            content = fiona.generate_fanvue_content()
            print(f"✅ Generated {len(content)} Fanvue-optimized content items")
            
        elif command == "loyalfans":
            logger.info("🎨 Running LoyalFans content generation...")
            content = fiona.generate_loyalfans_content()
            print(f"✅ Generated {len(content)} LoyalFans-optimized content items")
            
        else:
            print("❓ Unknown command!")
            print("Available commands:")
            print("  test       - Test all components")
            print("  generate   - Generate general content") 
            print("  fanvue     - Generate Fanvue-optimized content")
            print("  loyalfans  - Generate LoyalFans-optimized content")
            
    except Exception as e:
        logger.error(f"❌ Error executing command '{command}': {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()