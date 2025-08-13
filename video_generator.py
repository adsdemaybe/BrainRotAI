#!/usr/bin/env python3
"""
Video Generator for Scary Stories
Combines generated images with audio to create MP4 videos
"""

import os
import json
import math
from PIL import Image, ImageDraw, ImageFont
import subprocess
import wave

def get_audio_duration(audio_path):
    """
    Get the duration of an audio file in seconds
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        with wave.open(audio_path, 'rb') as audio_file:
            frames = audio_file.getnframes()
            sample_rate = audio_file.getframerate()
            duration = frames / float(sample_rate)
            return duration
    except Exception as e:
        print(f"❌ Error getting audio duration: {e}")
        return 0

def calculate_image_durations(images, total_duration):
    """
    Calculate how long each image should be displayed
    
    Args:
        images (list): List of image dictionaries
        total_duration (float): Total audio duration in seconds
        
    Returns:
        list: List of durations for each image
    """
    if not images:
        return []
    
    # Distribute time evenly across all images
    base_duration = total_duration / len(images)
    
    # Ensure minimum duration of 2 seconds per image
    min_duration = 2.0
    if base_duration < min_duration:
        base_duration = min_duration
    
    durations = [base_duration] * len(images)
    
    # If total duration is longer than needed, extend the last image
    total_calculated = sum(durations)
    if total_calculated < total_duration:
        durations[-1] += (total_duration - total_calculated)
    
    return durations

def resize_image_for_video(image_path, target_width=1920, target_height=1080):
    """
    Resize and pad image to fit video dimensions while maintaining aspect ratio
    
    Args:
        image_path (str): Path to image
        target_width (int): Target video width
        target_height (int): Target video height
        
    Returns:
        PIL.Image: Processed image
    """
    try:
        img = Image.open(image_path)
        
        # Calculate scaling to fit within target dimensions
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider than target ratio
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller than target ratio
            new_height = target_height
            new_width = int(target_height * img_ratio)
        
        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create black background
        background = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        
        # Center the image on the background
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        background.paste(img, (x_offset, y_offset))
        
        return background
        
    except Exception as e:
        print(f"❌ Error processing image {image_path}: {e}")
        # Return a black image as fallback
        return Image.new('RGB', (target_width, target_height), (0, 0, 0))

def create_text_overlay_image(text, width=1920, height=1080, font_size=48):
    """
    Create an image with text overlay for segments without generated images
    
    Args:
        text (str): Text to display
        width (int): Image width
        height (int): Image height
        font_size (int): Font size
        
    Returns:
        PIL.Image: Image with text
    """
    # Create dark background
    img = Image.new('RGB', (width, height), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit within image
        max_width = width - 100  # 50px margin on each side
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate vertical centering
        line_height = font_size + 10
        total_text_height = len(lines) * line_height
        start_y = (height - total_text_height) // 2
        
        # Draw text lines
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2]
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Draw text with slight shadow for better readability
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0))  # Shadow
            draw.text((x, y), line, font=font, fill=(255, 255, 255))  # Main text
        
    except Exception as e:
        print(f"⚠️ Error creating text overlay: {e}")
        # Simple fallback
        draw.text((50, height//2), text[:100] + "...", fill=(255, 255, 255))
    
    return img

def create_video_from_images_and_audio(images, audio_path, output_path, story_title):
    """
    Create MP4 video from images and audio using FFmpeg
    
    Args:
        images (list): List of image dictionaries with paths
        audio_path (str): Path to audio file
        output_path (str): Path for output video
        story_title (str): Story title for fallback
        
    Returns:
        bool: True if successful
    """
    try:
        print(f"🎬 Creating video: {output_path}")
        
        # Get audio duration
        audio_duration = get_audio_duration(audio_path)
        print(f"🎵 Audio duration: {audio_duration:.2f} seconds")
        
        if not images:
            print("❌ No images provided for video creation")
            return False
        
        # Calculate image durations
        durations = calculate_image_durations(images, audio_duration)
        print(f"📸 Using {len(images)} images with average duration of {sum(durations)/len(durations):.2f} seconds each")
        
        # Create temporary directory for processed images
        temp_dir = os.path.join(os.path.dirname(output_path), 'temp_video_images')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process and save images for video
        processed_images = []
        for i, (img_data, duration) in enumerate(zip(images, durations)):
            if os.path.exists(img_data['path']):
                processed_img = resize_image_for_video(img_data['path'])
            else:
                # Create text overlay if image doesn't exist
                text = img_data.get('segment_text', f'Part {i+1}')
                processed_img = create_text_overlay_image(text)
            
            # Save processed image
            temp_img_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            processed_img.save(temp_img_path, "PNG")
            processed_images.append((temp_img_path, duration))
        
        # Create FFmpeg input file list
        input_list_path = os.path.join(temp_dir, 'input_list.txt')
        with open(input_list_path, 'w') as f:
            for img_path, duration in processed_images:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            # Duplicate last image to ensure proper ending
            if processed_images:
                f.write(f"file '{processed_images[-1][0]}'\n")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create video with FFmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-f', 'concat',
            '-safe', '0',
            '-i', input_list_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',  # Stop when shortest stream ends
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        print("🎬 Running FFmpeg to create video...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video created successfully: {output_path}")
            
            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return False

def generate_story_video(json_path, audio_path, images_data, output_path):
    """
    Main function to generate a complete story video
    
    Args:
        json_path (str): Path to story JSON
        audio_path (str): Path to audio file
        images_data (list): List of generated images data
        output_path (str): Output video path
        
    Returns:
        bool: True if successful
    """
    try:
        # Load story data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        story_title = data.get('title', 'Unknown Story')
        
        print(f"🎬 Generating video for: '{story_title}'")
        
        success = create_video_from_images_and_audio(images_data, audio_path, output_path, story_title)
        
        if success:
            print(f"🎉 Story video generated successfully!")
            print(f"📹 Video saved to: {output_path}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error in video generation: {e}")
        return False

if __name__ == "__main__":
    # Test video creation
    print("🎬 Video Generator Test")
    print("This module requires FFmpeg to be installed and available in PATH")
