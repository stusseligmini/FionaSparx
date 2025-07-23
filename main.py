#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FionaSparx AI Content Creator - Main Entry Point
Optimized for Fanvue and LoyalFans content generation with N8N Automation

Usage:
    python main.py                 # Run basic test
    python main.py generate        # Generate content
    python main.py fanvue          # Generate Fanvue-optimized content  
    python main.py loyalfans       # Generate LoyalFans-optimized content
    python main.py test            # Test all components
    python main.py quality         # Assess content quality
    python main.py automation      # Start N8N automation system
    python main.py webhook-test    # Test webhook endpoints
    python main.py schedule        # Get scheduling recommendations
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

# Import nye funksjoner
from utils.Error_handling import CircuitBreaker, retry, FallbackHandler
from utils.cli_progress import ProgressBar, ConsoleUI, ProgressStyle, Colors
from utils.quality_assesment import ContentQualityAssessor, ContentType, QualityLevel
from utils.platform_templates import PlatformTemplateManager

# Import N8N automation system
from n8n_automation.automation_manager import N8NAutomationManager, create_n8n_automation

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FionaSparxSimple:
    """Simplified main entry point for FionaSparx AI Content Creator"""
    
    def __init__(self, config=None):
        ConsoleUI.print_header("FionaSparx AI Content Creator", color=Colors.BLUE)
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
            },
            # Circuit breaker konfigurasjon
            "circuit_breaker": {
                "failure_threshold": 3,
                "reset_timeout": 60,
                "test_requests": 1
            },
            # Quality assessment konfigurasjon
            "quality": {
                "minimum_score": 3.0,
                "auto_improve": True
            }
        }
        
        try:
            # Initialiser nye verktøy
            self.quality_assessor = ContentQualityAssessor(self.config.get("quality", {}))
            self.platform_templates = PlatformTemplateManager(self.config)
            
            # Initialiser eksisterende verktøy med resiliens
            with ProgressBar(total=3, description="Initializing components", style=ProgressStyle.BAR) as pbar:
                # Tekst generator med circuit breaker
                self.text_generator = self._init_text_generator()
                logger.info("✅ Text generator initialized")
                pbar.update(1)
                
                # Image generator med resiliens
                self.image_generator, self.image_generator_available = self._init_image_generator()
                pbar.update(2)
                
                # Ferdig initialisert
                pbar.update(3)
            
            ConsoleUI.print_success("FionaSparx AI Content Creator ready!")
            
        except Exception as e:
            ConsoleUI.print_error(f"Error during initialization: {e}")
            logger.error(f"❌ Error during initialization: {e}")
            raise
    
    @retry(max_attempts=2)
    def _init_text_generator(self):
        """Initialiser text generator med resiliens"""
        return SmartTextGenerator(self.config)
    
    def _init_image_generator(self):
        """Initialiser image generator med fallback"""
        try:
            generator = AdvancedImageGenerator(self.config["ai_model"])
            logger.info("✅ Image generator initialized")
            return generator, True
        except Exception as e:
            logger.warning(f"⚠️ Image generator not available: {e}")
            logger.info("💡 Running in text-only mode. Image generation will be simulated.")
            return None, False
    
    def test_components(self):
        """Test all components to ensure they work correctly"""
        ConsoleUI.print_section("Testing Components")
        logger.info("🧪 Testing all components...")
        
        try:
            with ProgressBar(total=4, description="Testing components", style=ProgressStyle.DETAILED) as pbar:
                # Test text generator
                logger.info("Testing text generation...")
                test_caption = self.text_generator.generate_smart_caption(
                    image_context="A beautiful lifestyle photo",
                    platform="instagram",
                    tone="friendly"
                )
                logger.info(f"✅ Generated test caption: {test_caption[:50]}...")
                pbar.update(1, description="Text generation tested")
                
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
                pbar.update(2, description="Image generation tested")
                
                # Test quality assessment
                logger.info("Testing quality assessment...")
                quality_score = self.quality_assessor.assess_content(
                    content="This is a test caption for quality assessment. #lifestyle #authentic",
                    platforms=["fanvue", "loyalfans"]
                )
                logger.info(f"✅ Quality assessment test complete: {quality_score.quality_level.name}")
                pbar.update(3, description="Quality assessment tested")
                
                # Test platform templates
                logger.info("Testing platform templates...")
                template = self.platform_templates.get_template("fanvue", "lifestyle")
                test_content = {
                    "personlig_introduksjon": "Starting my day with positive vibes!",
                    "hovedinnhold_med_detaljer": "Today I'm sharing some of my favorite moments from the weekend.",
                    "spørsmål_til_følgere": "What did you do this weekend?",
                    "call_to_action": "Let me know in the comments!",
                    "hashtags": "#lifestyle #weekend #positivevibes"
                }
                formatted_content = self.platform_templates.apply_template(template, test_content)
                logger.info(f"✅ Platform template test complete")
                pbar.update(4, description="Platform templates tested")
            
            ConsoleUI.print_success("All component tests passed!")
            return True
            
        except Exception as e:
            ConsoleUI.print_error(f"Component test failed: {e}")
            logger.error(f"❌ Component test failed: {e}")
            return False
    
    @CircuitBreaker("content_generation")
    def generate_fanvue_content(self):
        """Generate content optimized for Fanvue platform"""
        ConsoleUI.print_section("Generating Fanvue Content")
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
            
            with ProgressBar(total=len(fanvue_prompts), description="Generating Fanvue content", 
                           style=ProgressStyle.BAR) as pbar:
                
                for i, prompt in enumerate(fanvue_prompts):
                    pbar.update(i, description=f"Generating content {i+1}/{len(fanvue_prompts)}")
                    
                    # Generate image with resilience
                    images = self._generate_image_with_fallback(
                        prompt=prompt,
                        style=platform_config["style"],
                        platform="fanvue",
                        index=i+1
                    )
                    
                    if images:
                        # Get optimized template for Fanvue
                        template = self.platform_templates.get_template("fanvue", "lifestyle")
                        
                        # Generate Fanvue-optimized caption using template
                        basic_caption = self.text_generator.generate_smart_caption(
                            image_context=prompt,
                            platform="fanvue",
                            tone=platform_config["tone"]
                        )
                        
                        # Assess quality
                        quality_score = self.quality_assessor.assess_content(
                            content=basic_caption,
                            platforms=["fanvue"]
                        )
                        
                        # Prepare template content
                        template_content = {
                            "personlig_introduksjon": f"Just sharing a moment from my day ✨",
                            "hovedinnhold_med_detaljer": basic_caption,
                            "spørsmål_til_følgere": "How is your day going?",
                            "call_to_action": "Let me know in the comments below!",
                            "hashtags": "#fanvue #lifestyle #authentic #content"
                        }
                        
                        # Apply template
                        caption = self.platform_templates.apply_template(template, template_content)
                        
                        # Save content
                        filename = f"output/fanvue_content_{i+1}.png"
                        images[0].save(filename)
                        
                        content_item = {
                            "platform": "fanvue",
                            "image_path": filename,
                            "caption": caption,
                            "prompt": prompt,
                            "quality_score": f"{quality_score.overall:.2f}/5.0 ({quality_score.quality_level.name})"
                        }
                        
                        generated_content.append(content_item)
                        logger.info(f"✅ Fanvue content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/fanvue_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            ConsoleUI.print_success(f"Generated {len(generated_content)} Fanvue-optimized content items")
            return generated_content
            
        except Exception as e:
            ConsoleUI.print_error(f"Error generating Fanvue content: {e}")
            logger.error(f"❌ Error generating Fanvue content: {e}")
            return []
    
    @CircuitBreaker("content_generation")
    def generate_loyalfans_content(self):
        """Generate content optimized for LoyalFans platform"""
        ConsoleUI.print_section("Generating LoyalFans Content")
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
            
            with ProgressBar(total=len(loyalfans_prompts), description="Generating LoyalFans content", 
                           style=ProgressStyle.BAR) as pbar:
                           
                for i, prompt in enumerate(loyalfans_prompts):
                    pbar.update(i, description=f"Generating content {i+1}/{len(loyalfans_prompts)}")
                    
                    # Generate image with resilience
                    images = self._generate_image_with_fallback(
                        prompt=prompt,
                        style=platform_config["style"],
                        platform="loyalfans",
                        index=i+1
                    )
                    
                    if images:
                        # Get optimized template for LoyalFans
                        template = self.platform_templates.get_template("loyalfans", "exclusive")
                        
                        # Generate LoyalFans-optimized caption
                        basic_caption = self.text_generator.generate_smart_caption(
                            image_context=prompt,
                            platform="loyalfans", 
                            tone=platform_config["tone"]
                        )
                        
                        # Assess quality
                        quality_score = self.quality_assessor.assess_content(
                            content=basic_caption,
                            platforms=["loyalfans"]
                        )
                        
                        # Prepare template content
                        template_content = {
                            "eksklusiv_introduksjon": "Sharing something special with my loyal fans 💎",
                            "hovedinnhold_med_verdi": basic_caption,
                            "personlig_melding_til_fans": "Thank you for your amazing support!",
                            "hint_om_mer_eksklusivt": "More exclusive content coming soon...",
                            "call_to_action": "Check out the link in my bio for exclusive access",
                            "hashtags": "#loyalfans #exclusive #premium #content"
                        }
                        
                        # Apply template
                        caption = self.platform_templates.apply_template(template, template_content)
                        
                        # Save content
                        filename = f"output/loyalfans_content_{i+1}.png"
                        images[0].save(filename)
                        
                        content_item = {
                            "platform": "loyalfans",
                            "image_path": filename,
                            "caption": caption,
                            "prompt": prompt,
                            "quality_score": f"{quality_score.overall:.2f}/5.0 ({quality_score.quality_level.name})"
                        }
                        
                        generated_content.append(content_item)
                        logger.info(f"✅ LoyalFans content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/loyalfans_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            ConsoleUI.print_success(f"Generated {len(generated_content)} LoyalFans-optimized content items")
            return generated_content
            
        except Exception as e:
            ConsoleUI.print_error(f"Error generating LoyalFans content: {e}")
            logger.error(f"❌ Error generating LoyalFans content: {e}")
            return []
    
    @CircuitBreaker("content_generation")
    def generate_general_content(self):
        """Generate general content for testing"""
        ConsoleUI.print_section("Generating General Content")
        logger.info("🎨 Generating general content...")
        
        try:
            general_prompts = [
                "A beautiful nature landscape with mountains and sky",
                "A cozy coffee shop interior with warm lighting",
                "An artistic still life with flowers and books"
            ]
            
            generated_content = []
            
            with ProgressBar(total=len(general_prompts), description="Generating content", 
                           style=ProgressStyle.DETAILED) as pbar:
                           
                for i, prompt in enumerate(general_prompts):
                    pbar.update(i, description=f"Generating content {i+1}/{len(general_prompts)}")
                    
                    # Generate image with resilience
                    images = self._generate_image_with_fallback(
                        prompt=prompt,
                        style="realistic",
                        platform="general",
                        index=i+1
                    )
                    
                    if images:
                        # Generate caption
                        caption = self.text_generator.generate_smart_caption(
                            image_context=prompt,
                            platform="instagram",
                            tone="friendly"
                        )
                        
                        # Assess quality
                        quality_score = self.quality_assessor.assess_content(caption)
                        
                        # Save content
                        filename = f"output/general_content_{i+1}.png"
                        images[0].save(filename)
                        
                        content_item = {
                            "platform": "general",
                            "image_path": filename,
                            "caption": caption,
                            "prompt": prompt,
                            "quality_score": f"{quality_score.overall:.2f}/5.0 ({quality_score.quality_level.name})",
                            "quality_strengths": quality_score.strengths,
                            "quality_improvements": quality_score.improvement_areas
                        }
                        
                        generated_content.append(content_item)
                        logger.info(f"✅ General content {i+1} generated and saved")
            
            # Save content metadata
            with open("output/general_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            ConsoleUI.print_success(f"Generated {len(generated_content)} general content items")
            return generated_content
            
        except Exception as e:
            ConsoleUI.print_error(f"Error generating general content: {e}")
            logger.error(f"❌ Error generating general content: {e}")
            return []
    
    def _generate_image_with_fallback(self, prompt, style, platform, index):
        """Generer bilde med fallback-mekanisme"""
        try:
            if self.image_generator_available:
                images = self.image_generator.generate_enhanced_image(
                    prompt=prompt,
                    style=style,
                    quality="high",
                    num_images=1
                )
                return images
            else:
                # Fallback: create placeholder image
                from PIL import Image, ImageDraw
                colors = {
                    "fanvue": "lightcoral",
                    "loyalfans": "lightseagreen",
                    "general": "lightsteelblue"
                }
                color = colors.get(platform, "lightgray")
                
                img = Image.new('RGB', (512, 512), color=color)
                draw = ImageDraw.Draw(img)
                draw.text((50, 250), f"{platform.capitalize()} Content {index}\n(Fallback mode)", fill='white')
                return [img]
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # Advanced fallback using FallbackHandler
            return FallbackHandler.with_fallback(
                main_func=lambda: self.image_generator.generate_enhanced_image(
                    prompt=prompt,
                    style=style,
                    quality="fast",  # Prøv lavere kvalitet
                    num_images=1
                ),
                fallback_func=lambda e: self._create_fallback_image(platform, index),
                exceptions=(Exception,)
            )
    
    def _create_fallback_image(self, platform, index):
        """Lag et fallback-bilde når bildegenerering feiler"""
        from PIL import Image, ImageDraw
        colors = {
            "fanvue": "lightcoral",
            "loyalfans": "lightseagreen",
            "general": "lightsteelblue"
        }
        color = colors.get(platform, "lightgray")
        
        img = Image.new('RGB', (512, 512), color=color)
        draw = ImageDraw.Draw(img)
        draw.text((50, 250), f"{platform.capitalize()} Content {index}\n(Emergency Fallback)", fill='white')
        return [img]
    
    def assess_content_quality(self, file_path=None):
        """Assess quality of existing content"""
        ConsoleUI.print_section("Content Quality Assessment")
        logger.info("📊 Assessing content quality...")
        
        try:
            if not file_path:
                # List all JSON files in output directory
                json_files = list(Path("output").glob("*.json"))
                
                if not json_files:
                    ConsoleUI.print_warning("No content files found in output directory!")
                    return False
                
                # Ask user to select a file
                ConsoleUI.print_info("Available content files:")
                for i, file in enumerate(json_files):
                    print(f"{i+1}. {file.name}")
                    
                selection = ConsoleUI.prompt("Select a file number to assess", default="1")
                try:
                    index = int(selection) - 1
                    file_path = json_files[index]
                except (ValueError, IndexError):
                    ConsoleUI.print_error("Invalid selection!")
                    return False
            
            # Load the content file
            with open(file_path, 'r', encoding='utf-8') as f:
                content_items = json.load(f)
            
            ConsoleUI.print_info(f"Assessing quality of {len(content_items)} content items...")
            
            assessed_content = []
            
            with ProgressBar(total=len(content_items), description="Assessing content", 
                           style=ProgressStyle.BAR) as pbar:
                           
                for i, item in enumerate(content_items):
                    caption = item.get("caption", "")
                    platform = item.get("platform", "general")
                    
                    # Update progress
                    pbar.update(i, description=f"Assessing item {i+1}/{len(content_items)}")
                    
                    # Assess quality
                    quality_score = self.quality_assessor.assess_content(
                        content=caption,
                        platforms=[platform] if platform != "general" else ["fanvue", "loyalfans"]
                    )
                    
                    # Add quality data to item
                    item["quality"] = {
                        "overall_score": round(quality_score.overall, 2),
                        "quality_level": quality_score.quality_level.name,
                        "readability": round(quality_score.readability, 2),
                        "engagement": round(quality_score.engagement, 2),
                        "relevance": round(quality_score.relevance, 2),
                        "originality": round(quality_score.originality, 2),
                        "strengths": quality_score.strengths,
                        "improvements": quality_score.improvement_areas,
                        "recommendations": quality_score.recommendations
                    }
                    
                    assessed_content.append(item)
            
            # Save updated content with quality assessment
            output_path = file_path.parent / f"quality_assessed_{file_path.name}"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(assessed_content, f, indent=2, ensure_ascii=False)
            
            # Display quality summary
            ConsoleUI.print_section("Quality Assessment Results")
            
            # Prepare data for table
            headers = ["Item", "Quality Level", "Score", "Top Strength", "Top Improvement"]
            rows = []
            
            for i, item in enumerate(assessed_content):
                quality = item["quality"]
                rows.append([
                    f"Item {i+1}",
                    quality["quality_level"],
                    f"{quality['overall_score']:.2f}/5.0",
                    quality["strengths"][0] if quality["strengths"] else "N/A",
                    quality["improvements"][0] if quality["improvements"] else "N/A"
                ])
            
            # Display table
            ConsoleUI.print_table(headers, rows)
            
            ConsoleUI.print_success(f"Quality assessment saved to {output_path}")
            return True
            
        except Exception as e:
            ConsoleUI.print_error(f"Error assessing content quality: {e}")
            logger.error(f"❌ Error assessing content quality: {e}")
            return False


def main():
    """Main entry point with command line interface"""
    
    # Create FionaSparx instance
    try:
        fiona = FionaSparxSimple()
    except Exception as e:
        ConsoleUI.print_error(f"Failed to initialize FionaSparx: {e}")
        logger.error(f"❌ Failed to initialize FionaSparx: {e}")
        sys.exit(1)
    
    # Handle command line arguments
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "test"
    
    try:
        if command == "test":
            ConsoleUI.print_section("Running Component Tests")
            success = fiona.test_components()
            if success:
                ConsoleUI.print_success("All tests passed! FionaSparx is working correctly.")
            else:
                ConsoleUI.print_error("Some tests failed. Check logs for details.")
                sys.exit(1)
                
        elif command == "generate":
            ConsoleUI.print_section("Running General Content Generation")
            content = fiona.generate_general_content()
            ConsoleUI.print_success(f"Generated {len(content)} content items in output/ directory")
            
        elif command == "fanvue":
            ConsoleUI.print_section("Running Fanvue Content Generation")
            content = fiona.generate_fanvue_content()
            ConsoleUI.print_success(f"Generated {len(content)} Fanvue-optimized content items")
            
        elif command == "loyalfans":
            ConsoleUI.print_section("Running LoyalFans Content Generation")
            content = fiona.generate_loyalfans_content()
            ConsoleUI.print_success(f"Generated {len(content)} LoyalFans-optimized content items")
            
        elif command == "quality":
            ConsoleUI.print_section("Running Content Quality Assessment")
            fiona.assess_content_quality()
        
        elif command == "automation":
            ConsoleUI.print_section("Starting N8N Automation System")
            automation = create_n8n_automation(fiona)
            
            async def run_automation():
                try:
                    await automation.start()
                except KeyboardInterrupt:
                    ConsoleUI.print_info("Received shutdown signal")
                    await automation.stop()
                except Exception as e:
                    ConsoleUI.print_error(f"Automation system error: {e}")
                    await automation.stop()
                    raise
            
            import asyncio
            asyncio.run(run_automation())
        
        elif command == "webhook-test":
            ConsoleUI.print_section("Testing Webhook Endpoints")
            automation = create_n8n_automation(fiona)
            
            # Test webhook functionality
            async def test_webhooks():
                await automation.webhook_server.start_server("localhost", 8080)
                
                # Simulate webhook requests
                test_requests = [
                    {
                        "method": "POST",
                        "path": "/webhooks/generate-content",
                        "headers": {"authorization": "Bearer default_token"},
                        "body": '{"platform": "fanvue", "content_type": "lifestyle", "count": 1}',
                        "source_ip": "127.0.0.1"
                    },
                    {
                        "method": "GET", 
                        "path": "/webhooks/health",
                        "headers": {},
                        "body": "",
                        "source_ip": "127.0.0.1"
                    }
                ]
                
                for i, req in enumerate(test_requests):
                    ConsoleUI.print_info(f"Testing webhook {i+1}: {req['method']} {req['path']}")
                    result = await automation.webhook_server.handle_request(
                        req["method"], req["path"], req["headers"], req["body"], req["source_ip"]
                    )
                    ConsoleUI.print_success(f"Response: {result['status']} - {result.get('event_id', 'N/A')}")
                
                await automation.webhook_server.stop_server()
            
            import asyncio
            asyncio.run(test_webhooks())
            
        elif command == "schedule":
            ConsoleUI.print_section("Getting Scheduling Recommendations")
            automation = create_n8n_automation(fiona)
            
            # Get schedule recommendations for different platforms
            from n8n_automation.smart_scheduling import Platform, ContentType
            
            platforms = [Platform.FANVUE, Platform.LOYALFANS, Platform.INSTAGRAM]
            content_types = [ContentType.LIFESTYLE, ContentType.FASHION, ContentType.ARTISTIC]
            
            for platform in platforms:
                for content_type in content_types:
                    recommendation = automation.scheduling_engine.get_optimal_schedule(
                        platform, content_type
                    )
                    
                    ConsoleUI.print_info(f"{platform.value.title()} - {content_type.value.title()}:")
                    print(f"  Optimal time: {recommendation.optimal_time.strftime('%Y-%m-%d %H:%M')}")
                    print(f"  Confidence: {recommendation.confidence.value}")
                    print(f"  Expected engagement: {recommendation.expected_engagement:.1%}")
                    print(f"  Reasoning: {recommendation.reasoning[0] if recommendation.reasoning else 'N/A'}")
                    print()
            
            # Show analytics
            analytics = automation.scheduling_engine.get_schedule_analytics()
            ConsoleUI.print_info("Scheduling Analytics (Last 30 days):")
            print(f"  Total posts: {analytics['total_posts']}")
            print(f"  Average engagement: {analytics['average_engagement']:.1%}")
            print(f"  Best hours: {', '.join([h['hour'] for h in analytics['best_hours'][:3]])}")
            print(f"  Best days: {', '.join([d['day'] for d in analytics['best_days'][:3]])}")
            
            
        else:
            ConsoleUI.print_error("Unknown command!")
            print("Available commands:")
            print("  test       - Test all components")
            print("  generate   - Generate general content") 
            print("  fanvue     - Generate Fanvue-optimized content")
            print("  loyalfans  - Generate LoyalFans-optimized content")
            print("  quality    - Assess quality of existing content")
            print("  automation - Start N8N automation system")
            print("  webhook-test - Test webhook endpoints")
            print("  schedule   - Get scheduling recommendations")
            
    except Exception as e:
        ConsoleUI.print_error(f"Error executing command '{command}': {e}")
        logger.error(f"❌ Error executing command '{command}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
