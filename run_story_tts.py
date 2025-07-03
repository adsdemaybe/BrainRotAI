import os
import re
from reddit_webscraper import get_scary_stories, save_story_json
from google_api_tts import tts_story_json

API_KEY = "AIzaSyAxmkLOLrUOFryzj5NMMZVTZ2mOwf_4HAo"
SUBREDDIT = "OneParagraph"  # Change this to any subreddit you want
AUDIO_DIR = 'audio'
JSON_DIR = 'reddit_stories'

def sanitize_filename(title):
    # Remove invalid filename characters and limit length
    filename = re.sub(r'[^\w\-_ ]', '', title)[:50].strip().replace(' ', '_')
    return filename or 'untitled'

def already_processed(post_id):
    # Check if a file with this post_id exists in the audio directory
    for fname in os.listdir(AUDIO_DIR):
        if fname.endswith('.wav') and post_id in fname:
            return True
    return False

def main():
    print(f"Fetching stories from r/{SUBREDDIT} and generating TTS audio for the next unprocessed one...")
    stories = get_scary_stories(subreddit=SUBREDDIT)
    if not stories:
        print("No stories fetched. Exiting.")
        return
    for story in stories:
        post_id = story.get('id', '')
        title = story.get('title', 'untitled')
        safe_title = sanitize_filename(title)
        base_name = f"{safe_title}_{post_id}"
        json_path = os.path.join(JSON_DIR, f"{base_name}.json")
        audio_path = os.path.join(AUDIO_DIR, f"{base_name}.wav")
        if not already_processed(post_id):
            save_story_json(story, json_path)
            tts_story_json(json_path, audio_path, API_KEY)
            print(f"Done! Check '{audio_path}' and '{json_path}' for results.")
            break
    else:
        print("All top stories have already been processed!")

if __name__ == "__main__":
    main()
