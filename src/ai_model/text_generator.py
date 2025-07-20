import openai
from config_loader import get_config

class TextGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.api_key = get_config("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY mangler i .env")

        openai.api_key = self.api_key

    def generate_text(self, title):
        try:
            system_prompt = (
                "Du er en kreativ matblogger som skriver trendy og sunne oppskrifter "
                "for travle hverdager. Du gir korte, men inspirerende tekster."
            )
            user_prompt = f"Gi meg en rask og sunn hverdagsoppskrift basert på tittelen: '{title}'"

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7,
            )

            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"⚠️ Feil under tekstgenerering: {e}")
            return f"Hverdagsrett: {title} – en enkel og sunn oppskrift."
