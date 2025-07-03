#!/usr/bin/env python3
# Quick Reddit Scary Stories Scraper
"""
Quick Reddit Scary Stories Scraper
Fetches scary stories without API credentials using Reddit's JSON endpoints
"""

import requests
import json
from datetime import datetime
import os

def get_scary_stories(subreddit="scarystories", time_filter='week', limit=25):
    """Fetch scary stories from a given subreddit (default: r/OneParagraph)
    
    Args:
        subreddit (str): Subreddit name without 'r/'
        time_filter (str): Time filter ('week', 'month', 'year', 'all')
        limit (int): Maximum number of posts to fetch
    """
    
    print(f"🎃 Fetching scary stories from r/{subreddit}...")
    
    # Reddit's public JSON endpoint
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    
    headers = {
        'User-Agent': 'ScaryStoryScraper/1.0 (Educational Purpose)'
    }
    
    params = {
        't': time_filter,  # time filter
        'limit': limit     # number of posts
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
                'id': post.get('id', ''),
                'word_count': len(selftext.split())
            }
            stories.append(story)
        
        # Sort by score (highest first)
        stories.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"📊 Found {len(stories)} valid stories with text content")
        if stories:
            print(f"🏆 Top story has {stories[0]['score']} upvotes")
            print(f"📝 Stories range from {min(s['word_count'] for s in stories)} to {max(s['word_count'] for s in stories)} words")
        
        return stories
        
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

def get_story_statistics(stories):
    """Get statistics about the fetched stories
    
    Args:
        stories (list): List of story dictionaries
        
    Returns:
        dict: Statistics about the stories
    """
    if not stories:
        return {}
    
    scores = [s['score'] for s in stories]
    word_counts = [s['word_count'] for s in stories]
    
    stats = {
        'total_stories': len(stories),
        'avg_score': sum(scores) / len(scores),
        'max_score': max(scores),
        'min_score': min(scores),
        'avg_word_count': sum(word_counts) / len(word_counts),
        'max_word_count': max(word_counts),
        'min_word_count': min(word_counts),
        'long_stories': len([w for w in word_counts if w > 800])  # Stories that will be chunked
    }
    
    return stats

def print_story_statistics(stories):
    """Print formatted statistics about the stories"""
    stats = get_story_statistics(stories)
    if not stats:
        print("📊 No stories to analyze")
        return
    
    print("\n📊 Story Statistics:")
    print(f"   📚 Total stories: {stats['total_stories']}")
    print(f"   🏆 Score range: {stats['min_score']} - {stats['max_score']} (avg: {stats['avg_score']:.1f})")
    print(f"   📝 Word count range: {stats['min_word_count']} - {stats['max_word_count']} (avg: {stats['avg_word_count']:.1f})")
    print(f"   📄 Long stories (>800 words): {stats['long_stories']}")
    
    if stats['long_stories'] > 0:
        print(f"   ⚠️  {stats['long_stories']} stories will be processed in chunks for TTS")

def fetch_and_save_top_story(json_path, subreddit="scarystories"):
    stories = get_scary_stories(subreddit=subreddit)
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
