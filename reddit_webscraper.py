#!/usr/bin/env python3
"""
Quick Reddit Scary Stories Scraper
Fetches scary stories without API credentials using Reddit's JSON endpoints
"""

import requests
import json
from datetime import datetime
import os

def get_scary_stories():
    """Fetch scary stories from r/OneParagraph"""
    
    print("🎃 Fetching scary stories from r/OneParagraph...")
    
    # Reddit's public JSON endpoint
    url = "https://www.reddit.com/r/OneParagraph/top.json"
    
    headers = {
        'User-Agent': 'ScaryStoryScraper/1.0 (Educational Purpose)'
    }
    
    params = {
        't': 'week',  # time filter: week
        'limit': 25   # number of posts
    }
    
    try:
        print(f"🔍 Requesting data from Reddit...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print("Reddit might be blocking requests or the subreddit is restricted")
            return []
        
        data = response.json()
        posts = data['data']['children']
        
        print(f"📥 Retrieved {len(posts)} posts from Reddit")
        
        stories = []
        for post_data in posts:
            post = post_data['data']
            
            # Skip if no text content or removed/deleted
            selftext = post.get('selftext', '')
            if not selftext or selftext in ['[removed]', '[deleted]', '']:
                continue
            
            # Skip if it's just a link post
            if len(selftext.strip()) < 50:
                continue
            
            story = {
                'title': post.get('title', 'No Title'),
                'author': post.get('author', '[deleted]'),
                'score': post.get('score', 0),
                'upvote_ratio': post.get('upvote_ratio', 0),
                'created_utc': post.get('created_utc', 0),
                'created_date': datetime.fromtimestamp(post.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'url': f"https://reddit.com{post.get('permalink', '')}",
                'text': selftext,
                'num_comments': post.get('num_comments', 0),
                'awards': post.get('total_awards_received', 0),
                'id': post.get('id', '')
            }
            stories.append(story)
        
        # Sort by score (highest first)
        stories.sort(key=lambda x: x['score'], reverse=True)
        
        if stories:
            return [stories[0]]  # Return only the top story as a list
        else:
            return []
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Reddit might be slow or blocking requests.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from Reddit")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

def save_story_json(story, out_path):
    """Save a single story to a JSON file at the given path"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    print(f"💾 Story saved to '{out_path}'")

def fetch_and_save_top_story(json_path):
    stories = get_scary_stories()
    if stories:
        top_story = stories[0]
        save_story_json(top_story, json_path)
        return top_story
    else:
        print("No stories found.")
        return None

def main():
    print("🕷️  SCARY STORY SCRAPER - NO API REQUIRED! 🕷️")
    print("=" * 60)
    json_path = os.path.join('reddit_stories', 'scary_stories_quick.json')
    fetch_and_save_top_story(json_path)

if __name__ == "__main__":
    main()
