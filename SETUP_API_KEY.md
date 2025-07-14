# Setting Up OpenAI API Key

To use the AI features in HireVision, you need to set up your OpenAI API key.

## Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the generated API key

## Step 2: Create .env File

Create a file named `.env` in the project root directory (same level as `manage.py`) with the following content:

```
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_api_key_here

# Django Configuration
SECRET_KEY=django-insecure-6re@kum6gicewy1@bj!@nf+-2-!5cm@8r^-)beuc6xn3wz9907
DEBUG=True
```

Replace `your_actual_api_key_here` with the API key you copied from OpenAI.

## Step 3: Restart the Server

After creating the `.env` file, restart the Django development server:

```bash
python manage.py runserver
```

## Step 4: Test the Application

Now you should be able to use:
- Resume Analyzer
- Learning Path Analyzer
- Resume Builder

All AI features should work properly once the API key is configured.

## Troubleshooting

If you still get "Analysis failed" errors:

1. Make sure the `.env` file is in the correct location
2. Check that the API key is correct
3. Ensure you have sufficient credits in your OpenAI account
4. Check the console output for any error messages

## Note

The `.env` file is already in `.gitignore`, so your API key won't be committed to version control. 