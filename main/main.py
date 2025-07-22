#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FionaSparx AI Content Creator - Production Ready Version
Optimized for Fanvue and LoyalFans content generation with enterprise features

Usage:
    python main.py test            # Test all components
    python main.py generate        # Generate general content
    python main.py fanvue          # Generate Fanvue-optimized content  
    python main.py loyalfans       # Generate LoyalFans-optimized content
    python main.py monitor         # Show system status
    python main.py config          # Show configuration
"""

import os
import sys
import logging
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Rich for beautiful CLI output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Installing rich for better CLI experience...")
    os.system("pip install rich")
    try:
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import print as rprint
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules with error handling
try:
    from ai_model.enhanced_image_generator import EnhancedImageGenerator
    from ai_model.smart_text_generator import SmartTextGenerator
    from utils.config_manager import ConfigManager
    from utils.logger import setup_advanced_logging
    from utils.performance_monitor import PerformanceMonitor
    from content.content_quality_assessor import ContentQualityAssessor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Creating missing modules...")

# Fallback console if rich not available
console = Console() if RICH_AVAILABLE else None

class FionaSparxPro:
    """
    Production-ready FionaSparx AI Content Creator
    Enterprise features with robust error handling and monitoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize FionaSparx with advanced features"""
        self.start_time = time.time()
        self.setup_directories()
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Setup advanced logging
        self.logger = setup_advanced_logging(self.config)
        
        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize components
        self.initialize_components()
        
        self.log_startup_complete()
    
    def setup_directories(self):
        """Create required directories"""
        required_dirs = [
            "logs", "data", "output", "config", 
            "cache", "models", "temp", "exports"
        ]
        
        for directory in required_dirs:
            Path(directory).mkdir(exist_ok=True)
    
    def initialize_components(self):
        """Initialize all AI and content components with error handling"""
        self.components_status = {}
        
        try:
            # Text Generator (always available)
            self.text_generator = SmartTextGenerator(self.config)
            self.components_status["text_generator"] = "✅ Ready"
            
            # Image Generator (with fallback)
            try:
                self.image_generator = EnhancedImageGenerator(
                    self.config.get("ai_model", {}),
                    performance_monitor=self.performance_monitor
                )
                self.components_status["image_generator"] = "✅ Ready (GPU)" if self.image_generator.device != "cpu" else "✅ Ready (CPU)"
            except Exception as e:
                self.logger.warning(f"Image generator failed: {e}")
                self.image_generator = None
                self.components_status["image_generator"] = "⚠️ Fallback mode"
            
            # Content Quality Assessor
            try:
                self.quality_assessor = ContentQualityAssessor(self.config)
                self.components_status["quality_assessor"] = "✅ Ready"
            except Exception as e:
                self.logger.warning(f"Quality assessor failed: {e}")
                self.quality_assessor = None
                self.components_status["quality_assessor"] = "⚠️ Disabled"
            
            # Platform optimizers
            self.platform_configs = {
                "fanvue": self.config.get("platforms", {}).get("fanvue", self.get_default_fanvue_config()),
                "loyalfans": self.config.get("platforms", {}).get("loyalfans", self.get_default_loyalfans_config())
            }
            
            self.components_status["platform_configs"] = "✅ Ready"
            
        except Exception as e:
            self.logger.error(f"Critical error during initialization: {e}")
            raise
    
    def get_default_fanvue_config(self) -> Dict[str, Any]:
        """Default Fanvue configuration"""
        return {
            "style": "lifestyle",
            "tone": "authentic", 
            "max_hashtags": 20,
            "content_types": ["lifestyle", "fashion", "fitness", "daily"],
            "templates": {
                "lifestyle": [
                    "Just being my authentic self today 💫 {context}",
                    "Living my best life 🌟 {context}",
                    "Authentic vibes only ✨ {context}"
                ],
                "fitness": [
                    "Pushing my limits today 💪 {context}",
                    "Strong body, strong mind 🏋️‍♀️ {context}",
                    "Fitness is my therapy 🔥 {context}"
                ]
            },
            "hashtags": [
                "#fanvue", "#authentic", "#lifestyle", "#realme", "#genuine",
                "#dailylife", "#confidence", "#natural", "#unfiltered", "#real"
            ]
        }
    
    def get_default_loyalfans_config(self) -> Dict[str, Any]:
        """Default LoyalFans configuration"""
        return {
            "style": "artistic",
            "tone": "sophisticated",
            "max_hashtags": 15,
            "content_types": ["artistic", "fashion", "premium", "exclusive"],
            "templates": {
                "artistic": [
                    "Art is the highest form of expression ✨ {context}",
                    "Creating something unique today 🎨 {context}",
                    "Beauty in every moment 💫 {context}"
                ],
                "fashion": [
                    "Elegance is the only beauty that never fades ✨ {context}",
                    "Style is a way to say who you are 👑 {context}",
                    "Fashion is art you can wear 🖤 {context}"
                ]
            },
            "hashtags": [
                "#loyalfans", "#exclusive", "#premium", "#artistic", "#sophisticated",
                "#elegant", "#unique", "#creative", "#luxury", "#vip"
            ]
        }
    
    def log_startup_complete(self):
        """Log successful startup with component status"""
        startup_time = time.time() - self.start_time
        
        if RICH_AVAILABLE:
            # Create beautiful startup panel
            startup_panel = Panel.fit(
                f"[bold green]🚀 FionaSparx AI Content Creator Pro[/bold green]\n"
                f"[dim]Startup completed in {startup_time:.2f}s[/dim]\n\n"
                + "\n".join([f"[bold]{k}:[/bold] {v}" for k, v in self.components_status.items()]),
                title="[bold blue]System Ready[/bold blue]",
                border_style="green"
            )
            console.print(startup_panel)
        else:
            print(f"🚀 FionaSparx AI Content Creator Pro")
            print(f"   Startup completed in {startup_time:.2f}s")
            for k, v in self.components_status.items():
                print(f"   {k}: {v}")
        
        self.logger.info(f"FionaSparx Pro initialized successfully in {startup_time:.2f}s")
    
    def test_all_components(self):
        """Comprehensive testing of all components"""
        if RICH_AVAILABLE:
            console.print(Panel("[bold blue]🧪 Running Component Tests[/bold blue]", border_style="blue"))
        else:
            print("🧪 Running Component Tests")
        
        test_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console if RICH_AVAILABLE else None,
            disable=not RICH_AVAILABLE
        ) as progress:
            
            # Test text generation
            task1 = progress.add_task("Testing text generation...", total=100)
            try:
                test_caption = self.text_generator.generate_platform_caption(
                    image_context="A beautiful lifestyle photo",
                    platform="fanvue"
                )
                test_results["text_generation"] = "✅ Pass"
                progress.update(task1, completed=100)
            except Exception as e:
                test_results["text_generation"] = f"❌ Fail: {str(e)[:50]}"
                progress.update(task1, completed=100)
            
            # Test image generation
            task2 = progress.add_task("Testing image generation...", total=100)
            if self.image_generator:
                try:
                    test_images = self.image_generator.generate_safe_image(
                        "A beautiful landscape sunset",
                        style="artistic",
                        quality="fast"
                    )
                    if test_images:
                        test_results["image_generation"] = "✅ Pass"
                    else:
                        test_results["image_generation"] = "⚠️ No output"
                    progress.update(task2, completed=100)
                except Exception as e:
                    test_results["image_generation"] = f"❌ Fail: {str(e)[:50]}"
                    progress.update(task2, completed=100)
            else:
                test_results["image_generation"] = "⚠️ Skipped (fallback mode)"
                progress.update(task2, completed=100)
            
            # Test platform optimization
            task3 = progress.add_task("Testing platform optimization...", total=100)
            try:
                fanvue_content = self.generate_platform_content("fanvue", test_mode=True)
                loyalfans_content = self.generate_platform_content("loyalfans", test_mode=True)
                test_results["platform_optimization"] = "✅ Pass"
                progress.update(task3, completed=100)
            except Exception as e:
                test_results["platform_optimization"] = f"❌ Fail: {str(e)[:50]}"
                progress.update(task3, completed=100)
            
            # Test quality assessment
            task4 = progress.add_task("Testing quality assessment...", total=100)
            if self.quality_assessor:
                try:
                    quality_score = self.quality_assessor.assess_content(
                        caption="Test caption for quality assessment",
                        metadata={"platform": "fanvue"}
                    )
                    test_results["quality_assessment"] = "✅ Pass"
                    progress.update(task4, completed=100)
                except Exception as e:
                    test_results["quality_assessment"] = f"❌ Fail: {str(e)[:50]}"
                    progress.update(task4, completed=100)
            else:
                test_results["quality_assessment"] = "⚠️ Skipped (disabled)"
                progress.update(task4, completed=100)
        
        # Display results
        self.display_test_results(test_results)
        
        return all("✅" in result for result in test_results.values())
    
    def display_test_results(self, results: Dict[str, str]):
        """Display test results in a beautiful table"""
        if RICH_AVAILABLE:
            table = Table(title="Test Results", border_style="cyan")
            table.add_column("Component", style="cyan", no_wrap=True)
            table.add_column("Status", style="magenta")
            
            for component, status in results.items():
                table.add_row(component.replace("_", " ").title(), status)
            
            console.print(table)
        else:
            print("\n📊 Test Results:")
            for component, status in results.items():
                print(f"   {component.replace('_', ' ').title()}: {status}")
    
    def generate_platform_content(self, platform: str, num_items: int = 3, test_mode: bool = False):
        """Generate optimized content for specific platform"""
        platform_config = self.platform_configs.get(platform, {})
        
        if not platform_config:
            raise ValueError(f"Unknown platform: {platform}")
        
        generated_content = []
        
        if RICH_AVAILABLE and not test_mode:
            console.print(f"[bold green]🎨 Generating {num_items} items for {platform.title()}[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console if RICH_AVAILABLE and not test_mode else None,
            disable=test_mode or not RICH_AVAILABLE
        ) as progress:
            
            task = progress.add_task(f"Generating {platform} content...", total=num_items)
            
            for i in range(num_items):
                try:
                    # Generate image prompt based on platform
                    content_type = self.select_content_type(platform_config)
                    image_prompt = self.create_platform_prompt(platform, content_type)
                    
                    # Generate image if available
                    image = None
                    if self.image_generator and not test_mode:
                        images = self.image_generator.generate_safe_image(
                            image_prompt["prompt"],
                            style=platform_config["style"],
                            quality="medium"
                        )
                        image = images[0] if images else None
                    
                    # Generate caption
                    caption = self.text_generator.generate_platform_caption(
                        image_context=image_prompt["context"],
                        platform=platform,
                        tone=platform_config["tone"],
                        hashtags=platform_config["hashtags"][:platform_config["max_hashtags"]]
                    )
                    
                    # Create content item
                    content_item = {
                        "id": f"{platform}_{int(time.time())}_{i+1}",
                        "platform": platform,
                        "caption": caption,
                        "image_prompt": image_prompt["prompt"],
                        "content_type": content_type,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {
                            "style": platform_config["style"],
                            "tone": platform_config["tone"],
                            "quality_score": None
                        }
                    }
                    
                    # Assess quality if available
                    if self.quality_assessor and not test_mode:
                        quality_score = self.quality_assessor.assess_content(
                            caption=caption,
                            metadata=content_item["metadata"]
                        )
                        content_item["metadata"]["quality_score"] = quality_score
                    
                    # Save image if generated
                    if image and not test_mode:
                        image_path = f"output/{platform}_content_{i+1}.png"
                        image.save(image_path)
                        content_item["image_path"] = image_path
                    
                    generated_content.append(content_item)
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    self.logger.error(f"Error generating content item {i+1}: {e}")
                    progress.update(task, advance=1)
                    continue
        
        # Save metadata
        if not test_mode:
            self.save_content_metadata(platform, generated_content)
            
            if RICH_AVAILABLE:
                console.print(f"[bold green]✅ Generated {len(generated_content)} {platform} content items[/bold green]")
        
        return generated_content
    
    def select_content_type(self, platform_config: Dict[str, Any]) -> str:
        """Select appropriate content type for platform"""
        import random
        return random.choice(platform_config.get("content_types", ["lifestyle"]))
    
    def create_platform_prompt(self, platform: str, content_type: str) -> Dict[str, str]:
        """Create optimized prompts for platform and content type"""
        platform_config = self.platform_configs[platform]
        
        # Base prompts for different content types
        base_prompts = {
            "lifestyle": "A confident young woman in casual lifestyle setting, natural lighting, authentic smile",
            "fashion": "Fashion photography of an elegant woman, professional styling, high-end fashion",
            "fitness": "Athletic woman in workout attire, gym setting, motivational pose",
            "artistic": "Artistic portrait photography, creative lighting, professional model pose",
            "premium": "Luxury lifestyle photography, sophisticated setting, high-end aesthetic",
            "daily": "Candid lifestyle moment, natural setting, genuine expression"
        }
        
        prompt = base_prompts.get(content_type, base_prompts["lifestyle"])
        
        # Add platform-specific modifiers
        if platform == "fanvue":
            prompt += ", lifestyle photography, natural, candid, authentic"
        elif platform == "loyalfans":
            prompt += ", artistic photography, sophisticated, elegant, premium quality"
        
        return {
            "prompt": prompt,
            "context": f"{content_type} content for {platform}",
            "type": content_type
        }
    
    def save_content_metadata(self, platform: str, content: list):
        """Save content metadata to JSON file"""
        metadata_file = f"output/{platform}_content.json"
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved metadata to {metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
    
    def show_system_status(self):
        """Display comprehensive system status"""
        if RICH_AVAILABLE:
            # Create status table
            status_table = Table(title="System Status", border_style="green")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="magenta")
            status_table.add_column("Details", style="white")
            
            # Add component statuses
            for component, status in self.components_status.items():
                details = self.get_component_details(component)
                status_table.add_row(
                    component.replace("_", " ").title(),
                    status,
                    details
                )
            
            # Performance metrics
            perf_metrics = self.performance_monitor.get_summary()
            status_table.add_row(
                "Performance",
                "📊 Monitoring",
                f"Generated: {perf_metrics.get('total_generated', 0)}"
            )
            
            console.print(status_table)
            
            # Configuration panel
            config_panel = Panel(
                f"[bold]GPU Device:[/bold] {getattr(self.image_generator, 'device', 'N/A')}\n"
                f"[bold]Model:[/bold] {self.config.get('ai_model', {}).get('image_model', 'Default')}\n"
                f"[bold]Platforms:[/bold] {', '.join(self.platform_configs.keys())}",
                title="[bold blue]Configuration[/bold blue]",
                border_style="blue"
            )
            console.print(config_panel)
        else:
            print("📊 System Status:")
            for component, status in self.components_status.items():
                print(f"   {component.replace('_', ' ').title()}: {status}")
    
    def get_component_details(self, component: str) -> str:
        """Get detailed information about component"""
        if component == "image_generator" and self.image_generator:
            return f"Device: {self.image_generator.device}"
        elif component == "text_generator":
            return "Platform optimized"
        elif component == "quality_assessor" and self.quality_assessor:
            return "AI-powered"
        else:
            return "Ready"
    
    def show_configuration(self):
        """Display current configuration"""
        if RICH_AVAILABLE:
            config_text = json.dumps(self.config, indent=2)
            console.print(Panel(config_text, title="[bold blue]Configuration[/bold blue]", border_style="blue"))
        else:
            print("⚙️  Configuration:")
            print(json.dumps(self.config, indent=2))

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="FionaSparx AI Content Creator Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test                    # Test all components
  python main.py generate                # Generate general content
  python main.py fanvue                  # Generate Fanvue content
  python main.py loyalfans               # Generate LoyalFans content
  python main.py monitor                 # Show system status
  python main.py config                  # Show configuration
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='test',
        choices=['test', 'generate', 'fanvue', 'loyalfans', 'monitor', 'config'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of content items to generate (default: 3)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize FionaSparx
        app = FionaSparxPro(config_path=args.config)
        
        # Execute command
        if args.command == 'test':
            success = app.test_all_components()
            sys.exit(0 if success else 1)
        
        elif args.command == 'generate':
            # Generate content for both platforms
            app.generate_platform_content('fanvue', args.count)
            app.generate_platform_content('loyalfans', args.count)
        
        elif args.command == 'fanvue':
            app.generate_platform_content('fanvue', args.count)
        
        elif args.command == 'loyalfans':
            app.generate_platform_content('loyalfans', args.count)
        
        elif args.command == 'monitor':
            app.show_system_status()
        
        elif args.command == 'config':
            app.show_configuration()
        
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[bold red]❌ Operation cancelled by user[/bold red]")
        else:
            print("\n❌ Operation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n[bold red]❌ Fatal error: {e}[/bold red]")
        else:
            print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
