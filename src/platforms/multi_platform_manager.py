import logging
import random
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class MultiPlatformManager:
    """Avansert plattformhåndtering med smart publisering"""
    
    def __init__(self, config):
        self.config = config
        self.platforms = {}
        self.publish_history = []
        self.setup_platforms()
        logger.info("📱 Multi-Platform Manager initialisert")
    
    def setup_platforms(self):
        """Sett opp plattformtilkoblinger"""
        enabled_platforms = self.config.get("enabled", [])
        
        platform_configs = {
            "instagram": {
                "max_hashtags": 30,
                "optimal_times": ["09:00", "15:00", "21:00"],
                "image_specs": {"width": 1080, "height": 1080},
                "engagement_weight": 1.0
            },
            "twitter": {
                "max_hashtags": 5,
                "optimal_times": ["08:00", "12:00", "17:00", "20:00"],
                "image_specs": {"width": 1200, "height": 675},
                "engagement_weight": 0.8
            },
            "tiktok": {
                "max_hashtags": 10,
                "optimal_times": ["12:00", "18:00", "21:00"],
                "image_specs": {"width": 1080, "height": 1920},
                "engagement_weight": 1.2
            },
            "linkedin": {
                "max_hashtags": 5,
                "optimal_times": ["09:00", "14:00", "17:00"],
                "image_specs": {"width": 1200, "height": 627},
                "engagement_weight": 0.7
            },
            "facebook": {
                "max_hashtags": 15,
                "optimal_times": ["09:00", "13:00", "19:00"],
                "image_specs": {"width": 1200, "height": 630},
                "engagement_weight": 0.6
            }
        }
        
        for platform in enabled_platforms:
            if platform in platform_configs:
                self.platforms[platform] = {
                    "connected": True,
                    "api_client": None,  # Her ville du koblet til ekte API
                    "config": platform_configs[platform],
                    "last_publish": None,
                    "daily_count": 0,
                    "performance_history": []
                }
                logger.info(f"✅ {platform.title()} konfigurert")
    
    def smart_publish(self, platform, content, timing="optimal"):
        """Smart publisering med optimal timing"""
        try:
            if platform not in self.platforms:
                logger.error(f"❌ Plattform ikke støttet: {platform}")
                return False
            
            platform_config = self.platforms[platform]["config"]
            
            # Sjekk om det er optimal tid å publisere
            if timing == "optimal" and not self._is_optimal_time(platform):
                logger.info(f"⏰ Venter på optimal tid for {platform}")
                return False
            
            # Sjekk daglig grense
            if self._check_daily_limit(platform):
                logger.warning(f"📊 Daglig grense nådd for {platform}")
                return False
            
            # Tilpass innhold for plattform
            adapted_content = self._adapt_content_for_platform(content, platform)
            
            # Simuler publisering (her ville du brukt ekte API)
            success = self._simulate_publish(platform, adapted_content)
            
            if success:
                self._record_publish(platform, adapted_content)
                logger.info(f"✅ Publisert til {platform}")
                
                # Simuler engagement tracking
                self._simulate_engagement_tracking(platform, content["id"])
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Feil ved publisering til {platform}: {e}")
            return False
    
    def _is_optimal_time(self, platform):
        """Sjekk om det er optimal tid for publisering"""
        current_time = datetime.now().strftime("%H:%M")
        optimal_times = self.platforms[platform]["config"]["optimal_times"]
        
        # Sjekk om nåværende tid er innenfor 30 minutter av optimal tid
        for optimal_time in optimal_times:
            optimal_hour, optimal_minute = map(int, optimal_time.split(":"))
            current_hour, current_minute = map(int, current_time.split(":"))
            
            optimal_minutes = optimal_hour * 60 + optimal_minute
            current_minutes = current_hour * 60 + current_minute
            
            if abs(current_minutes - optimal_minutes) <= 30:
                return True
        
        return False
    
    def _check_daily_limit(self, platform):
        """Sjekk om daglig grense er nådd"""
        daily_limits = {
            "instagram": 5,
            "twitter": 10,
            "tiktok": 3,
            "linkedin": 2,
            "facebook": 4
        }
        
        current_count = self.platforms[platform]["daily_count"]
        limit = daily_limits.get(platform, 3)
        
        return current_count >= limit
    
    def _adapt_content_for_platform(self, content, platform):
        """Tilpass innhold for spesifikk plattform"""
        adapted = content.copy()
        platform_config = self.platforms[platform]["config"]
        
        # Tilpass bildeformat
        if "image_specs" in platform_config:
            adapted["image_specs"] = platform_config["image_specs"]
        
        # Tilpass hashtags
        if "caption" in content:
            adapted["caption"] = self._adapt_hashtags(
                content["caption"], 
                platform_config["max_hashtags"]
            )
        
        # Plattform-spesifikke tilpasninger
        if platform == "linkedin":
            # Mer profesjonell tone for LinkedIn
            adapted["caption"] = self._make_professional(adapted.get("caption", ""))
        elif platform == "tiktok":
            # Mer trendy språk for TikTok
            adapted["caption"] = self._make_trendy(adapted.get("caption", ""))
        elif platform == "twitter":
            # Kort format for Twitter
            adapted["caption"] = self._shorten_for_twitter(adapted.get("caption", ""))
        
        return adapted
    
    def _adapt_hashtags(self, caption, max_hashtags):
        """Tilpass antall hashtags"""
        if not caption:
            return ""
            
        parts = caption.split("#")
        if len(parts) <= max_hashtags + 1:  # +1 fordi første del ikke er hashtag
            return caption
        
        # Behold hovedtekst og begrens hashtags
        main_text = parts[0]
        hashtags = ["#" + tag for tag in parts[1:max_hashtags] if tag.strip()]
        
        return main_text + " " + " ".join(hashtags)
    
    def _make_professional(self, caption):
        """Gjør caption mer profesjonell for LinkedIn"""
        # Fjern emojis og gjør språket mer formelt
        import re
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 "]+", flags=re.UNICODE)
        
        professional = emoji_pattern.sub('', caption)
        
        # Erstatt uformelle uttrykk
        replacements = {
            "følger drømmene mine": "forfølger mine profesjonelle mål",
            "lever livet": "utvikler meg både personlig og profesjonelt",
            "nye eventyr": "nye muligheter og utfordringer"
        }
        
        for old, new in replacements.items():
            professional = professional.replace(old, new)
        
        return professional.strip()
    
    def _make_trendy(self, caption):
        """Gjør caption mer trendy for TikTok"""
        # Legg til trendy elementer
        trendy_additions = ["slay", "periodt", "no cap", "fr fr"]
        
        if random.random() < 0.3:  # 30% sjanse for å legge til trendy element
            addition = random.choice(trendy_additions)
            caption += f" {addition} ✨"
        
        return caption
    
    def _shorten_for_twitter(self, caption):
        """Kort ned for Twitter"""
        if len(caption) <= 280:
            return caption
        
        # Smart forkortelse
        parts = caption.split("#")
        main_text = parts[0].strip()
        
        if len(main_text) > 200:
            main_text = main_text[:197] + "..."
        
        # Behold viktigste hashtags
        important_hashtags = ["#motivation", "#lifestyle", "#inspiration"]
        hashtags = []
        
        for tag in parts[1:]:
            tag_with_hash = "#" + tag.strip()
            if tag_with_hash.lower() in [h.lower() for h in important_hashtags]:
                hashtags.append(tag_with_hash)
            if len(hashtags) >= 2:
                break
        
        result = main_text + " " + " ".join(hashtags)
        return result[:280]
    
    def _simulate_publish(self, platform, content):
        """Simuler publisering (erstatt med ekte API-kall)"""
        # Her ville du brukt ekte API for hver plattform
        # For nå simulerer vi bare
        
        simulation_delay = random.uniform(1, 3)  # Simuler nettverksforsinkelse
        time.sleep(simulation_delay)
        
        # Simuler 95% suksessrate
        success_rate = 0.95
        return random.random() < success_rate
    
    def _record_publish(self, platform, content):
        """Registrer publisering"""
        now = datetime.now()
        
        # Oppdater plattformstatistikk
        self.platforms[platform]["last_publish"] = now
        self.platforms[platform]["daily_count"] += 1
        
        # Legg til i historikk
        publish_record = {
            "platform": platform,
            "content_id": content.get("id"),
            "timestamp": now,
            "content_type": content.get("type", "image"),
            "theme": content.get("theme", "unknown")
        }
        
        self.publish_history.append(publish_record)
        
        # Begrens historikk til siste 1000 oppføringer
        if len(self.publish_history) > 1000:
            self.publish_history = self.publish_history[-1000:]
    
    def _simulate_engagement_tracking(self, platform, content_id):
        """Simuler engagement tracking"""
        # Her ville du integrert med ekte analytics API
        
        base_engagement = self.platforms[platform]["config"]["engagement_weight"]
        
        # Simuler tilfeldige engagement-tall
        likes = random.randint(int(50 * base_engagement), int(500 * base_engagement))
        comments = random.randint(int(5 * base_engagement), int(50 * base_engagement))
        shares = random.randint(int(2 * base_engagement), int(20 * base_engagement))
        
        engagement_data = {
            "content_id": content_id,
            "platform": platform,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "timestamp": datetime.now()
        }
        
        self.platforms[platform]["performance_history"].append(engagement_data)
        logger.info(f"📊 Simulert engagement for {platform}: {likes} likes, {comments} kommentarer")
    
    def get_insights(self):
        """Hent plattforminnsikter"""
        insights = {
            "platforms": {},
            "total_published_today": 0,
            "best_performing_platform": None,
            "recommendations": []
        }
        
        best_performance = 0
        
        for platform, data in self.platforms.items():
            platform_insights = {
                "daily_count": data["daily_count"],
                "last_publish": data["last_publish"],
                "avg_engagement": self._calculate_avg_engagement(platform),
                "optimal_next_time": self._get_next_optimal_time(platform)
            }
            
            insights["platforms"][platform] = platform_insights
            insights["total_published_today"] += data["daily_count"]
            
            # Finn best presterende plattform
            avg_eng = platform_insights["avg_engagement"]
            if avg_eng > best_performance:
                best_performance = avg_eng
                insights["best_performing_platform"] = platform
        
        # Generer anbefalinger
        insights["recommendations"] = self._generate_platform_recommendations()
        
        return insights
    
    def _calculate_avg_engagement(self, platform):
        """Beregn gjennomsnittlig engagement"""
        history = self.platforms[platform]["performance_history"]
        
        if not history:
            return 0
        
        total_engagement = sum(
            item["likes"] + item["comments"] + item["shares"] 
            for item in history[-10:]  # Siste 10 poster
        )
        
        return total_engagement / min(len(history), 10)
    
    def _get_next_optimal_time(self, platform):
        """Finn neste optimale publiseringstid"""
        optimal_times = self.platforms[platform]["config"]["optimal_times"]
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Finn neste tid i dag eller i morgen
        for time_str in optimal_times:
            if time_str > current_time:
                next_time = now.replace(
                    hour=int(time_str.split(":")[0]),
                    minute=int(time_str.split(":")[1]),
                    second=0,
                    microsecond=0
                )
                return next_time
        
        # Hvis ingen tid igjen i dag, ta første tid i morgen
        tomorrow = now + timedelta(days=1)
        first_time = optimal_times[0]
        next_time = tomorrow.replace(
            hour=int(first_time.split(":")[0]),
            minute=int(first_time.split(":")[1]),
            second=0,
            microsecond=0
        )
        
        return next_time
    
    def _generate_platform_recommendations(self):
        """Generer plattformanbefalinger"""
        recommendations = []
        
        for platform, data in self.platforms.items():
            daily_count = data["daily_count"]
            
            if daily_count == 0:
                recommendations.append(f"Vurder å publisere på {platform} i dag")
            elif daily_count < 2:
                recommendations.append(f"Du kan publisere mer på {platform}")
        
        # Finn plattform med best engagement
        best_platform = None
        best_engagement = 0
        
        for platform in self.platforms:
            avg_eng = self._calculate_avg_engagement(platform)
            if avg_eng > best_engagement:
                best_engagement = avg_eng
                best_platform = platform
        
        if best_platform:
            recommendations.append(f"Fokuser mer på {best_platform} - det presterer best")
        
        return recommendations
    
    def reset_daily_counts(self):
        """Nullstill daglige tellere (kjør ved midnatt)"""
        for platform in self.platforms:
            self.platforms[platform]["daily_count"] = 0
        logger.info("🔄 Nullstilte daglige tellere")
