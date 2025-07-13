def already_processed(post_id):
    if not os.path.exists(AUDIO_DIR):
        return False
    for fname in os.listdir(AUDIO_DIR):
        if fname.endswith('.wav') and post_id in fname:
            return True
    return False

def get_next_unprocessed_story(stories):
    for story in stories:
        post_id = story.get('id', '')
        if not already_processed(post_id):
            return story
    return None
import os
import re
from reddit_webscraper import get_scary_stories, save_story_json, print_story_statistics
from google_api_tts import tts_story_json

API_KEY = "AIzaSyAxmkLOLrUOFryzj5NMMZVTZ2mOwf_4HAo"
SUBREDDIT = "scarystories"  # Change this to any subreddit you want
AUDIO_DIR = 'audio'
JSON_DIR = 'reddit_stories'

def sanitize_filename(title):
    # Remove invalid filename characters and limit length
    filename = re.sub(r'[^\w\-_ ]', '', title)[:50].strip().replace(' ', '_')
    return filename or 'untitled'


def get_processing_status(stories):
    """
    Get processing status for all stories.
    
    Args:
        stories (list): List of stories
        
    Returns:
        dict: Processing status statistics
    """
    if not stories:
        return {'processed': 0, 'unprocessed': 0, 'total': 0}
    
    # All stories are considered unprocessed in this script
    return {
        'processed': 0,
        'unprocessed': len(stories),
        'total': len(stories),
        'completion_rate': 0.0
    }

def main():
    print(f"🎯 Fetching stories from r/{SUBREDDIT} and generating TTS audio...")
    # Ensure directories exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

    stories = get_scary_stories(subreddit=SUBREDDIT)
    if not stories:
        print("❌ No stories fetched. Exiting.")
        return

    print(f"📚 Retrieved {len(stories)} stories from Reddit")
    print_story_statistics(stories)
    status = get_processing_status(stories)
    print(f"\n🎯 Processing Status:")
    print(f"   ✅ Processed: {status['processed']}")
    print(f"   ⏳ Unprocessed: {status['unprocessed']}")
    print(f"   📊 Completion: {status['completion_rate']:.1f}%")

    # Find the next most popular unprocessed story
    next_story = get_next_unprocessed_story(stories)
    if not next_story:
        print("\n🎉 All top stories have already been processed!")
        return

    post_id = next_story.get('id', '')
    title = next_story.get('title', 'untitled')
    score = next_story.get('score', 0)
    safe_title = sanitize_filename(title)
    base_name = f"{safe_title}_{post_id}"
    json_path = os.path.join(JSON_DIR, f"{base_name}.json")
    audio_path = os.path.join(AUDIO_DIR, f"{base_name}.wav")

    print(f"\n🎯 Processing next unprocessed story:")
    print(f"   📖 Title: '{title}'")
    print(f"   📊 Score: {score}")
    print(f"   🆔 ID: {post_id}")

    try:
        save_story_json(next_story, json_path)
        print(f"💾 Saved story JSON to: {json_path}")
        print("🎤 Starting TTS generation...")
        tts_story_json(json_path, audio_path, API_KEY)
        print(f"✅ Success! Audio saved to: {audio_path}")
    except Exception as e:
        print(f"❌ Error processing story: {e}")
        return

if __name__ == "__main__":
    main()
