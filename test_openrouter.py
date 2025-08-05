#!/usr/bin/env python3
"""
Test script to check OpenRouter API integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_TEMPERATURE,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_SITE_URL,
    OPENROUTER_SITE_NAME,
)

def test_openrouter_api():
    """Test the OpenRouter API with a simple prompt"""
    
    print("=== OpenRouter API Test ===")
    print(f"API Key configured: {bool(OPENROUTER_API_KEY)}")
    print(f"API Key starts with: {OPENROUTER_API_KEY[:10] if OPENROUTER_API_KEY else 'None'}...")
    print(f"Base URL: {OPENROUTER_BASE_URL}")
    print(f"Model: {OPENROUTER_MODEL}")
    print(f"Temperature: {OPENROUTER_TEMPERATURE}")
    print(f"Max Tokens: {OPENROUTER_MAX_TOKENS}")
    print(f"Site URL: {OPENROUTER_SITE_URL}")
    print(f"Site Name: {OPENROUTER_SITE_NAME}")
    print()
    
    if not OPENROUTER_API_KEY:
        print("❌ No OpenRouter API key found!")
        return False
    
    try:
        # Create the client
        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        
        # Test prompt
        test_prompt = """
        You are a top 1% HR manager. Analyze this simple resume against a job description.
        
        Resume: John Doe, Software Engineer with 3 years of experience in Python and web development.
        
        Job Description: We are looking for a Python developer with 2+ years of experience.
        
        Please provide your analysis in the following JSON format:
        {
            "ats_score": 85,
            "score_explanation": "Strong match for the position",
            "strengths": ["Relevant experience", "Good technical skills"],
            "weaknesses": ["Could add more details"],
            "recommendations": ["Include more quantifiable achievements"],
            "skills_gap": ["Advanced cloud computing"],
            "upskilling_suggestions": ["Learn AWS"],
            "overall_assessment": "Good candidate with room for improvement"
        }
        """
        
        print("Making API call...")
        
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": OPENROUTER_SITE_URL,
                "X-Title": OPENROUTER_SITE_NAME,
            },
            extra_body={},
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a top 1% HR manager with exceptional talent evaluation skills. Provide thorough, fair, and constructive resume analysis.",
                },
                {"role": "user", "content": test_prompt},
            ],
            temperature=OPENROUTER_TEMPERATURE,
            max_tokens=OPENROUTER_MAX_TOKENS,
        )
        
        content = response.choices[0].message.content
        print("✅ API call successful!")
        print(f"Response length: {len(content)} characters")
        print(f"Response preview: {content[:500]}...")
        print()
        
        # Try to extract JSON
        import json
        import re
        
        # Find JSON in the response
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = content[start_idx:end_idx]
            print("Found JSON in response:")
            print(json_str)
            print()
            
            # Try to parse it
            try:
                parsed_json = json.loads(json_str)
                print("✅ JSON parsed successfully!")
                print(f"ATS Score: {parsed_json.get('ats_score')}")
                print(f"Strengths: {parsed_json.get('strengths')}")
                print(f"Weaknesses: {parsed_json.get('weaknesses')}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                return False
        else:
            print("❌ No JSON found in response")
            return False
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_api()
    if success:
        print("\n🎉 OpenRouter API test passed!")
    else:
        print("\n💥 OpenRouter API test failed!") 