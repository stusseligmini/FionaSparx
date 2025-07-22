"""
Content Quality Assessment Module with AI-based Evaluation

This module provides tools to analyze and evaluate content quality using AI,
ensuring high standards for generated content across platforms.

Key Features:
- AI-based content scoring
- Readability metrics
- Engagement prediction
- Platform-specific quality checks
- SEO optimization recommendations
- Custom quality rubrics

Author: FionaSparx AI Content Creator
Version: 1.0.0
"""

import re
import logging
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Typer av innhold som kan evalueres"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTI = "multi"  # Kombinert innhold


class QualityLevel(Enum):
    """Kvalitetsnivåer for evaluering"""
    EXCELLENT = 5
    GOOD = 4
    SATISFACTORY = 3
    NEEDS_IMPROVEMENT = 2
    POOR = 1


@dataclass
class QualityScore:
    """Struktur for kvalitetsvurdering"""
    overall: float  # Samlet score (0.0-5.0)
    readability: float  # Lesbarhet (0.0-5.0)
    engagement: float  # Engasjementspotensial (0.0-5.0)
    relevance: float  # Relevans for målgruppe (0.0-5.0)
    originality: float  # Originalitet (0.0-5.0)
    platform_fit: Dict[str, float]  # Plattformspesifikk egnethet (0.0-5.0)
    quality_level: QualityLevel  # Kvalitetsnivå basert på samlet score
    strengths: List[str]  # Identifiserte styrker
    improvement_areas: List[str]  # Forbedringsområder
    recommendations: List[str]  # Anbefalinger for forbedring


class ContentQualityAssessor:
    """
    AI-drevet innholdskvalitetsvurdering
    
    Evaluerer innholdskvalitet basert på flere faktorer og gir anbefalinger
    for forbedring.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.platform_metrics = {
            "fanvue": {
                "ideal_length": (150, 300),
                "hashtag_count": (10, 20),
                "readability_target": 70,  # Flesch Reading Ease
                "engagement_factors": {
                    "personal_touch": 0.35,
                    "call_to_action": 0.25,
                    "question_presence": 0.20,
                    "emoji_usage": 0.20,
                }
            },
            "loyalfans": {
                "ideal_length": (100, 250),
                "hashtag_count": (5, 15),
                "readability_target": 75,  # Flesch Reading Ease
                "engagement_factors": {
                    "authenticity": 0.40,
                    "call_to_action": 0.20,
                    "question_presence": 0.20,
                    "emoji_usage": 0.20,
                }
            },
            # Andre plattformer kan legges til her
        }
        
        logger.info("✅ Content Quality Assessor initialisert")
    
    def assess_content(self, content: str, content_type: ContentType = ContentType.TEXT, 
                      platforms: List[str] = None) -> QualityScore:
        """
        Vurder kvaliteten på innholdet og gi detaljert feedback
        
        Args:
            content: Innholdet som skal vurderes
            content_type: Type innhold (tekst, bilde, video, multi)
            platforms: Liste over plattformer å vurdere innhold for
            
        Returns:
            QualityScore: Detaljert kvalitetsvurdering
        """
        if not platforms:
            platforms = ["fanvue", "loyalfans"]
            
        logger.info(f"Vurderer {content_type.value}-innhold for plattformer: {', '.join(platforms)}")
        
        try:
            # Grunnleggende tekstanalyse
            text_metrics = self._analyze_text(content) if content_type == ContentType.TEXT else {}
            
            # Plattformspesifikk vurdering
            platform_scores = {}
            for platform in platforms:
                if platform in self.platform_metrics:
                    platform_scores[platform] = self._evaluate_platform_fit(
                        content, text_metrics, platform
                    )
            
            # Beregn samlet score
            readability = text_metrics.get("readability", 3.0)
            engagement = self._predict_engagement(content, text_metrics)
            relevance = self._assess_relevance(content, platforms)
            originality = self._assess_originality(content)
            
            # Vektede komponenter for samlet score
            components = [
                (readability, 0.25),
                (engagement, 0.30),
                (relevance, 0.25),
                (originality, 0.20)
            ]
            
            overall = sum(score * weight for score, weight in components)
            
            # Identifiser kvalitetsnivå
            quality_level = self._determine_quality_level(overall)
            
            # Identifiser styrker og forbedringsområder
            strengths, improvements = self._identify_strengths_and_improvements(
                content, text_metrics, platform_scores, overall
            )
            
            # Generer anbefalinger
            recommendations = self._generate_recommendations(
                content, text_metrics, platform_scores, improvements
            )
            
            score = QualityScore(
                overall=overall,
                readability=readability,
                engagement=engagement,
                relevance=relevance,
                originality=originality,
                platform_fit=platform_scores,
                quality_level=quality_level,
                strengths=strengths,
                improvement_areas=improvements,
                recommendations=recommendations
            )
            
            logger.info(f"Innholdsvurdering fullført: {quality_level.name} ({overall:.2f}/5.0)")
            return score
            
        except Exception as e:
            logger.error(f"Feil under innholdsvurdering: {e}")
            # Returner en standard score ved feil
            return QualityScore(
                overall=3.0,
                readability=3.0,
                engagement=3.0,
                relevance=3.0,
                originality=3.0,
                platform_fit={p: 3.0 for p in platforms},
                quality_level=QualityLevel.SATISFACTORY,
                strengths=["Kunne ikke analysere styrker på grunn av feil"],
                improvement_areas=["Kunne ikke analysere forbedringsområder på grunn av feil"],
                recommendations=["Prøv igjen eller kontakt support"]
            )
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyser tekst for grunnleggende metrikker"""
        # Fjern hashtags for noen beregninger
        clean_text = re.sub(r'#\w+', '', text)
        
        # Tell ord, setninger og tegn
        words = clean_text.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', clean_text)
        sentence_count = len([s for s in sentences if s.strip()])
        char_count = len(clean_text)
        
        # Beregn gjennomsnittlig ord- og setningslengde
        avg_word_length = char_count / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Enkel Flesch Reading Ease beregning (forenklet)
        # Original formel: 206.835 - 1.015 * (ord/setninger) - 84.6 * (stavelser/ord)
        # Her bruker vi en forenklet tilnærming med ordlengde i stedet for stavelser
        readability_score = max(0, min(100, 206.835 - 1.015 * avg_sentence_length - 8.4 * avg_word_length))
        
        # Tell hashtags
        hashtags = re.findall(r'#\w+', text)
        hashtag_count = len(hashtags)
        
        # Tell emojis (forenklet)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+"
        )
        emoji_count = len(re.findall(emoji_pattern, text))
        
        # Sjekk om teksten har spørsmål og call-to-action
        has_question = bool(re.search(r'\?', text))
        has_cta = bool(re.search(r'(klikk|følg|del|like|kommenter|sjekk ut|besøk|se mer)', text.lower()))
        
        # Konverter readability_score (0-100) til 5-poengs skala
        readability_5point = readability_score / 20
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "char_count": char_count,
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "readability_score": readability_score,
            "readability": readability_5point,
            "hashtag_count": hashtag_count,
            "hashtags": hashtags,
            "emoji_count": emoji_count,
            "has_question": has_question,
            "has_cta": has_cta
        }
    
    def _evaluate_platform_fit(self, content: str, metrics: Dict[str, Any], platform: str) -> float:
        """Vurder hvor godt innholdet passer for en spesifikk plattform"""
        if platform not in self.platform_metrics:
            return 3.0  # Middels score for ukjente plattformer
        
        platform_config = self.platform_metrics[platform]
        
        # Sjekk lengde mot ideelt område
        ideal_min, ideal_max = platform_config["ideal_length"]
        word_count = metrics.get("word_count", 0)
        
        if ideal_min <= word_count <= ideal_max:
            length_score = 5.0
        elif word_count < ideal_min:
            # For kort - gradvis reduksjon
            length_score = 5.0 - 2.0 * ((ideal_min - word_count) / ideal_min)
        else:
            # For langt - gradvis reduksjon
            length_score = 5.0 - 2.0 * ((word_count - ideal_max) / ideal_max)
        
        length_score = max(1.0, min(5.0, length_score))
        
        # Sjekk hashtag-antall
        ideal_hashtag_min, ideal_hashtag_max = platform_config["hashtag_count"]
        hashtag_count = metrics.get("hashtag_count", 0)
        
        if ideal_hashtag_min <= hashtag_count <= ideal_hashtag_max:
            hashtag_score = 5.0
        elif hashtag_count < ideal_hashtag_min:
            # For få - gradvis reduksjon
            hashtag_score = 3.0 + 2.0 * (hashtag_count / ideal_hashtag_min)
        else:
            # For mange - gradvis reduksjon
            excess = (hashtag_count - ideal_hashtag_max) / ideal_hashtag_max
            hashtag_score = 5.0 - min(2.0, 3.0 * excess)
        
        hashtag_score = max(1.0, min(5.0, hashtag_score))
        
        # Sjekk readability mot target
        readability_score = metrics.get("readability_score", 50)
        readability_target = platform_config["readability_target"]
        
        readability_diff = abs(readability_score - readability_target)
        if readability_diff <= 5:
            readability_score = 5.0
        elif readability_diff <= 10:
            readability_score = 4.0
        elif readability_diff <= 15:
            readability_score = 3.0
        elif readability_diff <= 25:
            readability_score = 2.0
        else:
            readability_score = 1.0
        
        # Sjekk engasjementsfaktorer
        engagement_factors = platform_config["engagement_factors"]
        engagement_score = 0
        
        # Personlig touch / autentisitet (forenklet)
        personal_factor = "personal_touch" if "personal_touch" in engagement_factors else "authenticity"
        personal_weight = engagement_factors.get(personal_factor, 0.35)
        
        personal_indicators = ["jeg", "min", "meg", "vi", "vår", "oss"]
        personal_count = sum(content.lower().count(word) for word in personal_indicators)
        personal_score = min(5.0, 2.0 + personal_count)
        
        # Call-to-action
        cta_weight = engagement_factors.get("call_to_action", 0.25)
        cta_score = 5.0 if metrics.get("has_cta", False) else 2.0
        
        # Spørsmål
        question_weight = engagement_factors.get("question_presence", 0.20)
        question_score = 5.0 if metrics.get("has_question", False) else 2.5
        
        # Emoji-bruk
        emoji_weight = engagement_factors.get("emoji_usage", 0.20)
        emoji_count = metrics.get("emoji_count", 0)
        emoji_score = min(5.0, 1.0 + emoji_count)
        
        # Samlet engasjementscore
        engagement_score = (
            personal_score * personal_weight +
            cta_score * cta_weight +
            question_score * question_weight +
            emoji_score * emoji_weight
        )
        
        # Vektet plattformscore
        platform_score = (
            length_score * 0.25 +
            hashtag_score * 0.25 +
            readability_score * 0.20 +
            engagement_score * 0.30
        )
        
        return min(5.0, max(1.0, platform_score))
    
    def _predict_engagement(self, content: str, metrics: Dict[str, Any]) -> float:
        """Predikter engasjementspotensial basert på innholdsanalyse"""
        engagement_score = 3.0  # Standard score
        
        # Justeringer basert på innholdskarakteristikk
        if metrics.get("has_question", False):
            engagement_score += 0.5  # Spørsmål øker engasjement
            
        if metrics.get("has_cta", False):
            engagement_score += 0.5  # Call-to-action øker engasjement
            
        # Emoji-bruk (optimal er 2-5 emojis)
        emoji_count = metrics.get("emoji_count", 0)
        if 2 <= emoji_count <= 5:
            engagement_score += 0.3
        elif emoji_count > 5:
            engagement_score -= 0.2  # For mange emojis kan virke unaturlig
            
        # Hashtagbruk (optimal er 5-15)
        hashtag_count = metrics.get("hashtag_count", 0)
        if 5 <= hashtag_count <= 15:
            engagement_score += 0.2
        elif hashtag_count > 15:
            engagement_score -= 0.3  # For mange hashtags kan virke spammy
            
        # Tekstlengde (optimal er 80-250 ord)
        word_count = metrics.get("word_count", 0)
        if 80 <= word_count <= 250:
            engagement_score += 0.3
        elif word_count > 400:
            engagement_score -= 0.4  # For lang tekst kan være uengasjerende
            
        # Lesbarhet
        readability = metrics.get("readability_score", 50)
        if 60 <= readability <= 80:
            engagement_score += 0.3  # Lettlest, men ikke for enkelt
            
        return min(5.0, max(1.0, engagement_score))
    
    def _assess_relevance(self, content: str, platforms: List[str]) -> float:
        """Vurder hvor relevant innholdet er for målgruppen"""
        # Dette er en forenklet implementasjon - en ekte AI-modell ville gjøre dette bedre
        relevance_score = 3.0  # Standard score
        
        # Sjekk for relevante nøkkelord basert på plattformer
        platform_keywords = {
            "fanvue": ["livsstil", "autentisk", "personlig", "ekte", "livet", "hverdag"],
            "loyalfans": ["eksklusiv", "unik", "premium", "innhold", "delt"]
        }
        
        # Tell forekomster av relevante nøkkelord
        keyword_count = 0
        for platform in platforms:
            if platform in platform_keywords:
                for keyword in platform_keywords[platform]:
                    if keyword.lower() in content.lower():
                        keyword_count += 1
        
        # Juster score basert på nøkkelord
        if keyword_count >= 3:
            relevance_score += 1.0
        elif keyword_count >= 1:
            relevance_score += 0.5
            
        # Begrens til gyldig område
        return min(5.0, max(1.0, relevance_score))
    
    def _assess_originality(self, content: str) -> float:
        """Vurder originalitet og unikhet av innholdet"""
        # Dette er en forenklet implementasjon - en ekte AI-modell ville gjøre dette bedre
        originality_score = 3.5  # Standard score - litt positiv bias
        
        # Sjekk for klisjéer og vanlige fraser
        cliches = [
            "lev livet til fulle", 
            "hver dag er en ny mulighet",
            "drømmer blir virkelighet",
            "dagen min",
            "blessed",
            "ute på eventyr",
            "beste tiden"
        ]
        
        cliche_count = sum(cliche.lower() in content.lower() for cliche in cliches)
        
        # Reduser score basert på klisjébruk
        if cliche_count >= 3:
            originality_score -= 1.5
        elif cliche_count >= 1:
            originality_score -= 0.5
            
        return min(5.0, max(1.0, originality_score))
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Bestem kvalitetsnivå basert på samlet score"""
        if overall_score >= 4.5:
            return QualityLevel.EXCELLENT
        elif overall_score >= 3.5:
            return QualityLevel.GOOD
        elif overall_score >= 2.5:
            return QualityLevel.SATISFACTORY
        elif overall_score >= 1.5:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    def _identify_strengths_and_improvements(self, content: str, 
                                          metrics: Dict[str, Any],
                                          platform_scores: Dict[str, float],
                                          overall: float) -> Tuple[List[str], List[str]]:
        """Identifiser styrker og forbedringsområder"""
        strengths = []
        improvements = []
        
        # Vurder lesbarhet
        readability = metrics.get("readability_score", 0)
        if readability >= 70:
            strengths.append("God lesbarhet som gjør innholdet lett å forstå")
        elif readability <= 40:
            improvements.append("Forbedre lesbarhet med kortere setninger og enklere ord")
        
        # Vurder lengde
        word_count = metrics.get("word_count", 0)
        if 100 <= word_count <= 300:
            strengths.append("Optimal tekstlengde for engasjement")
        elif word_count < 80:
            improvements.append("Legg til mer innhold for å øke dybden og verdi")
        elif word_count > 350:
            improvements.append("Vurder å forkorte teksten for bedre engasjement")
        
        # Vurder hashtags
        hashtag_count = metrics.get("hashtag_count", 0)
        if 5 <= hashtag_count <= 15:
            strengths.append(f"Effektiv bruk av {hashtag_count} hashtags")
        elif hashtag_count > 20:
            improvements.append("Reduser antall hashtags for å unngå å virke spammy")
        elif hashtag_count < 3:
            improvements.append("Legg til flere relevante hashtags for bedre synlighet")
        
        # Vurder engasjementselementer
        if metrics.get("has_question", False):
            strengths.append("Inkluderer spørsmål som oppfordrer til interaksjon")
        else:
            improvements.append("Legg til et spørsmål for å oppfordre til kommentarer")
            
        if metrics.get("has_cta", False):
            strengths.append("Inkluderer tydelig call-to-action")
        else:
            improvements.append("Legg til en call-to-action for å øke engasjement")
            
        # Vurder emoji-bruk
        emoji_count = metrics.get("emoji_count", 0)
        if 2 <= emoji_count <= 5:
            strengths.append("Balansert bruk av emojis")
        elif emoji_count > 8:
            improvements.append("Vurder å redusere antall emojis for et mer profesjonelt uttrykk")
        elif emoji_count == 0:
            improvements.append("Legg til noen relevante emojis for å gjøre teksten mer levende")
        
        # Plattformspesifikke vurderinger
        for platform, score in platform_scores.items():
            if score >= 4.0:
                strengths.append(f"Godt optimalisert for {platform}")
            elif score <= 2.5:
                improvements.append(f"Trenger optimalisering for {platform}")
        
        # Begrens til de mest relevante punktene
        strengths = strengths[:5]  # Maks 5 styrker
        improvements = improvements[:5]  # Maks 5 forbedringsområder
        
        return strengths, improvements
    
    def _generate_recommendations(self, content: str, 
                               metrics: Dict[str, Any],
                               platform_scores: Dict[str, float],
                               improvements: List[str]) -> List[str]:
        """Generer konkrete anbefalinger basert på forbedringsområder"""
        recommendations = []
        
        # Konverter forbedringsområder til konkrete anbefalinger
        for improvement in improvements:
            if "lesbarhet" in improvement.lower():
                recommendations.append("Del opp lange setninger og erstatt kompliserte ord med enklere alternativer")
                
            elif "lengde" in improvement.lower() and "forkorte" in improvement.lower():
                recommendations.append("Kutt ned til maksimalt 250-300 ord ved å fokusere på kjernebudskapet")
                
            elif "lengde" in improvement.lower() and "mer innhold" in improvement.lower():
                recommendations.append("Utvid innholdet til minst 100-150 ord for å gi mer verdi")
                
            elif "hashtags" in improvement.lower() and "reduser" in improvement.lower():
                recommendations.append("Behold 10-15 av de mest relevante hashtaggene og fjern resten")
                
            elif "hashtags" in improvement.lower() and "legg til" in improvement.lower():
                recommendations.append("Legg til 5-10 relevante hashtags som er populære innen din nisje")
                
            elif "spørsmål" in improvement.lower():
                recommendations.append("Avslutt teksten med et engasjerende spørsmål som oppfordrer til svar")
                
            elif "call-to-action" in improvement.lower():
                recommendations.append("Inkluder en tydelig oppfordring som 'Klikk på linken i bio' eller 'Del din mening i kommentarfeltet'")
                
            elif "emojis" in improvement.lower() and "redusere" in improvement.lower():
                recommendations.append("Bruk maks 3-5 emojis strategisk plassert i teksten")
                
            elif "emojis" in improvement.lower() and "legg til" in improvement.lower():
                recommendations.append("Inkluder 2-3 relevante emojis for å fremheve nøkkelpunkter")
                
            elif "optimalisering" in improvement.lower():
                platform = improvement.split()[-1]
                if platform == "fanvue":
                    recommendations.append("Legg til mer personlig innhold og autentiske elementer for Fanvue")
                elif platform == "loyalfans":
                    recommendations.append("Fremhev eksklusiviteten av innholdet for å bedre passe LoyalFans-formatet")
        
        # Legg til generelle anbefalinger hvis det er få spesifikke
        if len(recommendations) < 3:
            general_tips = [
                "Test ulike typer innhold for å se hva som får best respons",
                "Vær konsistent i tone og stil på tvers av innlegg",
                "Inkluder en personlig anekdote for å øke autentisiteten",
                "Bruk aktive verb for å gjøre teksten mer dynamisk",
                "Inkluder en relevant og aktuell referanse for å øke relevans"
            ]
            
            # Legg til generelle tips som ikke overlapper med eksisterende anbefalinger
            for tip in general_tips:
                if len(recommendations) >= 5:
                    break
                    
                if not any(tip.lower() in rec.lower() for rec in recommendations):
                    recommendations.append(tip)
        
        return recommendations
