import random
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SmartTextGenerator:
    """Intelligent tekstgenerator med kontekstforståelse"""
    
    def __init__(self, config):
        self.config = config
        self.setup_templates()
    
    def setup_templates(self):
        """Sett opp avanserte maler"""
        self.caption_templates = {
            "motivational": [
                "Hver dag er en ny mulighet til å skape noe vakkert ✨ {hashtags}",
                "Drømmer blir virkelighet når du tror på deg selv 💫 {hashtags}",
                "Først sa de det var umulig, så gjorde jeg det likevel 🚀 {hashtags}",
                "Styrke kommer ikke fra det du kan, men fra det du overvinner 💪 {hashtags}"
            ],
            "lifestyle": [
                "Livet er for kort til å ikke leve det fullt ut 🌟 {hashtags}",
                "Små øyeblikk, store minner 📸 {hashtags}",
                "Autentisitet er den nye trenden 💯 {hashtags}",
                "Hygge og gode vibber hele dagen ☀️ {hashtags}"
            ],
            "fashion": [
                "Stil er ikke hva du har på deg, men hvordan du bærer det 👗 {hashtags}",
                "Mote forsvinner, stil er evig ✨ {hashtags}",
                "Dagens outfit: selvtillit og et smil 😊 {hashtags}",
                "Klær er bare kostyme, personlighet er det som virkelig skinner 💫 {hashtags}"
            ],
            "fitness": [
                "Kroppen oppnår det sinnet tror på 💪 {hashtags}",
                "Progression over perfeksjon, alltid 🏃‍♀️ {hashtags}",
                "Sterkest versjon av meg selv, hver dag 🔥 {hashtags}",
                "Trening er mitt happy place 😊 {hashtags}"
            ],
            "travel": [
                "Nye steder, nye opplevelser, nye meg 🌍 {hashtags}",
                "Eventyr venter overalt, bare åpne øynene ✈️ {hashtags}",
                "Reise handler ikke om destinasjonen, men om reisen 🗺️ {hashtags}",
                "Samle øyeblikk, ikke ting 📱 {hashtags}"
            ]
        }
        
        self.hashtag_groups = {
            "lifestyle": ["#lifestyle", "#authenticity", "#dailylife", "#goodvibes", "#mindfulness"],
            "motivation": ["#motivation", "#inspiration", "#goals", "#mindset", "#growth"],
            "fashion": ["#fashion", "#style", "#ootd", "#fashionista", "#styleinspo"],
            "fitness": ["#fitness", "#workout", "#healthy", "#strongwoman", "#fitlife"],
            "travel": ["#travel", "#adventure", "#explore", "#wanderlust", "#travelgram"],
            "general": ["#ai", "#content", "#creator", "#authentic", "#life", "#inspiration"]
        }
    
    def generate_smart_caption(self, image_context, platform="instagram", tone="friendly"):
        """Generer smart beskrivelse basert på kontekst"""
        try:
            # Bestem kategori basert på kontekst
            category = self._detect_category(image_context)
            
            # Velg passende mal
            templates = self.caption_templates.get(category, self.caption_templates["lifestyle"])
            base_caption = random.choice(templates)
            
            # Generer hashtags
            hashtags = self._generate_smart_hashtags(category, platform)
            
            # Erstatt hashtag-placeholder
            caption = base_caption.format(hashtags=hashtags)
            
            # Tilpass for plattform
            caption = self._optimize_for_platform(caption, platform)
            
            logger.info(f"✅ Genererte smart caption for {category}")
            return caption
            
        except Exception as e:
            logger.error(f"❌ Feil ved tekstgenerering: {e}")
            return self._get_fallback_caption()
    
    def _detect_category(self, context):
        """Oppdag kategori fra kontekst"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["workout", "fitness", "gym", "athletic"]):
            return "fitness"
        elif any(word in context_lower for word in ["travel", "outdoor", "nature", "adventure"]):
            return "travel"
        elif any(word in context_lower for word in ["fashion", "elegant", "style", "outfit"]):
            return "fashion"
        elif any(word in context_lower for word in ["motivation", "confident", "strong", "success"]):
            return "motivational"
        else:
            return "lifestyle"
    
    def _generate_smart_hashtags(self, category, platform, max_hashtags=25):
        """Generer smarte hashtags"""
        hashtags = []
        
        # Legg til kategori-spesifikke hashtags
        if category in self.hashtag_groups:
            hashtags.extend(self.hashtag_groups[category][:8])
        
        # Legg til generelle hashtags
        hashtags.extend(self.hashtag_groups["general"][:5])
        
        # Legg til plattform-spesifikke hashtags
        if platform == "instagram":
            hashtags.extend(["#instagood", "#photooftheday", "#beautiful"])
        elif platform == "twitter":
            hashtags = hashtags[:5]  # Twitter har færre hashtags
        
        # Legg til dato-baserte hashtags
        today = datetime.now()
        day_hashtags = [
            f"#{today.strftime('%A').lower()}",
            f"#{today.strftime('%B').lower()}"
        ]
        hashtags.extend(day_hashtags)
        
        # Begrens antall
        hashtags = hashtags[:max_hashtags]
        
        return " ".join(hashtags)
    
    def _optimize_for_platform(self, caption, platform):
        """Optimaliser for spesifikk plattform"""
        if platform == "twitter":
            # Twitter har tegnbegrensning
            if len(caption) > 280:
                # Kort ned caption
                caption_parts = caption.split(" #")
                shortened = caption_parts[0][:200] + "..."
                hashtags = " #" + " #".join(caption_parts[1:3])  # Kun første 2 hashtags
                caption = shortened + hashtags
                
        elif platform == "linkedin":
            # LinkedIn er mer profesjonell
            caption = re.sub(r'[✨💫🚀💪🌟📸💯☀️👗😊💫🔥🏃‍♀️🌍✈️🗺️📱]', '', caption)
            caption = caption.replace("likevel", "allikevel")
            
        return caption
    
    def _get_fallback_caption(self):
        """Fallback caption hvis noe går galt"""
        fallbacks = [
            "Ny dag, nye muligheter ✨ #motivation #lifestyle #ai",
            "Autentisk innhold med AI-støtte 💫 #authentic #ai #content",
            "Kreativitet møter teknologi 🚀 #creativity #ai #innovation"
        ]
        return random.choice(fallbacks)
    
    def generate_story_text(self, context="daily"):
        """Generer tekst for stories"""
        story_templates = {
            "daily": [
                "Dagens vibe ✨",
                "Bare en vanlig dag 😊",
                "Små øyeblikk som betyr alt 💫"
            ],
            "behind_scenes": [
                "Bak kulissene 🎬",
                "Prosessen ✨",
                "Sånn lager jeg innhold 💻"
            ]
        }
        
        templates = story_templates.get(context, story_templates["daily"])
        return random.choice(templates)
