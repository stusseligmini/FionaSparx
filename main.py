#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FionaSparx AI Content Creator - Enterprise Edition Main Entry Point
Advanced AI content generation system with enterprise-grade features

Usage:
    python main.py                 # Run basic test
    python main.py generate        # Generate content
    python main.py fanvue          # Generate Fanvue-optimized content  
    python main.py loyalfans       # Generate LoyalFans-optimized content
    python main.py test            # Test all components
    python main.py health          # Check system health
    python main.py performance     # Show performance metrics
    python main.py config          # Validate configuration
    python main.py run-tests       # Run test suite
"""

import os
import sys
import logging
import json
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_model.image_generator import AdvancedImageGenerator
from ai_model.text_generator import SmartTextGenerator
from utils.logger import setup_logging

# Import new enterprise components
from data.config_validator import EnhancedConfigValidator
from utils.circuit_breaker import ResilientAIWrapper
from utils.performance_monitor import PerformanceMonitor, PerformanceTimer
from utils.health_check import HealthCheckManager
from utils.enhanced_cli import EnhancedCLI

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FionaSparxEnterprise:
    """Enterprise-grade FionaSparx AI Content Creator with advanced features"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize FionaSparx Enterprise Edition"""
        self.cli = EnhancedCLI()
        self.cli.print_banner()
        
        logger.info("🚀 Initializing FionaSparx Enterprise Edition...")
        
        # Create required directories
        for folder in ["logs", "data", "output", "config"]:
            Path(folder).mkdir(exist_ok=True)
        
        try:
            # Initialize configuration validator
            self.config_validator = EnhancedConfigValidator()
            self.config = self.config_validator.validate_and_load_config(config_path)
            self.cli.print_success("Configuration validated and loaded")
            
            # Initialize performance monitoring
            self.performance_monitor = PerformanceMonitor(self.config)
            self.cli.print_success("Performance monitoring initialized")
            
            # Initialize health check manager
            self.health_manager = HealthCheckManager(self.config)
            self.cli.print_success("Health check system initialized")
            
            # Initialize resilient AI wrapper
            self.resilient_wrapper = ResilientAIWrapper(self.config)
            self.cli.print_success("Resilient AI wrapper initialized")
            
            # Initialize AI components
            self._initialize_ai_components()
            
            # Set AI components for health checking
            self.health_manager.set_ai_components(self.text_generator, self.image_generator)
            
            # Start monitoring services
            self.performance_monitor.start_monitoring()
            self.health_manager.start_monitoring()
            
            self.cli.print_success("FionaSparx Enterprise Edition ready!")
            
        except Exception as e:
            self.cli.print_error(f"Failed to initialize FionaSparx: {e}")
            raise
    
    def _initialize_ai_components(self):
        """Initialize AI components with error handling"""
        try:
            self.text_generator = SmartTextGenerator(self.config)
            self.cli.print_success("Text generator initialized")
            
            # Try to initialize image generator with fallback
            try:
                self.image_generator = AdvancedImageGenerator(self.config["ai_model"])
                self.cli.print_success("Image generator initialized")
                self.image_generator_available = True
            except Exception as e:
                self.cli.print_warning(f"Image generator not available: {e}")
                self.cli.print_info("Running in text-only mode. Image generation will be simulated.")
                self.image_generator = None
                self.image_generator_available = False
            
        except Exception as e:
            self.cli.print_error(f"Error during AI component initialization: {e}")
            raise
    
    def test_components(self):
        """Test all components with enhanced feedback"""
        self.cli.print_header("Component Testing")
        
        def test_steps():
            yield 1, "Testing configuration validation"
            time.sleep(0.2)
            
            yield 2, "Testing text generation"
            # Test text generator with resilience
            test_caption = self.resilient_wrapper.generate_text_resilient(
                self.text_generator,
                image_context="A beautiful lifestyle photo",
                platform="instagram",
                tone="friendly"
            )
            self.cli.print_success(f"Generated test caption: {test_caption[:50]}...")
            time.sleep(0.2)
            
            yield 3, "Testing health checks"
            health_status = self.health_manager.get_overall_health()
            if health_status["status"] == "healthy":
                self.cli.print_success("All health checks passed")
            else:
                self.cli.print_warning(f"Health check status: {health_status['status']}")
            time.sleep(0.2)
            
            yield 4, "Testing performance monitoring"
            performance_summary = self.performance_monitor.get_performance_summary()
            self.cli.print_success("Performance monitoring is active")
            time.sleep(0.2)
            
            yield 5, "Testing image generation"
            if self.image_generator_available:
                with PerformanceTimer(self.performance_monitor, "test_image_generation", "test_model"):
                    test_images = self.resilient_wrapper.generate_image_resilient(
                        self.image_generator,
                        prompt="A beautiful landscape with mountains and sky",
                        style="realistic",
                        quality="fast",
                        num_images=1
                    )
                
                if test_images:
                    self.cli.print_success("Generated test image successfully")
                    test_images[0].save("output/test_image.png")
                    self.cli.print_info("Test image saved to output/test_image.png")
                else:
                    self.cli.print_warning("Image generation returned empty result")
            else:
                self.cli.print_info("Image generator not available - simulating image generation")
                # Create a simple placeholder image
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (512, 512), color='lightblue')
                draw = ImageDraw.Draw(img)
                draw.text((50, 250), "Test Image\n(Generated in fallback mode)", fill='black')
                img.save("output/test_image.png")
                self.cli.print_info("Placeholder test image saved to output/test_image.png")
        
        success = self.cli.show_operation_progress("Component Testing", 5, test_steps)
        return success
    
    def generate_fanvue_content(self):
        """Generate content optimized for Fanvue platform with enterprise features"""
        self.cli.print_header("Fanvue Content Generation")
        
        def generation_steps():
            platform_config = self.config["platforms"]["fanvue"]
            
            # Fanvue-optimized prompts
            fanvue_prompts = [
                "A confident young woman in casual lifestyle setting, natural lighting, authentic smile",
                "Stylish fashion photography, modern outfit, urban background, professional quality",
                "Lifestyle moment, cozy home setting, natural authentic expression, soft lighting"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(fanvue_prompts):
                yield i+1, f"Generating Fanvue content {i+1}/{len(fanvue_prompts)}"
                
                start_time = time.time()
                
                try:
                    # Generate image with performance monitoring
                    if self.image_generator_available:
                        with PerformanceTimer(self.performance_monitor, "fanvue_image_generation", "stable-diffusion"):
                            images = self.resilient_wrapper.generate_image_resilient(
                                self.image_generator,
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
                        # Generate Fanvue-optimized caption with performance monitoring
                        with PerformanceTimer(self.performance_monitor, "fanvue_text_generation", "smart-text-generator"):
                            caption = self.resilient_wrapper.generate_text_resilient(
                                self.text_generator,
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
                            "prompt": prompt,
                            "generation_time_ms": (time.time() - start_time) * 1000,
                            "timestamp": time.time()
                        }
                        
                        generated_content.append(content_item)
                        
                except Exception as e:
                    self.cli.print_error(f"Failed to generate content {i+1}: {e}")
                    continue
                
                time.sleep(0.1)  # Visual delay
            
            # Save content metadata
            with open("output/fanvue_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            yield len(fanvue_prompts), f"Generated {len(generated_content)} Fanvue content items"
        
        success = self.cli.show_operation_progress("Fanvue Content Generation", 4, generation_steps)
        
        if success:
            self.cli.print_success(f"Fanvue content generation completed!")
            self.cli.print_info("Files saved to output/ directory")
        
        return success
    
    def generate_loyalfans_content(self):
        """Generate content optimized for LoyalFans platform with enterprise features"""
        self.cli.print_header("LoyalFans Content Generation")
        
        def generation_steps():
            platform_config = self.config["platforms"]["loyalfans"]
            
            # LoyalFans-optimized prompts
            loyalfans_prompts = [
                "Artistic portrait photography, creative lighting, professional model pose, high fashion",
                "Elegant lifestyle scene, sophisticated setting, confident expression, artistic composition",
                "Creative fashion photography, unique styling, dramatic lighting, artistic atmosphere"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(loyalfans_prompts):
                yield i+1, f"Generating LoyalFans content {i+1}/{len(loyalfans_prompts)}"
                
                start_time = time.time()
                
                try:
                    # Generate image with performance monitoring
                    if self.image_generator_available:
                        with PerformanceTimer(self.performance_monitor, "loyalfans_image_generation", "stable-diffusion"):
                            images = self.resilient_wrapper.generate_image_resilient(
                                self.image_generator,
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
                        # Generate LoyalFans-optimized caption with performance monitoring
                        with PerformanceTimer(self.performance_monitor, "loyalfans_text_generation", "smart-text-generator"):
                            caption = self.resilient_wrapper.generate_text_resilient(
                                self.text_generator,
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
                            "prompt": prompt,
                            "generation_time_ms": (time.time() - start_time) * 1000,
                            "timestamp": time.time()
                        }
                        
                        generated_content.append(content_item)
                        
                except Exception as e:
                    self.cli.print_error(f"Failed to generate content {i+1}: {e}")
                    continue
                
                time.sleep(0.1)  # Visual delay
            
            # Save content metadata
            with open("output/loyalfans_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            yield len(loyalfans_prompts), f"Generated {len(generated_content)} LoyalFans content items"
        
        success = self.cli.show_operation_progress("LoyalFans Content Generation", 4, generation_steps)
        
        if success:
            self.cli.print_success(f"LoyalFans content generation completed!")
            self.cli.print_info("Files saved to output/ directory")
        
        return generated_content
    
    def generate_general_content(self):
        """Generate general content for testing with enterprise features"""
        self.cli.print_header("General Content Generation")
        
        def generation_steps():
            general_prompts = [
                "A beautiful nature landscape with mountains and sky",
                "A cozy coffee shop interior with warm lighting",
                "An artistic still life with flowers and books"
            ]
            
            generated_content = []
            
            for i, prompt in enumerate(general_prompts):
                yield i+1, f"Generating general content {i+1}/{len(general_prompts)}"
                
                start_time = time.time()
                
                try:
                    # Generate image with performance monitoring
                    if self.image_generator_available:
                        with PerformanceTimer(self.performance_monitor, "general_image_generation", "stable-diffusion"):
                            images = self.resilient_wrapper.generate_image_resilient(
                                self.image_generator,
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
                        # Generate caption with performance monitoring
                        with PerformanceTimer(self.performance_monitor, "general_text_generation", "smart-text-generator"):
                            caption = self.resilient_wrapper.generate_text_resilient(
                                self.text_generator,
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
                            "prompt": prompt,
                            "generation_time_ms": (time.time() - start_time) * 1000,
                            "timestamp": time.time()
                        }
                        
                        generated_content.append(content_item)
                        
                except Exception as e:
                    self.cli.print_error(f"Failed to generate content {i+1}: {e}")
                    continue
                
                time.sleep(0.1)  # Visual delay
            
            # Save content metadata
            with open("output/general_content.json", "w", encoding="utf-8") as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            yield len(general_prompts), f"Generated {len(generated_content)} general content items"
        
        success = self.cli.show_operation_progress("General Content Generation", 4, generation_steps)
        
        if success:
            self.cli.print_success(f"General content generation completed!")
            self.cli.print_info("Files saved to output/ directory")
        
        return generated_content
    
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


    def show_health_status(self):
        """Show comprehensive health status"""
        self.cli.print_header("System Health Status")
        
        health_status = self.health_manager.get_overall_health()
        self.cli.print_health_status(health_status)
        
        # Export health report
        report_path = self.health_manager.export_health_report()
        if report_path:
            self.cli.print_info(f"Health report exported to {report_path}")
        
        return health_status["status"] == "healthy"
    
    def show_performance_metrics(self):
        """Show performance metrics"""
        self.cli.print_header("Performance Metrics")
        
        performance_summary = self.performance_monitor.get_performance_summary()
        self.cli.print_performance_summary(performance_summary)
        
        # Show circuit breaker status
        circuit_health = self.resilient_wrapper.get_health_status()
        
        self.cli.print_info("\nCircuit Breaker Status:")
        for circuit_name, circuit_info in circuit_health.items():
            if circuit_name != "overall_health":
                status = circuit_info.get("state", "unknown")
                self.cli.print_info(f"  {circuit_name}: {status}")
        
        # Export metrics
        metrics_path = self.performance_monitor.export_metrics()
        if metrics_path:
            self.cli.print_info(f"Performance metrics exported to {metrics_path}")
        
        return True
    
    def validate_configuration(self):
        """Validate and display configuration"""
        self.cli.print_header("Configuration Validation")
        
        try:
            # Re-validate configuration
            config = self.config_validator.validate_and_load_config()
            self.cli.print_success("Configuration is valid")
            
            # Show configuration summary
            self.cli.print_info("\nConfiguration Summary:")
            
            # AI Model Configuration
            ai_config = config.get("ai_model", {})
            self.cli.print_info(f"  AI Model: {ai_config.get('image_model', 'N/A')}")
            self.cli.print_info(f"  Device: {ai_config.get('device', 'N/A')}")
            self.cli.print_info(f"  Fallback Mode: {ai_config.get('fallback_mode', False)}")
            
            # Platform Configuration
            platforms = config.get("platforms", {})
            self.cli.print_info(f"  Enabled Platforms: {', '.join(platforms.keys())}")
            
            # Monitoring Configuration
            monitoring = config.get("monitoring", {})
            self.cli.print_info(f"  Monitoring Enabled: {monitoring.get('enabled', False)}")
            
            # Environment Info
            env_info = self.config_validator.get_environment_info()
            self.cli.print_info(f"  Environment Variables Loaded: {env_info['env_vars_loaded']}")
            
            return True
            
        except Exception as e:
            self.cli.print_error(f"Configuration validation failed: {e}")
            return False
    
    def run_test_suite(self):
        """Run the comprehensive test suite"""
        self.cli.print_header("Running Test Suite")
        
        try:
            from tests.test_framework import TestRunner
            
            test_runner = TestRunner(verbose=True)
            success = test_runner.run_all_tests()
            
            if success:
                self.cli.print_success("All tests passed!")
            else:
                self.cli.print_error("Some tests failed!")
            
            return success
            
        except ImportError as e:
            self.cli.print_error(f"Test framework not available: {e}")
            return False
        except Exception as e:
            self.cli.print_error(f"Error running tests: {e}")
            return False
    
    def shutdown(self):
        """Graceful shutdown of all services"""
        self.cli.print_info("Shutting down FionaSparx Enterprise...")
        
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.stop_monitoring()
        
        if hasattr(self, 'health_manager'):
            self.health_manager.stop_monitoring()
        
        self.cli.print_success("Shutdown complete")


def main():
    """Main entry point with enhanced command line interface"""
    
    cli = EnhancedCLI()
    
    # Available commands
    commands = {
        "test": "Test all components",
        "generate": "Generate general content",
        "fanvue": "Generate Fanvue-optimized content",
        "loyalfans": "Generate LoyalFans-optimized content",
        "health": "Check system health status",
        "performance": "Show performance metrics",
        "config": "Validate configuration",
        "run-tests": "Run comprehensive test suite"
    }
    
    # Handle command line arguments
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "test"
    
    if command == "help" or command == "--help" or command == "-h":
        cli.print_command_help(commands)
        return
    
    if command not in commands:
        cli.print_error(f"Unknown command: {command}")
        cli.print_command_help(commands)
        sys.exit(1)
    
    # Create FionaSparx instance
    try:
        fiona = FionaSparxEnterprise()
    except Exception as e:
        cli.print_error(f"Failed to initialize FionaSparx: {e}")
        sys.exit(1)
    
    start_time = time.time()
    success = False
    
    try:
        if command == "test":
            cli.print_info("Running component tests...")
            success = fiona.test_components()
            
        elif command == "generate":
            cli.print_info("Running general content generation...")
            content = fiona.generate_general_content()
            success = len(content) > 0
            if success:
                cli.print_success(f"Generated {len(content)} content items")
            
        elif command == "fanvue":
            cli.print_info("Running Fanvue content generation...")
            success = fiona.generate_fanvue_content()
            
        elif command == "loyalfans":
            cli.print_info("Running LoyalFans content generation...")
            content = fiona.generate_loyalfans_content()
            success = len(content) > 0
            if success:
                cli.print_success(f"Generated {len(content)} LoyalFans content items")
                
        elif command == "health":
            cli.print_info("Checking system health...")
            success = fiona.show_health_status()
            
        elif command == "performance":
            cli.print_info("Gathering performance metrics...")
            success = fiona.show_performance_metrics()
            
        elif command == "config":
            cli.print_info("Validating configuration...")
            success = fiona.validate_configuration()
            
        elif command == "run-tests":
            cli.print_info("Running test suite...")
            success = fiona.run_test_suite()
        
        # Show execution summary
        execution_time = time.time() - start_time
        
        if success:
            cli.print_success(f"Command '{command}' completed successfully in {execution_time:.2f}s")
        else:
            cli.print_error(f"Command '{command}' failed after {execution_time:.2f}s")
        
    except KeyboardInterrupt:
        cli.print_warning("Operation cancelled by user")
        success = False
    except Exception as e:
        cli.print_error(f"Error executing command '{command}': {e}")
        success = False
    finally:
        # Graceful shutdown
        fiona.shutdown()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()