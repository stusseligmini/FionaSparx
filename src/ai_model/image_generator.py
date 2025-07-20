import torch
from PIL import Image
from diffusers import StableDiffusionPipeline

class ImageGenerator:
    def __init__(self, model_name="CompVis/stable-diffusion-v1-4", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_name, 
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        self.pipe.to(self.device)

    def generate_image(self, prompt):
        try:
            if self.device == "cuda":
                with torch.autocast("cuda"):
                    image = self.pipe(prompt, guidance_scale=7.5).images[0]
            else:
                image = self.pipe(prompt, guidance_scale=7.5).images[0]
            return image
        except Exception as e:
            print(f"Feil ved bilde-generering: {e}")
            return Image.new("RGB", (512, 512), color="gray")  # fallback-bilde
