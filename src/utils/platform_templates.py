"""
Platform Optimizations Module with Enhanced Templates

This module provides specialized templates and optimization strategies
for various content platforms, with particular focus on Fanvue and LoyalFans.

Key Features:
- Platform-specific content templates
- Custom optimization strategies
- Engagement-focused formatting
- Platform-specific best practices
- Template selection based on content type
- Performance tracking

Author: FionaSparx AI Content Creator
Version: 1.0.0
"""

import re
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PlatformTemplateManager:
    """
    Håndtering av optimaliserte maler for ulike plattformer
    
    Spesielt fokusert på Fanvue og LoyalFans for innholdsoptimalisering.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.setup_templates()
        logger.info("✅ Platform Template Manager initialisert")
    
    def setup_templates(self):
        """Oppretter optimaliserte maler for ulike plattformer"""
        # Fanvue-optimaliserte maler
        self.fanvue_templates = {
            "lifestyle": [
                {
                    "title": "Autentisk hverdagsinnblikk",
                    "structure": (
                        "🌟 {personlig_introduksjon}\n\n"
                        "{hovedinnhold_med_detaljer}\n\n"
                        "💭 {spørsmål_til_følgere}\n\n"
                        "{call_to_action}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["✨", "💫", "🌟", "💭", "☀️", "❤️", "🥰", "😊"],
                    "cta_options": [
                        "Har du opplevd noe lignende? Del i kommentarene!",
                        "Følg med for flere innblikk i hverdagen min",
                        "Sjekk link i bio for mer eksklusive innblikk",
                        "Vil du se mer? La meg vite i kommentarene!"
                    ]
                },
                {
                    "title": "Personlig refleksjon",
                    "structure": (
                        "✨ {tanker_om_tema}\n\n"
                        "Dette er hvordan jeg ser på det:\n"
                        "{punkter_med_erfaring}\n\n"
                        "{personlig_konklusjon}\n\n"
                        "💭 {relatert_spørsmål}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["✨", "💭", "🧠", "💫", "🤔", "💖", "🌈"],
                    "cta_options": [
                        "Hva tenker du? Del dine tanker!",
                        "Følg for flere personlige refleksjoner",
                        "Vil du dele dine erfaringer med dette?",
                        "Sjekk link i bio for en dypere samtale om dette"
                    ]
                },
                {
                    "title": "Bak kulissene",
                    "structure": (
                        "👀 {bak_kulissene_introduksjon}\n\n"
                        "Det de fleste ikke ser:\n"
                        "{punktliste_med_innsikt}\n\n"
                        "{personlig_betraktning}\n\n"
                        "💬 {spørsmål_eller_cta}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["👀", "🎬", "🔍", "💫", "✨", "🤫", "😊", "💖"],
                    "cta_options": [
                        "Vil du se mer av hva som skjer bak kulissene?",
                        "Følg for flere eksklusive innblikk",
                        "Sjekk ut link i bio for mer innhold som dette",
                        "Kommenter om du vil se mer av denne typen innhold!"
                    ]
                }
            ],
            "casual": [
                {
                    "title": "Hverdagsøyeblikk",
                    "structure": (
                        "✌️ {uformell_introduksjon}\n\n"
                        "{hverdagsfortelling}\n\n"
                        "🤣 {humoristisk_vri_eller_tanke}\n\n"
                        "{spørsmål_til_følgere}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["✌️", "🤣", "😂", "👌", "🙌", "💯", "🤪"],
                    "cta_options": [
                        "Relaterbart? Drop en emoji i kommentarene!",
                        "Del din lignende historie i kommentarene",
                        "Tagg en venn som ville likt dette",
                        "Trykk følg for flere hverdagshistorier!"
                    ]
                },
                {
                    "title": "Ærlig øyeblikk",
                    "structure": (
                        "💯 Helt ærlig? {ærlig_introduksjon}\n\n"
                        "{hovedinnhold_med_sårbarhet}\n\n"
                        "{personlig_lærdom}\n\n"
                        "🤔 {reflekterende_spørsmål}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["💯", "🤔", "❤️", "🙏", "✨", "💪", "🌱"],
                    "cta_options": [
                        "Har du opplevd noe lignende?",
                        "Del dine ærlige tanker i kommentarene",
                        "Sjekk ut profilen min for mer ærlige øyeblikk",
                        "Er det flere som har det slik? La meg vite!"
                    ]
                }
            ],
            "announcement": [
                {
                    "title": "Spennende nyhet",
                    "structure": (
                        "🎉 STOR NYHET! {nyhet_introduksjon}\n\n"
                        "{detaljert_beskrivelse}\n\n"
                        "{fordeler_eller_muligheter}\n\n"
                        "⏰ {timing_og_tilgjengelighet}\n\n"
                        "{call_to_action}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["🎉", "✨", "🚀", "💫", "⏰", "🔥", "💯", "🤩"],
                    "cta_options": [
                        "Ikke gå glipp av dette! Trykk på linken i bio",
                        "Del med en venn som ville verdsatt dette",
                        "Kommenter '🔥' hvis du er like spent som meg!",
                        "Følg med for flere detaljer som kommer snart"
                    ]
                }
            ]
        }
        
        # LoyalFans-optimaliserte maler
        self.loyalfans_templates = {
            "exclusive": [
                {
                    "title": "Eksklusivt innhold",
                    "structure": (
                        "🔒 {eksklusiv_introduksjon}\n\n"
                        "{hovedinnhold_med_verdi}\n\n"
                        "{personlig_melding_til_fans}\n\n"
                        "👀 {hint_om_mer_eksklusivt}\n\n"
                        "{call_to_action}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["🔒", "✨", "👀", "💎", "🥂", "🌹", "💖", "🌟"],
                    "cta_options": [
                        "Se mer eksklusivt innhold i link i bio",
                        "Vil du se mer? La meg vite i kommentarene!",
                        "Del hva du ønsker å se mer av",
                        "Gå ikke glipp av neste eksklusive oppdatering"
                    ]
                },
                {
                    "title": "Premium opplevelse",
                    "structure": (
                        "💎 {premium_introduksjon}\n\n"
                        "Kun for mine loyale fans:\n"
                        "{eksklusiv_innholdsbeskrivelse}\n\n"
                        "{personlig_melding}\n\n"
                        "👑 {fordeler_og_verdi}\n\n"
                        "{call_to_action}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["💎", "👑", "✨", "🥂", "🌹", "💫", "🔥", "🌟"],
                    "cta_options": [
                        "Få tilgang til mer premium innhold (link i bio)",
                        "Takk for at du støtter meg! Hva vil du se mer av?",
                        "Del dine tanker om dette eksklusive innholdet",
                        "Ikke gå glipp av neste premium oppdatering"
                    ]
                }
            ],
            "teaser": [
                {
                    "title": "Innholdsteaser",
                    "structure": (
                        "👀 {mystisk_introduksjon}\n\n"
                        "{hint_om_kommende_innhold}\n\n"
                        "{verdi_og_løfte}\n\n"
                        "🔥 {forventningsskapende_avslutning}\n\n"
                        "{call_to_action}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["👀", "🔥", "💫", "🤫", "✨", "🚀", "💯", "🎬"],
                    "cta_options": [
                        "Følg linken i bio for å ikke gå glipp av dette",
                        "Kommenter '👀' hvis du vil se mer",
                        "Del med en venn som ville elsket dette",
                        "Sett på varsler for å se når dette slippes"
                    ]
                }
            ],
            "gratitude": [
                {
                    "title": "Takknemlighet til fans",
                    "structure": (
                        "❤️ {takknemlighetsintro}\n\n"
                        "{spesifikk_verdsettelse}\n\n"
                        "{personlig_melding_fra_hjertet}\n\n"
                        "🙏 {løfte_om_fremtidig_innhold}\n\n"
                        "{spørsmål_til_fans}\n\n"
                        "{hashtags}"
                    ),
                    "emoji_suggestion": ["❤️", "🙏", "💖", "✨", "🥰", "💯", "🌟", "🤗"],
                    "cta_options": [
                        "Fortell meg hva du ønsker å se mer av",
                        "Del et øyeblikk hvor mitt innhold gjorde en forskjell for deg",
                        "Takk for at du er her - se mer i linken i bio",
                        "Du er grunnen til at jeg fortsetter - hva kan jeg gjøre mer av?"
                    ]
                }
            ]
        }
        
        # Generiske maler som kan tilpasses for ulike plattformer
        self.generic_templates = {
            "question": [
                {
                    "title": "Engasjerende spørsmål",
                    "structure": (
                        "🤔 {introduksjonsspørsmål}\n\n"
                        "{hovedinnhold}\n\n"
                        "💭 {spørsmål_til_følgere}\n\n"
                        "{hashtags}"
                    ),
                    "elements": [
                        "introduksjonsspørsmål",
                        "hovedinnhold", 
                        "spørsmål_til_følgere",
                        "hashtags"
                    ]
                }
            ]
        }
    
    def get_template(self, platform, template_type):
        """Hent en mal for en spesifikk plattform og type"""
        if platform == "fanvue":
            templates = self.fanvue_templates.get(template_type, [])
        elif platform == "loyalfans":
            templates = self.loyalfans_templates.get(template_type, [])
        else:
            templates = self.generic_templates.get(template_type, [])
        
        if templates:
            # Returner første mal som standard
            return templates[0]
        else:
            # Fallback til generisk mal
            return {
                "title": "Generisk mal",
                "structure": "{hovedinnhold}\n\n{hashtags}",
                "elements": ["hovedinnhold", "hashtags"]
            }
    
    def apply_template(self, template, content_data):
        """Anvend mal på innholdsdata"""
        try:
            structure = template.get("structure", "{hovedinnhold}")
            return structure.format(**content_data)
        except KeyError as e:
            logger.warning(f"Manglende nøkkel i innholdsdata: {e}")
            # Fallback til enkel formatering
            return f"{content_data.get('hovedinnhold', 'Innhold')}\n\n{content_data.get('hashtags', '')}"
