import os
from reddit_webscraper import fetch_and_save_top_story
from google_api_tts import tts_story_json

REDDIT_JSON_PATH = os.path.join('reddit_stories', 'scary_stories_quick.json')
AUDIO_OUT_PATH = os.path.join('audio', 'out.wav')
API_KEY = "AIzaSyAxmkLOLrUOFryzj5NMMZVTZ2mOwf_4HAo"

def main():
    print("Fetching top scary story and generating TTS audio...")
    top_story = fetch_and_save_top_story(REDDIT_JSON_PATH)
    if top_story:
        tts_story_json(REDDIT_JSON_PATH, AUDIO_OUT_PATH, API_KEY)
        print(f"Done! Check '{AUDIO_OUT_PATH}' and '{REDDIT_JSON_PATH}' for results.")
    else:
        print("No story fetched. Exiting.")

if __name__ == "__main__":
    main()
