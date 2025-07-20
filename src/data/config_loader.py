import json
import os

DEFAULT_CONFIG = {
    "ai_model": {
        "image_model": "stable-diffusion",
        "text_model": "template"
    },
    "platforms": {
        "twitter": True,
        "instagram": False
    }
}

def load_config(path="Config/config.json"):
    if not os.path.exists(path):
        print("⚠️ config.json ikke funnet. Bruker standard.")
        return DEFAULT_CONFIG

    with open(path, "r") as f:
        try:
            config = json.load(f)
            if "ai_model" not in config or "image_model" not in config["ai_model"]:
                raise ValueError("config.json mangler 'ai_model.image_model'")
            return config
        except Exception as e:
            print(f"⚠️ Kunne ikke laste config: {e}. Bruker default.")
            return DEFAULT_CONFIG
