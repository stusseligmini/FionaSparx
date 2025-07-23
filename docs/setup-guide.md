# FionaSparx AI Content Creator - Setup Guide

## Overview

FionaSparx is a comprehensive AI-powered social media automation system designed specifically for content creators on platforms like FanVue and LoyalFans. This guide will walk you through the complete setup process.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- N8N (optional, for workflow automation)
- API keys for your desired platforms

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/stusseligmini/FionaSparx.git
   cd FionaSparx
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp config/api-keys.example.env config/.env
   ```

5. **Edit configuration file**
   ```bash
   nano config/.env  # Add your API keys and settings
   ```

6. **Test the system**
   ```bash
   python main.py test
   ```

## 🔧 Configuration

### Environment Variables

Copy `config/api-keys.example.env` to `config/.env` and configure the following:

#### Core Settings
```env
ENVIRONMENT=development
DATABASE_PATH=data/fionasparx.db
DB_ENCRYPTION_KEY=your_secure_encryption_key
```

#### AI Model Configuration
```env
# OpenAI (recommended for text generation)
TEXT_MODEL_API_KEY=your_openai_api_key

# Stability AI (recommended for image generation)
IMAGE_MODEL_API_KEY=your_stability_ai_key

# Hugging Face (backup models)
HUGGINGFACE_API_KEY=your_huggingface_token
```

#### Platform API Keys

##### Instagram Business API
1. Create a Facebook App at [developers.facebook.com](https://developers.facebook.com)
2. Add Instagram Basic Display and Instagram Graph API
3. Get your Business Account ID and Access Token

```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id
INSTAGRAM_APP_ID=your_facebook_app_id
INSTAGRAM_APP_SECRET=your_facebook_app_secret
```

##### Twitter API v2
1. Apply for Twitter Developer Account at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app and generate API keys
3. Enable OAuth 2.0 and get Bearer Token

```env
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

##### FanVue & LoyalFans
Contact the platforms directly for API access:

```env
FANVUE_API_KEY=your_fanvue_api_key
FANVUE_USER_ID=your_fanvue_user_id
LOYALFANS_API_KEY=your_loyalfans_api_key
LOYALFANS_USER_ID=your_loyalfans_user_id
```

## 🤖 AI Model Setup

### Text Generation

#### Option 1: OpenAI (Recommended)
```env
TEXT_MODEL=gpt-4
TEXT_MODEL_API_KEY=sk-your-openai-key
```

#### Option 2: Local Models
```env
USE_LOCAL_MODELS=true
TEXT_MODEL=microsoft/DialoGPT-large
```

### Image Generation

#### Option 1: Stability AI (Recommended)
```env
IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
IMAGE_MODEL_API_KEY=your-stability-key
```

#### Option 2: Hugging Face
```env
IMAGE_MODEL=runwayml/stable-diffusion-v1-5
HUGGINGFACE_API_KEY=your-hf-token
```

## 📊 Database Setup

The system uses SQLite by default. On first run, it will automatically create all required tables.

### Manual Database Initialization
```bash
python -c "
from src.database.models import DatabaseManager
db = DatabaseManager()
print('Database initialized successfully')
"
```

### Database Migration
```bash
python -c "
from src.database.models import DatabaseManager, migrate_database
db = DatabaseManager()
migrate_database(db, target_version=2)
"
```

## 🔄 N8N Workflow Setup

### Install N8N
```bash
npm install -g n8n
```

### Start N8N
```bash
n8n start
```

### Import Workflows
1. Open N8N at `http://localhost:5678`
2. Go to "Workflows" → "Import from File"
3. Import each workflow file from the `workflows/` directory:
   - `daily-posting.json`
   - `engagement-analysis.json`
   - `content-generation.json`

### Configure Workflow Credentials
1. In N8N, go to "Credentials"
2. Add credentials for each platform:
   - **Instagram Credentials**: Add Instagram Graph API credentials
   - **Twitter Credentials**: Add Twitter OAuth credentials
   - **PostgreSQL**: Configure database connection
   - **HTTP Authentication**: Add API keys

### Workflow Configuration
```env
N8N_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key
N8N_DAILY_POSTING_WORKFLOW_ID=workflow_id_from_n8n
N8N_ENGAGEMENT_ANALYSIS_WORKFLOW_ID=workflow_id_from_n8n
N8N_CONTENT_GENERATION_WORKFLOW_ID=workflow_id_from_n8n
```

## 🛡️ Security Setup

### JWT Authentication
```env
JWT_SECRET_KEY=your_very_secure_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Database Encryption
```env
DB_ENCRYPTION_KEY=your_database_encryption_key
```

### API Rate Limiting
```env
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=3600
```

### Content Moderation
```env
CONTENT_MODERATION_ENABLED=true
ADULT_CONTENT_FILTER=strict
```

## 📅 Scheduling Setup

### Automatic Posting
```env
AUTO_POSTING_ENABLED=true
POSTING_HOURS=08:00,12:00,17:00,20:00
TIMEZONE=Europe/Oslo
```

### Cross-Platform Promotion
```env
CROSS_PROMOTION_ENABLED=true
CROSS_PROMOTION_DELAY_MINUTES=30
```

## 🧪 Testing Your Setup

### Run Component Tests
```bash
python main.py test
```

### Test Individual Components
```bash
# Test text generation
python -c "
from src.ai_model.text_generator import SmartTextGenerator
gen = SmartTextGenerator()
result = gen.generate_caption('lifestyle', 'fanvue')
print(result)
"

# Test image generation
python -c "
from src.ai_model.image_generator import AdvancedImageGenerator
gen = AdvancedImageGenerator()
result = gen.generate_images('A confident woman in casual lifestyle setting', count=1)
print(result)
"
```

### Test Platform APIs
```bash
# Test Instagram API
python -c "
from src.api.instagram import InstagramAPI
from config.settings import get_config
config = get_config()
creds = config.get_platform_credentials('instagram')
if creds:
    api = InstagramAPI(creds['access_token'], creds['business_account_id'])
    insights = api.get_account_insights()
    print(insights)
else:
    print('Instagram credentials not configured')
"
```

## 🚀 Running the System

### Development Mode
```bash
# Start the system in development mode
python main.py

# Generate content for specific platform
python main.py fanvue
python main.py loyalfans

# Generate general content
python main.py generate
```

### Production Mode
```bash
# Set environment to production
export ENVIRONMENT=production

# Run with logging
python main.py 2>&1 | tee logs/fionasparx.log
```

### Background Service
```bash
# Using systemd (Linux)
sudo cp scripts/fionasparx.service /etc/systemd/system/
sudo systemctl enable fionasparx
sudo systemctl start fionasparx

# Using PM2 (Cross-platform)
npm install -g pm2
pm2 start ecosystem.config.js
```

## 📈 Monitoring & Analytics

### Application Logs
```bash
# View logs
tail -f logs/fionasparx.log

# View N8N workflow logs
tail -f ~/.n8n/logs/n8n.log
```

### Database Analytics
```bash
python -c "
from src.database.models import DatabaseManager
db = DatabaseManager()
stats = db.get_database_stats()
print(stats)
"
```

### System Health Check
```bash
python -c "
from config.settings import get_config
config = get_config()
summary = config.get_configuration_summary()
print(summary)
"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure Python path includes src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 2. API Authentication Errors
```bash
# Verify API keys are set
python -c "
from config.settings import get_config
config = get_config()
platforms = config.get_enabled_platforms()
print(f'Enabled platforms: {platforms}')
"
```

#### 3. Database Errors
```bash
# Reset database
rm data/fionasparx.db
python -c "
from src.database.models import DatabaseManager
db = DatabaseManager()
print('Database recreated')
"
```

#### 4. N8N Workflow Errors
- Check N8N logs at `~/.n8n/logs/`
- Verify credentials are properly configured
- Test individual nodes in the workflow

### Performance Optimization

#### 1. Enable Caching
```env
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600
ENABLE_CACHING=true
```

#### 2. Optimize AI Models
```env
# Use local models for faster generation
USE_LOCAL_MODELS=true

# Reduce concurrent generations if memory limited
MAX_CONCURRENT_GENERATIONS=2
```

#### 3. Database Optimization
```bash
# Run cleanup regularly
python -c "
from src.database.models import DatabaseManager
db = DatabaseManager()
db.cleanup_old_data(days_to_keep=30)
"
```

## 📞 Support

### Getting Help
1. Check the [documentation](docs/)
2. Review the [API documentation](docs/api-documentation.md)
3. Check the logs for error messages
4. Test individual components

### Reporting Issues
When reporting issues, include:
- Error messages from logs
- Configuration summary (without API keys)
- Steps to reproduce
- System information (OS, Python version)

### Development
For development and customization:
1. Fork the repository
2. Create a feature branch
3. Run tests: `python main.py test`
4. Submit a pull request

## 🎯 Next Steps

After setup:
1. **Content Generation**: Test generating content for your platforms
2. **Analytics**: Monitor performance and optimize based on insights
3. **Automation**: Set up N8N workflows for hands-off operation
4. **Customization**: Adapt templates and AI prompts to your style
5. **Scaling**: Add more platforms and advanced features

## 📋 Checklist

- [ ] Python environment set up
- [ ] Dependencies installed
- [ ] Configuration file created and populated
- [ ] Database initialized
- [ ] API credentials tested
- [ ] N8N workflows imported (optional)
- [ ] System tests passed
- [ ] First content generated successfully
- [ ] Monitoring set up
- [ ] Backup strategy in place

Congratulations! Your FionaSparx AI Content Creator system is now ready to generate amazing content automatically! 🎉