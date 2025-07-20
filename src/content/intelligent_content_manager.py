import random
import uuid
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class IntelligentContentManager:
    """Intelligent innholdshåndtering med læringsevne og trendanalyse"""
    
    def __init__(self, config, database):
        self.config = config
        self.db = database
        self.themes = config.get("themes", ["lifestyle", "motivation", "fashion"])
        self.setup_content_strategies()
        logger.info("🧠 Intelligent Content Manager initialisert")
    
    def setup_content_strategies(self):
        """Sett opp innholdsstrategier"""
        self.prompt_templates = {
            "lifestyle": [
                "professional lifestyle photo of a confident {subject}, {setting}, natural lighting, candid moment",
                "authentic lifestyle portrait, {subject} in {setting}, soft natural light, genuine expression",
                "casual lifestyle photography, {subject} enjoying {activity}, bright daylight, positive energy"
            ],
            "motivation": [
                "inspiring portrait of determined {subject}, {setting}, dramatic lighting, powerful composition",
                "motivational fitness photo, {subject} {activity}, gym setting, dynamic angle, strength focus",
                "success mindset photo, confident {subject}, {setting}, professional lighting, achievement theme"
            ],
            "fashion": [
                "high fashion portrait, elegant {subject}, {setting}, studio lighting, artistic composition",
                "street style photo, fashionable {subject}, urban {setting}, natural light, trendy outfit",
                "editorial fashion shot, sophisticated {subject}, {setting}, professional photography, style focus"
            ],
            "travel": [
                "travel photography, adventurous {subject}, beautiful {setting}, golden hour lighting, wanderlust",
                "destination photo, {subject} exploring {setting}, natural lighting, adventure spirit",
                "travel lifestyle shot, {subject} at {setting}, scenic background, journey documentation"
            ],
            "fitness": [
                "fitness motivation photo, athletic {subject}, gym {setting}, dynamic lighting, strength training",
                "workout lifestyle shot, {subject} {activity}, fitness environment, energetic composition",
                "health and wellness photo, fit {subject}, {setting}, natural light, active lifestyle"
            ]
        }
        
        self.subjects = ["woman", "young woman", "confident woman", "professional woman"]
        self.settings = {
            "lifestyle": ["modern apartment", "cozy cafe", "city street", "home office", "outdoor terrace"],
            "motivation": ["gym environment", "office space", "outdoor setting", "urban environment"],
            "fashion": ["studio setting", "urban background", "minimalist space", "natural environment"],
            "travel": ["scenic location", "beautiful destination", "natural landscape", "cultural site"],
            "fitness": ["modern gym", "outdoor fitness area", "home workout space", "athletic facility"]
        }
        
        self.activities = {
            "fitness": ["doing yoga", "strength training", "running", "working out", "stretching"],
            "lifestyle": ["working on laptop", "drinking coffee", "reading book", "relaxing"],
            "motivation": ["achieving goals", "leading meeting", "presenting", "succeeding"]
        }
    
    def get_trending_topics(self):
        """Analyser trender fra database og eksterne kilder"""
        try:
            # Hent data fra database om hva som har fungert bra
            recent_performance = self.db.get_recent_performance_data(days=30)
            
            # Analyser hvilke temaer som presterer best
            trending = self._analyze_performance_data(recent_performance)
            
            # Legg til sesongbaserte trender
            seasonal_trends = self._get_seasonal_trends()
            trending.update(seasonal_trends)
            
            logger.info(f"📈 Identifiserte {len(trending)} trending topics")
            return trending
            
        except Exception as e:
            logger.error(f"❌ Feil ved trendanalyse: {e}")
            return self._get_default_trends()
    
    def _analyze_performance_data(self, performance_data):
        """Analyser ytelsesdata for å finne trender"""
        trends = {}
        
        for item in performance_data:
            theme = item.get("theme", "lifestyle")
            engagement = item.get("engagement_rate", 0)
            
            if theme not in trends:
                trends[theme] = {"total_engagement": 0, "count": 0}
            
            trends[theme]["total_engagement"] += engagement
            trends[theme]["count"] += 1
        
        # Beregn gjennomsnittlig engagement per tema
        for theme in trends:
            if trends[theme]["count"] > 0:
                trends[theme]["avg_engagement"] = trends[theme]["total_engagement"] / trends[theme]["count"]
            else:
                trends[theme]["avg_engagement"] = 0
        
        return trends
    
    def _get_seasonal_trends(self):
        """Hent sesongbaserte trender"""
        month = datetime.now().month
        seasonal_trends = {}
        
        if month in [12, 1, 2]:  # Vinter
            seasonal_trends.update({
                "cozy": {"weight": 1.5, "keywords": ["warm", "cozy", "indoor"]},
                "new_year": {"weight": 1.3, "keywords": ["goals", "fresh start", "motivation"]}
            })
        elif month in [3, 4, 5]:  # Vår
            seasonal_trends.update({
                "renewal": {"weight": 1.4, "keywords": ["fresh", "growth", "new beginnings"]},
                "outdoor": {"weight": 1.2, "keywords": ["nature", "outdoor", "sunshine"]}
            })
        elif month in [6, 7, 8]:  # Sommer
            seasonal_trends.update({
                "summer_vibes": {"weight": 1.6, "keywords": ["summer", "vacation", "beach"]},
                "fitness": {"weight": 1.3, "keywords": ["fit", "healthy", "active"]}
            })
        else:  # Høst
            seasonal_trends.update({
                "autumn": {"weight": 1.3, "keywords": ["cozy", "warm colors", "comfort"]},
                "productivity": {"weight": 1.2, "keywords": ["focus", "goals", "achievement"]}
            })
        
        return seasonal_trends
    
    def _get_default_trends(self):
        """Fallback trender"""
        return {
            "lifestyle": {"weight": 1.0, "keywords": ["authentic", "daily life"]},
            "motivation": {"weight": 1.0, "keywords": ["inspiration", "goals"]},
            "fashion": {"weight": 1.0, "keywords": ["style", "elegant"]}
        }
    
    def generate_smart_prompts(self, performance_data, trending_topics):
        """Generer smarte prompts basert på analyse"""
        try:
            num_posts = self.config.get("daily_posts", 3)
            prompts = []
            
            # Velg temaer basert på trender og ytelse
            selected_themes = self._select_optimal_themes(trending_topics, num_posts)
            
            for i, theme in enumerate(selected_themes):
                prompt_data = self._create_theme_prompt(theme, trending_topics.get(theme, {}))
                prompts.append(prompt_data)
            
            logger.info(f"🎯 Genererte {len(prompts)} smarte prompts")
            return prompts
            
        except Exception as e:
            logger.error(f"❌ Feil ved prompt-generering: {e}")
            return self._get_fallback_prompts()
    
    def _select_optimal_themes(self, trending_topics, num_posts):
        """Velg optimale temaer basert på trender"""
        # Sorter temaer etter ytelse/trend-score
        sorted_themes = sorted(
            trending_topics.items(),
            key=lambda x: x[1].get("avg_engagement", 0) * x[1].get("weight", 1.0),
            reverse=True
        )
        
        # Velg topp-temaer, men sørg for variasjon
        selected = []
        theme_counts = {}
        
        for theme, _ in sorted_themes:
            if len(selected) >= num_posts:
                break
                
            # Unngå for mange av samme tema
            if theme_counts.get(theme, 0) < 2:
                selected.append(theme)
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Fyll opp med standard temaer hvis nødvendig
        while len(selected) < num_posts:
            for theme in self.themes:
                if theme not in selected:
                    selected.append(theme)
                    break
        
        return selected[:num_posts]
    
    def _create_theme_prompt(self, theme, trend_data):
        """Opprett prompt for spesifikt tema"""
        # Velg template
        templates = self.prompt_templates.get(theme, self.prompt_templates["lifestyle"])
        template = random.choice(templates)
        
        # Velg elementer
        subject = random.choice(self.subjects)
        setting = random.choice(self.settings.get(theme, self.settings["lifestyle"]))
        activity = random.choice(self.activities.get(theme, ["relaxing"]))
        
        # Bygg prompt
        prompt = template.format(
            subject=subject,
            setting=setting,
            activity=activity
        )
        
        # Legg til trend-keywords
        if "keywords" in trend_data:
            keywords = ", ".join(trend_data["keywords"][:2])
            prompt += f", {keywords}"
        
        return {
            "prompt": prompt,
            "theme": theme,
            "context": f"{theme} content with {subject} in {setting}",
            "style": self._get_style_for_theme(theme),
            "tone": self._get_tone_for_theme(theme),
            "metadata": {
                "subject": subject,
                "setting": setting,
                "activity": activity,
                "trend_score": trend_data.get("avg_engagement", 0)
            }
        }
    
    def _get_style_for_theme(self, theme):
        """Hent stil for tema"""
        style_mapping = {
            "lifestyle": "realistic",
            "motivation": "cinematic",
            "fashion": "artistic",
            "travel": "cinematic",
            "fitness": "realistic"
        }
        return style_mapping.get(theme, "realistic")
    
    def _get_tone_for_theme(self, theme):
        """Hent tone for tema"""
        tone_mapping = {
            "lifestyle": "friendly",
            "motivation": "inspiring",
            "fashion": "sophisticated",
            "travel": "adventurous",
            "fitness": "energetic"
        }
        return tone_mapping.get(theme, "friendly")
    
    def _get_fallback_prompts(self):
        """Fallback prompts hvis noe går galt"""
        return [
            {
                "prompt": "professional photo of a confident woman, natural lighting, high quality",
                "theme": "lifestyle",
                "context": "lifestyle content",
                "style": "realistic",
                "tone": "friendly"
            }
        ] * self.config.get("daily_posts", 3)
    
    def create_content_item(self, image, caption, metadata):
        """Opprett komplett innholdsobjekt"""
        return {
            "id": str(uuid.uuid4()),
            "type": "image",
            "image": image,
            "caption": caption,
            "metadata": metadata,
            "created_at": datetime.now(),
            "published": False,
            "platforms": {},
            "performance": {},
            "theme": metadata.get("theme", "lifestyle")
        }
    
    def optimize_for_platform(self, content_item, platform):
        """Optimaliser innhold for spesifikk plattform"""
        optimized = content_item.copy()
        
        if platform == "instagram":
            # Instagram-optimalisering
            optimized["aspect_ratio"] = "1:1"
            optimized["hashtag_strategy"] = "high_volume"
            
        elif platform == "twitter":
            # Twitter-optimalisering
            optimized["caption"] = self._shorten_for_twitter(content_item["caption"])
            optimized["hashtag_strategy"] = "minimal"
            
        elif platform == "tiktok":
            # TikTok-optimalisering
            optimized["aspect_ratio"] = "9:16"
            optimized["hashtag_strategy"] = "trending"
        
        return optimized
    
    def _shorten_for_twitter(self, caption):
        """Kort ned caption for Twitter"""
        if len(caption) <= 280:
            return caption
        
        # Behold hovedtekst, kort ned hashtags
        parts = caption.split("#")
        main_text = parts[0].strip()
        
        if len(main_text) > 200:
            main_text = main_text[:197] + "..."
        
        # Legg til maks 2 hashtags
        hashtags = ["#" + tag.strip() for tag in parts[1:3] if tag.strip()]
        
        return main_text + " " + " ".join(hashtags)
    
    def get_trend_analysis(self):
        """Hent trendanalyse for rapporter"""
        try:
            trending = self.get_trending_topics()
            
            analysis = {
                "top_performing_themes": [],
                "seasonal_trends": self._get_seasonal_trends(),
                "content_recommendations": []
            }
            
            # Sorter etter ytelse
            sorted_trends = sorted(
                trending.items(),
                key=lambda x: x[1].get("avg_engagement", 0),
                reverse=True
            )
            
            analysis["top_performing_themes"] = [
                {"theme": theme, "engagement": data.get("avg_engagement", 0)}
                for theme, data in sorted_trends[:5]
            ]
            
            # Generer anbefalinger
            analysis["content_recommendations"] = self._generate_recommendations(sorted_trends)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Feil ved trendanalyse: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, sorted_trends):
        """Generer innholdsanbefalinger"""
        recommendations = []
        
        if sorted_trends:
            top_theme = sorted_trends[0][0]
            recommendations.append(f"Fokuser mer på {top_theme}-innhold - det presterer best")
            
            if len(sorted_trends) > 1:
                second_theme = sorted_trends[1][0]
                recommendations.append(f"Kombinér {top_theme} og {second_theme} for optimal variasjon")
        
        # Sesongbaserte anbefalinger
        seasonal = self._get_seasonal_trends()
        if seasonal:
            top_seasonal = max(seasonal.items(), key=lambda x: x[1]["weight"])
            recommendations.append(f"Utnytt sesongtrenden: {top_seasonal[0]}")
        
        return recommendations
