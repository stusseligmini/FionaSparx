def generate_ideas(platform):
    if platform.lower() == "fanvue":
        return [
            "📸 AI content: Flørtete badekåpe-shoot",
            "🎥 AI content: Kveldsvideo med stearinlys og lav musikk"
        ]
    elif platform.lower() == "loyalfans":
        return [
            "📝 AI content: Spørsmål til følgerne – 'Hva vil du se i morgen?'",
            "🎧 AI content: Morgenrutine med sexy voiceover"
        ]
    else:
        return ["AI content: Standardinnlegg – prøv noe nytt i dag!"]
