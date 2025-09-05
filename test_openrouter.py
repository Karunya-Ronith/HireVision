#!/usr/bin/env python3
"""
Test script to check both OpenRouter and OpenAI API integration
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
    # OPENROUTER_MAX_TOKENS,  # Using default max tokens
    OPENROUTER_SITE_URL,
    OPENROUTER_SITE_NAME,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    # OPENAI_MAX_TOKENS,  # Using default max tokens
    USE_OPENAI_OVERRIDE,
)
from utils import get_api_client, make_api_call

def test_api_integration():
    """Test both OpenRouter and OpenAI API integration"""
    
    print("=== API Integration Test ===")
    print(f"Override setting: {USE_OPENAI_OVERRIDE}")
    print(f"OpenRouter API Key configured: {bool(OPENROUTER_API_KEY)}")
    print(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")
    print()
    
    # Test the centralized API client function
    try:
        print("Testing centralized API client function...")
        client, config = get_api_client()
        
        print(f"✅ API client created successfully!")
        print(f"Model: {config['model']}")
        print(f"Temperature: {config['temperature']}")
        print(f"Max Tokens: {config['max_tokens']}")
        print(f"Extra Headers: {config.get('extra_headers', {})}")
        print()
        
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
        
        print("Making API call using centralized function...")
        
        system_message = "You are a top 1% HR manager with exceptional talent evaluation skills. Provide thorough, fair, and constructive resume analysis."
        messages = [{"role": "user", "content": test_prompt}]
        
        content = make_api_call(messages, system_message)
        
        print("✅ API call successful!")
        print(f"Response length: {len(content)} characters")
        print(f"Response preview: {content[:500]}...")
        print()
        
        # Try to extract JSON
        import json
        
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


def test_both_apis():
    """Test both OpenRouter and OpenAI APIs"""
    
    print("=== Testing Both APIs ===")
    
    # Test OpenRouter (if not in override mode)
    if not USE_OPENAI_OVERRIDE and OPENROUTER_API_KEY:
        print("\n--- Testing OpenRouter API ---")
        try:
            # Temporarily set override to False to test OpenRouter
            import config
            original_override = config.USE_OPENAI_OVERRIDE
            config.USE_OPENAI_OVERRIDE = False
            
            success = test_api_integration()
            config.USE_OPENAI_OVERRIDE = original_override
            
            if success:
                print("✅ OpenRouter API test passed!")
            else:
                print("❌ OpenRouter API test failed!")
        except Exception as e:
            print(f"❌ OpenRouter API test error: {e}")
    
    # Test OpenAI (if available)
    if OPENAI_API_KEY:
        print("\n--- Testing OpenAI API ---")
        try:
            # Temporarily set override to True to test OpenAI
            import config
            original_override = config.USE_OPENAI_OVERRIDE
            config.USE_OPENAI_OVERRIDE = True
            
            success = test_api_integration()
            config.USE_OPENAI_OVERRIDE = original_override
            
            if success:
                print("✅ OpenAI API test passed!")
            else:
                print("❌ OpenAI API test failed!")
        except Exception as e:
            print(f"❌ OpenAI API test error: {e}")
    
    print("\n--- Current Configuration ---")
    print(f"USE_OPENAI_OVERRIDE: {USE_OPENAI_OVERRIDE}")
    if USE_OPENAI_OVERRIDE:
        print("Currently using: OpenAI")
    else:
        print("Currently using: OpenRouter")

if __name__ == "__main__":
    print("🚀 Starting API Integration Tests...")
    print()
    
    # Test current configuration
    success = test_api_integration()
    if success:
        print("\n🎉 Current API configuration test passed!")
    else:
        print("\n💥 Current API configuration test failed!")
    
    print("\n" + "="*50)
    
    # Test both APIs
    test_both_apis()
    
    print("\n" + "="*50)
    print("🏁 API Integration Tests Complete!") 