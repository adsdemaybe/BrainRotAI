#!/usr/bin/env python3
"""
Test script for BrainRotAI components
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"❌ PIL/Pillow import failed: {e}")
        return False
    
    try:
        import json
        import os
        import re
        import time
        import math
        import subprocess
        print("✅ Standard library modules imported successfully")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False
    
    try:
        from google import genai
        from google.genai import types
        print("✅ Google GenAI imported successfully")
    except ImportError as e:
        print(f"❌ Google GenAI import failed: {e}")
        print("📝 Note: This is expected if google-genai is not installed")
        print("📝 Run: pip install google-genai")
        return False
    
    return True

def test_project_modules():
    """Test if project modules can be imported"""
    print("\n🧪 Testing project modules...")
    
    try:
        import reddit_webscraper
        print("✅ reddit_webscraper imported successfully")
    except ImportError as e:
        print(f"❌ reddit_webscraper import failed: {e}")
        return False
    
    try:
        import google_api_tts
        print("✅ google_api_tts imported successfully")
    except ImportError as e:
        print(f"❌ google_api_tts import failed: {e}")
        return False
    
    try:
        import image_generator
        print("✅ image_generator imported successfully")
    except ImportError as e:
        print(f"❌ image_generator import failed: {e}")
        return False
    
    try:
        import video_generator
        print("✅ video_generator imported successfully")
    except ImportError as e:
        print(f"❌ video_generator import failed: {e}")
        return False
    
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\n🧪 Testing FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg returned an error")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("📝 Video generation will not work without FFmpeg")
        print("🔗 Download from: https://ffmpeg.org/download.html")
        return False

def test_directories():
    """Test if required directories exist or can be created"""
    print("\n🧪 Testing directories...")
    
    directories = ["audio", "reddit_stories", "images", "videos"]
    
    for directory in directories:
        try:
            import os
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Directory {directory} ready")
        except Exception as e:
            print(f"❌ Cannot create directory {directory}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🎃 BrainRotAI System Test")
    print("=" * 40)
    
    tests = [
        ("Core Dependencies", test_imports),
        ("Project Modules", test_project_modules), 
        ("FFmpeg", test_ffmpeg),
        ("Directories", test_directories)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print(f"\n🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("🚀 Run 'python run_story_tts.py' to start generating content!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        if passed >= total - 1:  # Allow FFmpeg to be missing
            print("📝 You can still use audio and image generation features.")

if __name__ == "__main__":
    main()
