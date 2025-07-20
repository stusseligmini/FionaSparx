# FionaSparx AI Content Creator

AI Content Optimization for Social Platforms - **Optimized for Fanvue and LoyalFans**

## 🚀 Overview

FionaSparx is an advanced AI-powered content creation system specifically optimized for Fanvue and LoyalFans platforms. It combines intelligent text generation with high-quality image creation to produce engaging, platform-specific content.

## ✨ Features

- **🎨 AI Image Generation**: High-quality image creation with style optimization
- **📝 Smart Text Generation**: Platform-specific captions and hashtags  
- **🎯 Platform Optimization**: Tailored content for Fanvue and LoyalFans
- **🔄 Fallback Mode**: Works even when AI models are unavailable
- **📊 Content Analytics**: JSON metadata for all generated content
- **🛡️ Error Handling**: Robust error handling and logging

## 🏗️ Architecture

```
FionaSparx/
├── main.py                    # Main entry point (NEW)
├── src/
│   ├── ai_model/
│   │   ├── text_generator.py     # Enhanced with platform optimization
│   │   ├── image_generator.py    # Advanced image generation
│   │   ├── smart_text_generator.py    # Import bridge
│   │   └── advanced_image_generator.py # Import bridge
│   ├── content/
│   ├── platforms/
│   ├── data/
│   └── utils/
├── output/                    # Generated content (NEW)
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/stusseligmini/FionaSparx.git
   cd FionaSparx
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the system**:
   ```bash
   python main.py test
   ```

### Basic Usage

```bash
# Test all components
python main.py test

# Generate general content
python main.py generate

# Generate Fanvue-optimized content
python main.py fanvue

# Generate LoyalFans-optimized content  
python main.py loyalfans
```

## 🎯 Platform-Specific Features

### Fanvue Optimization

- **Style**: Authentic, lifestyle-focused content
- **Tone**: Friendly, relatable, genuine
- **Hashtags**: Platform-specific tags like `#fanvue`, `#authentic`, `#realme`
- **Content Types**: Lifestyle, fashion, fitness with natural appeal

**Example Fanvue Content**:
```json
{
  "platform": "fanvue",
  "caption": "Just being my authentic self today 💫 What makes you feel most confident? #fanvue #lifestyle #authentic #realme #dailylife",
  "prompt": "A confident young woman in casual lifestyle setting, natural lighting, authentic smile"
}
```

### LoyalFans Optimization  

- **Style**: Sophisticated, artistic, premium
- **Tone**: Elegant, exclusive, refined
- **Hashtags**: Premium tags like `#loyalfans`, `#exclusive`, `#premium`, `#vip`
- **Content Types**: Artistic portraits, high fashion, luxury lifestyle

**Example LoyalFans Content**:
```json
{
  "platform": "loyalfans", 
  "caption": "Art is the highest form of expression ✨ Creating something unique today #loyalfans #artistic #creative #unique #sophisticated",
  "prompt": "Artistic portrait photography, creative lighting, professional model pose, high fashion"
}
```

## 🎨 Content Generation Features

### Smart Text Generation

The enhanced text generator includes:

- **Platform Detection**: Automatically optimizes content for target platform
- **Context Analysis**: Understands image context for relevant captions
- **Dynamic Hashtags**: Platform-specific hashtag optimization
- **Tone Adaptation**: Adjusts writing style per platform requirements

### Advanced Image Generation

- **Style Control**: Realistic, artistic, cinematic, fashion, lifestyle styles
- **Quality Settings**: High, medium, fast generation modes
- **Post-Processing**: Automatic image enhancement for quality
- **Fallback Mode**: Placeholder generation when AI models unavailable

## 📊 Output Structure

Generated content is saved in the `output/` directory:

```
output/
├── fanvue_content_1.png       # Generated images
├── fanvue_content_2.png
├── fanvue_content_3.png
├── fanvue_content.json        # Metadata and captions
├── loyalfans_content_1.png
├── loyalfans_content_2.png  
├── loyalfans_content_3.png
├── loyalfans_content.json
├── general_content_1.png
├── general_content_2.png
├── general_content_3.png
├── general_content.json
└── test_image.png             # Test output
```

## 🔧 Configuration

The system uses smart defaults but can be customized:

```python
config = {
    "ai_model": {
        "image_model": "runwayml/stable-diffusion-v1-5",
        "device": "auto",  # auto, cuda, cpu
        "image_size": [512, 512]
    },
    "platforms": {
        "fanvue": {
            "style": "lifestyle",
            "tone": "authentic", 
            "max_hashtags": 20
        },
        "loyalfans": {
            "style": "artistic",
            "tone": "engaging",
            "max_hashtags": 15
        }
    }
}
```

## 🛡️ Error Handling & Fallback

The system includes robust error handling:

- **Network Issues**: Works offline with cached models
- **Missing Models**: Generates placeholder content in fallback mode
- **GPU Unavailable**: Automatically switches to CPU mode
- **Generation Failures**: Provides fallback captions and images

## 📝 API Reference

### Main Classes

#### `FionaSparxSimple`
Main entry point class with platform-optimized content generation.

**Methods**:
- `test_components()`: Test all system components
- `generate_fanvue_content()`: Generate Fanvue-optimized content
- `generate_loyalfans_content()`: Generate LoyalFans-optimized content
- `generate_general_content()`: Generate general-purpose content

#### `SmartTextGenerator` (Enhanced)
Intelligent text generation with platform optimization.

**Key Features**:
- Platform-specific templates for Fanvue and LoyalFans
- Context-aware category detection
- Dynamic hashtag generation
- Tone and style adaptation

#### `AdvancedImageGenerator`
High-quality AI image generation with multiple styles and quality settings.

## 🧪 Testing

Run the comprehensive test suite:

```bash
python main.py test
```

This tests:
- Text generation functionality
- Image generation (or fallback mode)
- Platform-specific optimizations
- File I/O operations
- Error handling

## 🔄 Development Workflow

1. **Make changes** to source files in `src/`
2. **Test changes**: `python main.py test`
3. **Generate samples**: `python main.py fanvue` or `python main.py loyalfans`
4. **Review output** in `output/` directory
5. **Iterate** based on results

## 📋 Requirements

See `requirements.txt` for complete dependency list. Key requirements:

- `torch>=2.0.0` - PyTorch for AI models
- `diffusers>=0.21.0` - Hugging Face Diffusers
- `transformers>=4.21.0` - Transformer models
- `pillow>=9.0.0` - Image processing
- `schedule` - Task scheduling
- `python-dotenv` - Environment management

## 🎯 Platform Guidelines

### Fanvue Content Guidelines
- Focus on authenticity and relatability  
- Use natural, lifestyle-oriented imagery
- Encourage engagement with questions
- Maintain friendly, approachable tone
- Emphasize real moments and genuine expressions

### LoyalFans Content Guidelines
- Emphasize premium, exclusive content
- Use sophisticated, artistic imagery
- Highlight luxury and refinement
- Maintain elegant, upscale tone
- Focus on unique, high-quality experiences

## 🔮 Future Enhancements

- **Multi-language Support**: Content generation in multiple languages
- **Advanced Analytics**: Performance tracking and optimization
- **Batch Processing**: Generate multiple content sets
- **Custom Templates**: User-defined caption templates
- **API Integration**: Direct platform publishing
- **Content Scheduling**: Automated posting workflows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python main.py test`
5. Submit a pull request

## 📄 License

This project is part of the FionaSparx AI Content Creator system.

## 🆘 Support

For issues or questions:
1. Check the error logs in the console output
2. Verify all dependencies are installed correctly
3. Test with `python main.py test` to diagnose issues
4. Review the output in `output/` directory for results

---

**Made with ❤️ for content creators on Fanvue and LoyalFans**
