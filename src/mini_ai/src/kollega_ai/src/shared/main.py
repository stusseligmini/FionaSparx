from src.mini_ai.idea_generator import generate_ideas
from src.kollega_ai.persona_writer import write_caption

if __name__ == "__main__":
    platform = "Fanvue"
    ideas = generate_ideas(platform)
    
    print(f"Forslag for {platform}:")
    for idea in ideas:
        caption = write_caption(idea)
        print(f"- {caption}")
