# BrainRotAI

Small Python toolkit that:
- Scrapes top text posts from a subreddit via Reddit’s public JSON endpoints
- Saves stories to JSON
- Generates TTS audio from a story JSON (Google API)
- (Optional) Generates images/videos (requires FFmpeg for video)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Video generation requires FFmpeg installed and on your `PATH`.

## Quick start

Run a basic system check:

```bash
python test_system.py
```

Fetch the next unprocessed story and generate a `.wav`:

```bash
python run_story_tts.py
```

Note: `run_story_tts.py` currently contains a hard-coded API key; replace it with your own key (and avoid committing secrets).
