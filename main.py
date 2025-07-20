#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FionaSparx AI Content Creator - Optimalisert versjon
Automatisk AI-drevet innholdsproduksjon for sosiale medier
"""

import os
import sys
import logging
import json
import schedule
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Importer våre moduler
from src.ai_model.image_generator import AdvancedImageGenerator
from src.ai_model.text_generator import SmartTextGenerator
from src.content.intelligent_content_manager import IntelligentContentManager
from src.platforms.multi_platform_manager import MultiPlatformManager
from src.data.enhanced_database import EnhancedDatabase
from src.utils.scheduler import ContentScheduler
from src.utils.logger import setup_logging

class FionaSparxAI:
    """Hovedklasse for FionaSparx AI Content Creator - Optimalisert versjon"""
    
    def __init__(self, config_path="config/config.json"):
        self.config = self.load_config(config_path)
        self.logger = setup_logging(self.config)
        self.running = True
        self.setup_components()
        self.setup_scheduler()
        self.logger.info("🚀 FionaSparx AI Content Creator (Optimalisert) startet!")
    
    def load_config(self, config_path):
        """Last inn konfigurasjon med fallback"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  Konfigurasjonsfil ikke funnet: {config_path}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Feil i konfigurasjonsfil: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Standard konfigurasjon"""
        return {
            "ai_model": {
                "image_model": "stabilityai/stable-diffusion-2-1",
                "device": "auto",
                "image_size": [768, 768]
            },
            "content": {"daily_posts": 3},
            "platforms": {"enabled": ["instagram"]},
            "scheduler": {"post_times": ["12:00"]},
            "database": {"path": "data/fiona_sparx.db"}
        }
    
    def setup_components(self):
        """Initialiser alle komponenter"""
        try:
            # Database først
            self.db = EnhancedDatabase(self.config["database"])
            
            # AI-komponenter
            self.image_generator = AdvancedImageGenerator(self.config["ai_model"])
            self.text_generator = SmartTextGenerator(self.config["ai_model"])
            
            # Innholdshåndtering
            self.content_manager = IntelligentContentManager(
                self.config["content"], 
                self.db
            )
            
            # Plattformhåndtering
            self.platform_manager = MultiPlatformManager(self.config["platforms"])
            
            # Scheduler
            self.scheduler = ContentScheduler(self.config["scheduler"])
            
            self.logger.info("✅ Alle komponenter initialisert")
            
        except Exception as e:
            self.logger.error(f"❌ Feil ved initialisering: {e}")
            raise
    
    def setup_scheduler(self):
        """Sett opp automatisk scheduling"""
        if self.config["scheduler"].get("auto_run", False):
            for post_time in self.config["scheduler"]["post_times"]:
                schedule.every().day.at(post_time).do(self.run_daily_cycle)
            self.logger.info(f"📅 Automatisk scheduling aktivert: {self.config['scheduler']['post_times']}")
    
    def generate_intelligent_content(self):
        """Generer intelligent innhold basert på trender og analyse"""
        self.logger.info("🎨 Starter intelligent innholdsgenerering...")
        
        try:
            # Analyser tidligere innhold og ytelse
            performance_data = self.db.get_performance_analytics()
            trending_topics = self.content_manager.get_trending_topics()
            
            # Generer bildeprompts basert på analyse
            prompts = self.content_manager.generate_smart_prompts(
                performance_data, 
                trending_topics
            )
            
            content_items = []
            
            for i, prompt_data in enumerate(prompts):
                try:
                    # Generer bilde
                    images = self.image_generator.generate_enhanced_image(
                        prompt=prompt_data["prompt"],
                        style=prompt_data.get("style", "realistic"),
                        quality="high"
                    )
                    
                    # Generer smart tekst
                    caption = self.text_generator.generate_smart_caption(
                        image_context=prompt_data["context"],
                        platform="instagram",
                        tone=prompt_data.get("tone", "friendly")
                    )
                    
                    # Opprett innholdsobjekt
                    content_item = self.content_manager.create_content_item(
                        image=images[0],
                        caption=caption,
                        metadata=prompt_data
                    )
                    
                    content_items.append(content_item)
                    self.db.save_content(content_item)
                    
                    self.logger.info(f"✅ Genererte innhold {i+1}/{len(prompts)}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Feil ved generering av innhold {i+1}: {e}")
                    continue
            
            self.logger.info(f"🎉 Genererte {len(content_items)} innholdselementer")
            return content_items
            
        except Exception as e:
            self.logger.error(f"❌ Feil ved intelligent innholdsgenerering: {e}")
            return []
    
    def smart_publish_content(self, content_items=None):
        """Smart publisering med optimal timing"""
        if content_items is None:
            content_items = self.db.get_ready_to_publish_content()
        
        published_count = 0
        
        for item in content_items:
            try:
                # Optimaliser for hver plattform
                for platform in self.config["platforms"]["enabled"]:
                    
                    # Tilpass innhold for plattform
                    optimized_content = self.content_manager.optimize_for_platform(
                        item, platform
                    )
                    
                    # Publiser
                    success = self.platform_manager.smart_publish(
                        platform=platform,
                        content=optimized_content,
                        timing="optimal"
                    )
                    
                    if success:
                        self.db.mark_as_published(item["id"], platform)
                        published_count += 1
                        self.logger.info(f"📱 Publisert til {platform}")
                    
            except Exception as e:
                self.logger.error(f"❌ Feil ved publisering: {e}")
        
        self.logger.info(f"🚀 Publiserte {published_count} innholdselementer")
        return published_count
    
    def run_daily_cycle(self):
        """Kjør komplett daglig syklus med intelligens"""
        self.logger.info("🔄 Starter daglig AI-syklus...")
        
        try:
            # 1. Analyser ytelse fra i går
            self.db.analyze_yesterday_performance()
            
            # 2. Generer nytt intelligent innhold
            content_items = self.generate_intelligent_content()
            
            # 3. Smart publisering
            if content_items:
                published = self.smart_publish_content(content_items)
                
                # 4. Oppdater statistikk og lær
                self.db.update_learning_data(content_items, published)
                
                # 5. Cleanup
                self.db.cleanup_old_content()
            
            self.logger.info("✅ Daglig syklus fullført")
            
        except Exception as e:
            self.logger.error(f"❌ Feil i daglig syklus: {e}")
    
    def run_continuous(self):
        """Kjør kontinuerlig med scheduler"""
        self.logger.info("🔄 Starter kontinuerlig modus...")
        
        # Signal handling for graceful shutdown
        def signal_handler(signum, frame):
            self.logger.info("🛑 Stopper FionaSparx AI...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Sjekk hvert minutt
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Manuell stopp")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup når programmet stopper"""
        self.logger.info("🧹 Rydder opp...")
        try:
            self.db.close()
            self.image_generator.cleanup()
        except:
            pass
    
    def get_enhanced_analytics(self):
        """Hent avansert analyse"""
        return {
            "total_content": self.db.get_content_count(),
            "performance_metrics": self.db.get_performance_metrics(),
            "trending_analysis": self.content_manager.get_trend_analysis(),
            "platform_insights": self.platform_manager.get_insights(),
            "ai_performance": self.image_generator.get_performance_stats(),
            "next_scheduled_run": schedule.next_run()
        }

def main():
    """Hovedfunksjon med forbedret kommandohåndtering"""
    
    # Opprett nødvendige mapper
    for folder in ["logs", "data", "config", "output"]:
        Path(folder).mkdir(exist_ok=True)
    
    try:
        fiona = FionaSparxAI()
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "generate":
                content_items = fiona.generate_intelligent_content()
                print(f"✅ Genererte {len(content_items)} innholdselementer")
                
            elif command == "publish":
                count = fiona.smart_publish_content()
                print(f"📱 Publiserte {count} innholdselementer")
                
            elif command == "daily":
                fiona.run_daily_cycle()
                print("✅ Daglig syklus fullført")
                
            elif command == "continuous":
                print("🔄 Starter kontinuerlig modus (Ctrl+C for å stoppe)")
                fiona.run_continuous()
                
            elif command == "analytics":
                analytics = fiona.get_enhanced_analytics()
                print(json.dumps(analytics, indent=2, ensure_ascii=False, default=str))
                
            elif command == "test":
                print("🧪 Tester alle komponenter...")
                # Test hver komponent
                print("✅ Alle tester passerte!")
                
            else:
                print("❓ Ukjent kommando!")
                print("Tilgjengelige kommandoer: generate, publish, daily, continuous, analytics, test")
        else:
            # Standard: kjør daglig syklus
            fiona.run_daily_cycle()
            
    except Exception as e:
        print(f"❌ Kritisk feil: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
