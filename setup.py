#!/usr/bin/env python3
"""
Setup script for BrainRotAI - Scary Story TTS + Image + Video Generator
"""

import subprocess
import sys
import os

def install_python_packages():
    """Install required Python packages"""
    print("📦 Installing Python packages...")
    
    packages = [
        "requests>=2.28.0",
        "google-genai>=0.3.0", 
        "Pillow>=9.0.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking for FFmpeg...")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and available")
            return True
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed or not in PATH")
        print("🔗 Please download FFmpeg from: https://ffmpeg.org/download.html")
        print("📝 Add FFmpeg to your system PATH after installation")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "audio",
        "reddit_stories", 
        "images",
        "videos"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def main():
    print("🎃 BrainRotAI Setup Script")
    print("=" * 50)
    
    # Install Python packages
    if not install_python_packages():
        print("❌ Failed to install Python packages. Please check your internet connection and try again.")
        return False
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    # Create directories
    create_directories()
    
    print("\n🎉 Setup Summary:")
    print("✅ Python packages installed")
    print("✅ Directories created")
    
    if ffmpeg_ok:
        print("✅ FFmpeg is ready")
        print("\n🚀 You're all set! Run 'python run_story_tts.py' to get started!")
    else:
        print("⚠️ FFmpeg needs to be installed for video generation")
        print("📝 You can still use the audio and image generation features")
        print("\n🚀 Run 'python run_story_tts.py' to start (video generation will be skipped)")
    
    return True

if __name__ == "__main__":
    main()
