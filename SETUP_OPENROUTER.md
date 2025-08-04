# OpenRouter API Setup Guide

## Step 1: Get Your OpenRouter API Key

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key (it starts with `sk-or-`)

## Step 2: Update Your .env File

Add the following lines to your `.env` file:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen3-coder:free
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_MAX_TOKENS=4000
OPENROUTER_SITE_URL=http://localhost:8000
OPENROUTER_SITE_NAME=HireVision
```

**Important Notes:**
- Replace `sk-or-your-actual-api-key-here` with your actual OpenRouter API key
- The `OPENROUTER_SITE_URL` should be your actual website URL (using localhost for development)
- The `OPENROUTER_SITE_NAME` should be your actual application name

## Step 3: Recommended Models

### Free Models (No Credit Required)
- `qwen/qwen3-coder:free` - Good for coding tasks
- `mistralai/mistral-7b-instruct:free` - General purpose
- `meta-llama/llama-3.1-8b-instruct:free` - Good balance of quality and speed

### Paid Models (Require Credits)
- `anthropic/claude-3.5-sonnet` - High quality, similar to GPT-4
- `openai/gpt-4o` - OpenAI's latest model
- `meta-llama/llama-3.1-405b-instruct` - Massive 405B parameter model

## Step 4: Restart Your Server

After updating the `.env` file, restart your Django development server:

```bash
python manage.py runserver
```

## Step 5: Test the Integration

1. Go to your Resume Analysis page
2. Upload a resume and job description
3. Check if the analysis works with OpenRouter

## Troubleshooting

### Common Issues:

1. **"OpenRouter API Key Not Configured"**
   - Make sure your `.env` file has the correct `OPENROUTER_API_KEY`
   - Ensure the `.env` file is in the root directory of your project

2. **"Error connecting to OpenRouter API"**
   - Check your internet connection
   - Verify your API key is valid
   - Ensure you have sufficient credits (for paid models)

3. **Slow Response Times**
   - Try a different model
   - Check OpenRouter's status page for any service issues

## Benefits of OpenRouter

- **Access to Massive Models**: Use models with 405B+ parameters
- **Free Models Available**: No cost for basic usage
- **OpenAI-Compatible API**: Easy integration with existing code
- **Multiple Providers**: Access models from OpenAI, Anthropic, Meta, and more
- **Cost-Effective**: Often cheaper than direct API access

## Support

- OpenRouter Documentation: [docs.openrouter.ai](https://docs.openrouter.ai)
- OpenRouter Discord: [discord.gg/openrouter](https://discord.gg/openrouter)
- Model Status: [openrouter.ai/models](https://openrouter.ai/models) 