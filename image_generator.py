#!/usr/bin/env python3
"""
Image Generator for Scary Stories
Uses Google Gemini to generate images based on story paragraphs/sentences
"""

from google import genai
from google.genai import types
import json
import os
import re
import time
from PIL import Image
import io
import base64

def split_story_into_segments(text, segment_type='paragraph'):
    """
    Split story text into segments (paragraphs or sentences)
    
    Args:
        text (str): The story text
        segment_type (str): 'paragraph' or 'sentence'
        
    Returns:
        list: List of text segments
    """
    if segment_type == 'paragraph':
        # Split by double newlines or single newlines followed by significant spacing
        segments = re.split(r'\n\s*\n|\n(?=\s{4,})', text.strip())
        segments = [seg.strip() for seg in segments if seg.strip()]
    else:  # sentence
        # Split by sentence endings
        segments = re.split(r'(?<=[.!?])\s+', text.strip())
        segments = [seg.strip() for seg in segments if seg.strip()]
    
    return segments

def generate_image_prompt(segment, story_title, style="dark horror art"):
    """
    Create an image generation prompt based on a story segment
    
    Args:
        segment (str): Text segment to base the image on
        story_title (str): Title of the story for context
        style (str): Art style for the image
        
    Returns:
        str: Generated prompt for image creation
    """
    # Extract key visual elements from the text
    prompt = f"Create a {style} illustration based on this text: '{segment[:200]}...' "
    prompt += f"Style: atmospheric, cinematic, dark mood, high contrast lighting. "
    prompt += f"Theme from '{story_title}'. Focus on visual storytelling, "
    prompt += f"mysterious atmosphere, detailed environment. No text overlays."
    
    return prompt

def generate_image_from_text(client, segment, story_title, image_path, style="dark horror art"):
    """
    Generate an image using Google Gemini based on text segment
    
    Args:
        client: Google GenAI client
        segment (str): Text segment
        story_title (str): Story title for context
        image_path (str): Path to save the image
        style (str): Image style
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        prompt = generate_image_prompt(segment, story_title, style)
        print(f"🎨 Generating image for: '{segment[:50]}{'...' if len(segment) > 50 else ''}'")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-exp",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )
        
        # Get image data
        image_data = response.candidates[0].content.parts[0].inline_data.data
        
        # Convert base64 to image and save
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Save as high quality PNG
        image.save(image_path, "PNG", quality=95)
        print(f"✅ Image saved: {image_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return False

def generate_story_images(json_path, images_dir, api_key, segment_type='paragraph', style="dark horror art"):
    """
    Generate images for all segments of a story
    
    Args:
        json_path (str): Path to story JSON file
        images_dir (str): Directory to save images
        api_key (str): Google API key
        segment_type (str): 'paragraph' or 'sentence'
        style (str): Image style
        
    Returns:
        list: List of generated image paths
    """
    print(f"🎨 Starting image generation for story segments...")
    
    # Load story data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    story_text = data.get('text', '')
    story_title = data.get('title', 'Unknown Story')
    story_id = data.get('id', 'unknown')
    
    if not story_text.strip():
        print("❌ No story text found!")
        return []
    
    # Split story into segments
    segments = split_story_into_segments(story_text, segment_type)
    print(f"📄 Split story into {len(segments)} {segment_type}s")
    
    # Create images directory
    story_images_dir = os.path.join(images_dir, f"{story_id}_{segment_type}s")
    os.makedirs(story_images_dir, exist_ok=True)
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    generated_images = []
    successful_generations = 0
    
    for i, segment in enumerate(segments):
        if len(segment.strip()) < 10:  # Skip very short segments
            continue
            
        image_filename = f"{segment_type}_{i+1:03d}.png"
        image_path = os.path.join(story_images_dir, image_filename)
        
        print(f"🎨 Processing {segment_type} {i+1}/{len(segments)}...")
        
        success = generate_image_from_text(client, segment, story_title, image_path, style)
        
        if success:
            generated_images.append({
                'path': image_path,
                'segment_text': segment,
                'index': i,
                'type': segment_type
            })
            successful_generations += 1
        
        # Add delay to avoid rate limiting
        if i < len(segments) - 1:
            print("⏱️ Waiting 2 seconds before next image...")
            time.sleep(2)
    
    print(f"🎨 Image generation complete!")
    print(f"✅ Successfully generated {successful_generations}/{len(segments)} images")
    
    return generated_images

def create_title_image(client, story_title, story_text, image_path, api_key, style="dark horror art"):
    """
    Create a title/cover image for the story
    
    Args:
        client: Google GenAI client
        story_title (str): Story title
        story_text (str): Full story text for context
        image_path (str): Path to save title image
        api_key (str): Google API key
        style (str): Image style
        
    Returns:
        bool: True if successful
    """
    try:
        # Create a comprehensive prompt for the title image
        story_summary = story_text[:300] + "..." if len(story_text) > 300 else story_text
        
        prompt = f"Create a dramatic {style} title card illustration for the horror story '{story_title}'. "
        prompt += f"Based on this story excerpt: '{story_summary}' "
        prompt += f"Style: cinematic movie poster, dark atmosphere, mysterious, high contrast, "
        prompt += f"professional book cover design. Central focus on the main theme. "
        prompt += f"No text overlays - pure visual storytelling."
        
        print(f"🎨 Generating title image for: '{story_title}'")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-exp", 
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )
        
        # Get image data and save
        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path, "PNG", quality=95)
        
        print(f"✅ Title image saved: {image_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating title image: {e}")
        return False

if __name__ == "__main__":
    # Test the image generation
    api_key = "AIzaSyAxmkLOLrUOFryzj5NMMZVTZ2mOwf_4HAo"
    json_path = os.path.join('reddit_stories', 'test_story.json')
    images_dir = 'images'
    
    if os.path.exists(json_path):
        generate_story_images(json_path, images_dir, api_key, segment_type='paragraph')
    else:
        print(f"Test JSON file not found: {json_path}")
