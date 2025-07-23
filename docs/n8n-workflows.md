# N8N Workflows Documentation

## Overview

This document provides detailed information about the N8N workflows included with FionaSparx AI Content Creator. These workflows enable complete automation of content creation, posting, and analytics.

## 📋 Workflow Overview

### 1. Daily Posting Workflow (`daily-posting.json`)
**Purpose**: Automated daily content posting with quality checks and cross-platform promotion

**Trigger**: Cron schedule (8:00, 12:00, 17:00, 20:00 daily)

**Features**:
- Smart content generation based on time of day
- Quality assessment before posting
- Platform-specific routing (FanVue/LoyalFans)
- Cross-platform promotion to Instagram/Twitter
- Analytics logging
- Error handling with regeneration

### 2. Engagement Analysis Workflow (`engagement-analysis.json`)
**Purpose**: Hourly analysis of engagement patterns and AI learning

**Trigger**: Hourly (30 minutes past each hour)

**Features**:
- Multi-platform data fetching
- Engagement pattern analysis
- AI model updates with new insights
- Subscriber behavior analysis
- Automated response generation
- Performance insights storage

### 3. Content Generation Workflow (`content-generation.json`)
**Purpose**: Advanced content generation API with quality control

**Trigger**: Webhook/Manual trigger

**Features**:
- AI-powered content strategy
- Parallel image and caption generation
- Comprehensive quality assessment
- Content compilation and metadata
- API response handling
- Error recovery and fallbacks

## 🔧 Installation Instructions

### Step 1: Install N8N
```bash
# Install N8N globally
npm install -g n8n

# Or using Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Step 2: Start N8N
```bash
# Start N8N
n8n start

# Access at http://localhost:5678
```

### Step 3: Import Workflows

1. **Open N8N Interface**
   - Navigate to `http://localhost:5678`
   - Create an account or log in

2. **Import Each Workflow**
   - Click "Add Workflow" → "Import from File"
   - Select workflow JSON files from `workflows/` directory
   - Import all three workflows

3. **Activate Workflows**
   - Open each imported workflow
   - Click the "Active" toggle to enable

### Step 4: Configure Credentials

#### Required Credentials

1. **HTTP Authentication (for FionaSparx API)**
   ```
   Name: FionaSparx API
   Type: HTTP Header Auth
   Header: Authorization
   Value: Bearer your_api_key
   ```

2. **Instagram Graph API**
   ```
   Name: Instagram API
   Type: Generic Credential
   Access Token: your_instagram_access_token
   Business Account ID: your_business_account_id
   ```

3. **Twitter OAuth**
   ```
   Name: Twitter API
   Type: Twitter OAuth API
   API Key: your_twitter_api_key
   API Secret: your_twitter_api_secret
   Access Token: your_twitter_access_token
   Access Token Secret: your_twitter_access_token_secret
   ```

4. **PostgreSQL/Database**
   ```
   Name: FionaSparx Database
   Type: Postgres
   Host: localhost
   Database: fionasparx
   User: your_db_user
   Password: your_db_password
   ```

5. **FanVue API** (if available)
   ```
   Name: FanVue API
   Type: HTTP Header Auth
   Header: Authorization
   Value: Bearer your_fanvue_api_key
   ```

6. **LoyalFans API** (if available)
   ```
   Name: LoyalFans API
   Type: HTTP Header Auth
   Header: Authorization
   Value: Bearer your_loyalfans_api_key
   ```

## 📊 Workflow Details

### Daily Posting Workflow

#### Nodes Overview
1. **Schedule Trigger**: Cron schedule for posting times
2. **Content Generation**: Calls FionaSparx API to generate content
3. **Quality Check**: Validates content quality (threshold: 3.5/5.0)
4. **Platform Router**: Routes content to appropriate platform
5. **Post to FanVue**: Posts content to FanVue platform
6. **Post to LoyalFans**: Posts content to LoyalFans platform
7. **Cross-platform Promotion**: Creates promotional posts on Instagram/Twitter
8. **Analytics Logger**: Stores performance data
9. **Content Regeneration**: Regenerates content if quality check fails
10. **Error Handler**: Handles and logs errors

#### Configuration

**Schedule Configuration**:
```json
{
  "rule": {
    "hour": [8, 12, 17, 20],
    "minute": [0],
    "timezone": "Europe/Oslo"
  }
}
```

**Content Generation Parameters**:
```javascript
// Morning (8:00)
{
  "contentType": "morning_motivation",
  "platform": "fanvue"
}

// Afternoon (12:00)
{
  "contentType": "lifestyle", 
  "platform": "loyalfans"
}

// Evening (17:00)
{
  "contentType": "afternoon_update",
  "platform": "fanvue"
}

// Night (20:00)
{
  "contentType": "evening_thoughts",
  "platform": "loyalfans"
}
```

#### Error Handling
- Quality check failures trigger content regeneration
- Network errors are logged and admin notifications sent
- Failed posts are queued for retry
- Fallback content used if all generation attempts fail

### Engagement Analysis Workflow

#### Nodes Overview
1. **Hourly Analysis Trigger**: Runs every hour at 30 minutes past
2. **Fetch Platform Data**: Retrieves data from all connected platforms
3. **Analyze Engagement Patterns**: AI-powered pattern analysis
4. **Update Learning Model**: Updates AI models with new insights
5. **Store Analytics Data**: Saves analysis results to database
6. **Subscriber Interaction Analysis**: Analyzes subscriber behavior
7. **AI Response Generation**: Generates personalized responses
8. **Store Subscriber Insights**: Saves subscriber analysis

#### Platform Data Collection
```javascript
// Instagram data
{
  "fields": "id,caption,media_type,timestamp,like_count,comments_count,insights.metric(impressions,reach,engagement)",
  "since": "1 hour ago"
}

// Twitter data  
{
  "tweet.fields": "created_at,public_metrics,context_annotations",
  "start_time": "1 hour ago"
}

// FanVue/LoyalFans data
{
  "hours": 1,
  "types": "likes,comments,tips,views"
}
```

#### Learning Insights Generated
- Optimal posting times per platform
- Best performing content types
- Engagement rate trends
- Subscriber preferences
- Cross-platform performance comparison
- Churn risk analysis

### Content Generation Workflow

#### Nodes Overview
1. **Webhook Trigger**: Receives API requests for content generation
2. **Parse Request**: Validates and processes request parameters
3. **AI Content Strategy**: Determines optimal content approach
4. **Generate Images**: Creates AI-generated images
5. **Generate Captions**: Creates platform-optimized captions
6. **Quality Assessment**: Comprehensive quality evaluation
7. **Compile Final Content**: Assembles complete content packages
8. **Store Content**: Saves content to database
9. **Response Handler**: Formats API response
10. **Webhook Response**: Returns content to requester

#### API Request Format
```json
{
  "platform": "fanvue|loyalfans|instagram|twitter",
  "content_type": "lifestyle|fashion|fitness|motivation",
  "count": 3,
  "style": "authentic|elegant|casual",
  "mood": "positive|energetic|relaxed",
  "include_image": true,
  "quality_threshold": 3.5
}
```

#### API Response Format
```json
{
  "success": true,
  "request_id": "req_123456789",
  "generated_at": "2024-01-15T10:30:00Z",
  "platform": "fanvue",
  "content_type": "lifestyle",
  "summary": {
    "total_generated": 3,
    "quality_passed": 3,
    "average_quality": 4.2,
    "ready_to_post": 3
  },
  "content": [
    {
      "id": "content_1",
      "caption": "Living my best life...",
      "hashtags": ["#lifestyle", "#authentic"],
      "image_path": "output/fanvue_content_1.png",
      "quality_score": 4.2,
      "quality_level": "GOOD",
      "passed_threshold": true,
      "estimated_engagement": "high"
    }
  ]
}
```

## 🔧 Customization

### Modifying Posting Schedule

Edit the cron expression in the Daily Posting Workflow:
```json
{
  "rule": {
    "hour": [6, 10, 14, 18, 22],  // Custom hours
    "minute": [0],
    "timezone": "America/New_York"  // Your timezone
  }
}
```

### Adding New Platforms

1. **Create Platform Node**:
   ```javascript
   // Add to Platform Router switch conditions
   {
     "operation": "equal",
     "value1": "={{$json.platform}}",
     "value2": "new_platform"
   }
   ```

2. **Add Posting Node**:
   ```javascript
   // HTTP Request node for new platform
   {
     "method": "POST",
     "url": "https://api.newplatform.com/v1/posts",
     "headers": {
       "Authorization": "Bearer {{$credentials.new_platform.api_key}}"
     },
     "body": {
       "content": "={{$json.content.caption}}",
       "media": "={{$json.content.image_path}}"
     }
   }
   ```

### Custom Content Rules

Modify content generation parameters:
```javascript
// In Content Generation node
const customRules = {
  "morning": {
    "content_type": "motivation",
    "style": "energetic",
    "hashtags": ["#mondaymotivation", "#goodmorning"]
  },
  "afternoon": {
    "content_type": "lifestyle", 
    "style": "casual",
    "hashtags": ["#lifestyle", "#authentic"]
  }
};
```

### Quality Thresholds

Adjust quality requirements:
```javascript
// In Quality Check node
const qualityThresholds = {
  "fanvue": 3.5,
  "loyalfans": 4.0,
  "instagram": 3.8,
  "twitter": 3.2
};

const minQuality = qualityThresholds[platform] || 3.5;
```

## 📊 Monitoring & Analytics

### Workflow Execution Logs

N8N provides detailed execution logs:
1. **Workflow History**: View past executions
2. **Node Execution Data**: See data flow between nodes
3. **Error Logs**: Detailed error information
4. **Performance Metrics**: Execution times and success rates

### Custom Monitoring

Add monitoring nodes to workflows:
```javascript
// Slack notification node
{
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "channel": "#fionasparx-alerts",
    "text": "Daily posting workflow completed: {{$json.results}}"
  }
}

// Email notification node
{
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "subject": "FionaSparx Daily Report",
    "text": "Content posted: {{$json.content_count}}\nEngagement: {{$json.avg_engagement}}"
  }
}
```

### Performance Analytics

Track workflow performance:
```javascript
// Analytics logging node
const performanceData = {
  "workflow_id": "daily_posting",
  "execution_time": Date.now() - startTime,
  "success_rate": successCount / totalCount,
  "content_generated": contentCount,
  "platforms_posted": platformsCount,
  "errors": errorCount
};
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Workflow Not Triggering
- Check cron expression syntax
- Verify workflow is activated
- Check N8N service status

#### 2. Authentication Errors
- Verify credentials are properly configured
- Check API key permissions
- Test credentials in individual nodes

#### 3. Content Generation Failures
- Check FionaSparx API endpoint availability
- Verify API request format
- Review error logs for specific issues

#### 4. Database Connection Issues
- Verify database credentials
- Check database server status
- Test connection from N8N

### Debugging Steps

1. **Test Individual Nodes**
   - Use "Execute Node" to test single nodes
   - Check input/output data
   - Verify node configuration

2. **Check Execution History**
   - Review failed executions
   - Examine error messages
   - Check data flow between nodes

3. **Enable Debug Mode**
   ```bash
   # Start N8N with debug logging
   N8N_LOG_LEVEL=debug n8n start
   ```

4. **Webhook Testing**
   ```bash
   # Test content generation webhook
   curl -X POST http://localhost:5678/webhook/content-generation \
     -H "Content-Type: application/json" \
     -d '{"platform": "fanvue", "content_type": "lifestyle", "count": 1}'
   ```

## 🔄 Backup & Recovery

### Workflow Backup
```bash
# Export workflows
n8n export:workflow --all --output=workflows/backup/

# Export credentials (encrypted)
n8n export:credentials --all --output=credentials/backup/
```

### Workflow Restoration
```bash
# Import workflows
n8n import:workflow --input=workflows/backup/

# Import credentials
n8n import:credentials --input=credentials/backup/
```

## 📈 Scaling & Optimization

### Performance Optimization
- Use workflow queues for high-volume processing
- Implement proper error handling and retries
- Monitor resource usage and optimize accordingly
- Use webhooks instead of polling where possible

### Horizontal Scaling
- Deploy multiple N8N instances
- Use external queue systems (Redis, RabbitMQ)
- Implement load balancing
- Use external databases (PostgreSQL, MySQL)

## 🎯 Best Practices

1. **Error Handling**: Always include error handling nodes
2. **Logging**: Log important events and metrics
3. **Testing**: Test workflows thoroughly before production
4. **Documentation**: Document custom modifications
5. **Monitoring**: Set up alerts for critical failures
6. **Security**: Use secure credential storage
7. **Performance**: Monitor and optimize execution times
8. **Backup**: Regular backup of workflows and data

## 📞 Support

For N8N specific issues:
- [N8N Documentation](https://docs.n8n.io/)
- [N8N Community](https://community.n8n.io/)
- [N8N GitHub](https://github.com/n8n-io/n8n)

For FionaSparx workflow issues:
- Check the setup guide
- Review workflow execution logs
- Test individual components
- Contact support with specific error messages