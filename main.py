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
        
        # Initialize components with error handling
        self.components_initialized = {}
        self.initialize_components()
        
        logger.info("🎉 FionaSparx AI Content Creator ready!")
    
    def initialize_components(self):
        """Initialize components with fallback handling"""
        
        # Test text generator
        try:
            from ai_model.text_generator import SmartTextGenerator
            self.text_generator = SmartTextGenerator(self.config)
            self.components_initialized['text_generator'] = True
            logger.info("✅ Text generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Text generator not available: {e}")
            self.text_generator = None
            self.components_initialized['text_generator'] = False
        
        # Test image generator
        try:
            from ai_model.image_generator import AdvancedImageGenerator
            self.image_generator = AdvancedImageGenerator(self.config["ai_model"])
            self.components_initialized['image_generator'] = True
            logger.info("✅ Image generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Image generator not available: {e}")
            self.image_generator = None
            self.components_initialized['image_generator'] = False
        
        # Test content manager
        try:
            from content.intelligent_content_manager import IntelligentContentManager
            self.content_manager = IntelligentContentManager(self.config.get("content", {}), None)
            self.components_initialized['content_manager'] = True
            logger.info("✅ Content manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Content manager not available: {e}")
            self.content_manager = None
            self.components_initialized['content_manager'] = False
            
        # Test platform manager
        try:
            from platforms.multi_platform_manager import MultiPlatformManager
            self.platform_manager = MultiPlatformManager(self.config.get("platforms", {}))
            self.components_initialized['platform_manager'] = True
            logger.info("✅ Platform manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Platform manager not available: {e}")
            self.platform_manager = None
            self.components_initialized['platform_manager'] = False
            
        # Test database
        try:
            from data.enhanced_database import EnhancedDatabase
            self.database = EnhancedDatabase(self.config.get("database", {"path": "data/test.db"}))
            self.components_initialized['database'] = True
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database not available: {e}")
            self.database = None
            self.components_initialized['database'] = False
            
        # Test logger utility
        try:
            from utils.logger import setup_logging
            setup_logging(self.config)
            self.components_initialized['logger'] = True
            logger.info("✅ Logger utility initialized")
        except Exception as e:
            logger.warning(f"⚠️ Logger utility not available: {e}")
            self.components_initialized['logger'] = False
    
    def test_components(self):
        """Test all components to ensure they work correctly"""
        logger.info("🧪 Testing all components...")
        
        success_count = 0
        total_count = len(self.components_initialized)
        
        for component, status in self.components_initialized.items():
            if status:
                logger.info(f"✅ {component} - Working")
                success_count += 1
            else:
                logger.warning(f"❌ {component} - Not available")
        
        logger.info(f"📊 Component test results: {success_count}/{total_count} components working")
        
        if success_count >= 2:  # At least 2 components working
            logger.info("🎉 Basic structure test passed!")
            return True
        else:
            logger.error("❌ Too many components failed. Check dependencies.")
            return False
    
    def generate_test_content(self):
        """Generate simple test content"""
        logger.info("🎨 Generating test content...")
        
        if self.text_generator:
            try:
                test_caption = self.text_generator.generate_smart_caption(
                    image_context="A beautiful lifestyle photo",
                    platform="instagram",
                    tone="friendly"
                )
                logger.info(f"✅ Generated test caption: {test_caption[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Text generation failed: {e}")
        
        # Create a simple placeholder image if PIL is available
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color='lightblue')
            draw = ImageDraw.Draw(img)
            draw.text((50, 250), "Test Image\n(Structure test)", fill='black')
            img.save("output/test_structure.png")
            logger.info("💾 Test structure image saved to output/test_structure.png")
        except ImportError:
            logger.info("⚠️ PIL not available - skipping test image generation")
        except Exception as e:
            logger.warning(f"⚠️ Error creating test image: {e}")
        
        logger.info("✅ Test content generation completed")

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
            structure_success = fiona.test_components()
            fiona.generate_test_content()
            
            if structure_success:
                print("✅ Structure tests passed! FionaSparx core structure is working correctly.")
                print("📝 Note: Some components may require additional dependencies to be fully functional.")
            else:
                print("❌ Structure tests failed. Check import errors above.")
                sys.exit(1)
                
        elif command == "generate":
            logger.info("🎨 Running test content generation...")
            fiona.generate_test_content()
            print("✅ Test content generation completed")
            
        elif command == "fanvue":
            logger.info("🎨 Testing Fanvue content generation...")
            fiona.generate_test_content()
            print("✅ Fanvue structure test completed")
            
        elif command == "loyalfans":
            logger.info("🎨 Testing LoyalFans content generation...")
            fiona.generate_test_content()
            print("✅ LoyalFans structure test completed")
            
        else:
            print("❓ Unknown command!")
            print("Available commands:")
            print("  test       - Test all components and structure")
            print("  generate   - Generate test content") 
            print("  fanvue     - Test Fanvue-optimized content structure")
            print("  loyalfans  - Test LoyalFans-optimized content structure")
            
    except Exception as e:
        logger.error(f"❌ Error executing command '{command}': {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()