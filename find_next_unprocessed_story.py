import os
import re
from reddit_webscraper import get_scary_stories

SUBREDDIT = "scarystories"  # Change this to any subreddit you want
AUDIO_DIR = 'audio'

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

def main():
    print(f"🔍 Fetching stories from r/{SUBREDDIT}...")
    stories = get_scary_stories(subreddit=SUBREDDIT)
    if not stories:
        print("❌ No stories fetched.")
        return
    next_story = get_next_unprocessed_story(stories)
    if next_story:
        print("\nNext unprocessed story:")
        print(f"  📖 Title: {next_story.get('title', 'untitled')}")
        print(f"  🆔 ID: {next_story.get('id', '')}")
        print(f"  📊 Score: {next_story.get('score', 0)}")
    else:
        print("🎉 All top stories have already been processed!")

if __name__ == "__main__":
    main()
