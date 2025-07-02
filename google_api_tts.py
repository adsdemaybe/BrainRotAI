from google import genai
from google.genai import types
import wave
import json
import os

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def tts_story_json(json_path, audio_out_path, api_key, voice_name='Kore'):
   client = genai.Client(api_key=api_key)
   with open(json_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
   story_text = data.get('text', '')
   response = client.models.generate_content(
      model="gemini-2.5-flash-preview-tts",
      contents=story_text,
      config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
               voice_config=types.VoiceConfig(
                  prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                  )
               )
            ),
      )
   )
   data = response.candidates[0].content.parts[0].inline_data.data
   os.makedirs(os.path.dirname(audio_out_path), exist_ok=True)
   wave_file(audio_out_path, data)
   print(f"Audio saved to {audio_out_path}")

if __name__ == "__main__":
   api_key = "AIzaSyAxmkLOLrUOFryzj5NMMZVTZ2mOwf_4HAo"
   json_path = os.path.join(os.getcwd(), 'reddit_stories', 'scary_stories_quick.json')
   audio_out_path = os.path.join('audio', 'out.wav')
   tts_story_json(json_path, audio_out_path, api_key)