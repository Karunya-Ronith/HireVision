#!/usr/bin/env python3
"""
Test script for HireVision application
This script tests the basic functionality without requiring an OpenAI API key
"""

import os
import sys
from config import OPENAI_MODEL, ERROR_MESSAGES
from utils import (
    validate_inputs,
    sanitize_input,
    clean_text,
    truncate_text,
    extract_json_from_text,
    create_fallback_analysis,
    create_error_analysis,
)


def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"Error Messages Available: {len(ERROR_MESSAGES)}")
    print("✅ Configuration test passed\n")


def test_utils():
    """Test utility functions"""
    print("🛠️ Testing Utility Functions...")

    # Test sanitize_input
    test_input = "<script>alert('test')</script>Hello World"
    sanitized = sanitize_input(test_input)
    assert "<script>" not in sanitized, "Sanitization failed"
    print("✅ Input sanitization working")

    # Test clean_text
    test_text = "  Hello   World  \n\n  Test  "
    cleaned = clean_text(test_text)
    assert cleaned == "Hello World Test", "Text cleaning failed"
    print("✅ Text cleaning working")

    # Test truncate_text
    long_text = "A" * 1000
    truncated = truncate_text(long_text, 100)
    assert len(truncated) <= 103, "Text truncation failed"  # 100 + "..."
    print("✅ Text truncation working")

    # Test JSON extraction
    test_json = '{"test": "value", "number": 42}'
    extracted = extract_json_from_text(f"Some text {test_json} more text")
    assert (
        extracted is not None and extracted["test"] == "value"
    ), "JSON extraction failed"
    print("✅ JSON extraction working")

    # Test error analysis creation
    error_analysis = create_error_analysis("Test error")
    assert "Test error" in str(error_analysis), "Error analysis creation failed"
    print("✅ Error analysis creation working")

    print("✅ All utility functions working correctly\n")


def test_validation():
    """Test input validation"""
    print("✅ Testing Input Validation...")

    # Test with None values
    is_valid, error_msg = validate_inputs(None, "test job description")
    assert not is_valid, "Should fail with None PDF"
    print("✅ None PDF validation working")

    # Test with empty job description
    is_valid, error_msg = validate_inputs("fake_path.pdf", "")
    assert not is_valid, "Should fail with empty job description"
    print("✅ Empty job description validation working")

    # Test with short job description
    is_valid, error_msg = validate_inputs("fake_path.pdf", "short")
    assert not is_valid, "Should fail with short job description"
    print("✅ Short job description validation working")

    print("✅ Input validation working correctly\n")


def test_error_handling():
    """Test error handling functions"""
    print("🛡️ Testing Error Handling...")

    # Test API error handling
    from utils import handle_api_error

    # Simulate different error types
    rate_limit_error = Exception("rate limit exceeded")
    error_msg = handle_api_error(rate_limit_error)
    assert "rate limit" in error_msg.lower(), "Rate limit error handling failed"
    print("✅ Rate limit error handling working")

    timeout_error = Exception("request timed out")
    error_msg = handle_api_error(timeout_error)
    assert "timed out" in error_msg.lower(), "Timeout error handling failed"
    print("✅ Timeout error handling working")

    network_error = Exception("network connection failed")
    error_msg = handle_api_error(network_error)
    assert "network" in error_msg.lower(), "Network error handling failed"
    print("✅ Network error handling working")

    print("✅ Error handling working correctly\n")


def main():
    """Run all tests"""
    print("🚀 Starting HireVision Application Tests\n")

    try:
        test_config()
        test_utils()
        test_validation()
        test_error_handling()

        print("🎉 All tests passed! The application is ready to run.")
        print("\n📋 Summary of Improvements:")
        print("✅ Updated to gpt-4.1-nano model")
        print("✅ Enhanced error handling with retry logic")
        print("✅ Improved input validation and sanitization")
        print("✅ More lenient resume scoring (85-100 for excellent)")
        print("✅ Top 1% HR manager prompt for critical analysis")
        print("✅ Anti-hallucination instructions for learning paths")
        print("✅ Resource verification system")
        print("✅ Comprehensive error messages and user feedback")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
