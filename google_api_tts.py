from google import genai
from google.genai import types
import wave
import json
import os
import re
import time

# This script uses Google GenAI to convert text to speech (TTS) for a given story in JSON format.

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def split_text_smart(text, max_words=800):
   """Split text into chunks at sentence boundaries, respecting word limit
   
   Args:
       text (str): The text to split
       max_words (int): Maximum words per chunk (default: 800)
       
   Returns:
       list: List of text chunks
   """
   words = text.split()
   if len(words) <= max_words:
      return [text]
   
   chunks = []
   current_chunk = []
   current_word_count = 0
   
   # Split into sentences first
   sentences = re.split(r'(?<=[.!?])\s+', text)
   
   for sentence in sentences:
      sentence_words = len(sentence.split())
      
      # If adding this sentence would exceed the limit, start a new chunk
      if current_word_count + sentence_words > max_words and current_chunk:
         chunks.append(' '.join(current_chunk))
         current_chunk = [sentence]
         current_word_count = sentence_words
      else:
         current_chunk.append(sentence)
         current_word_count += sentence_words
   
   # Add the last chunk if there's content
   if current_chunk:
      chunks.append(' '.join(current_chunk))
   
   return chunks

def combine_wave_files(output_path, wave_data_list, channels=1, rate=24000, sample_width=2):
   """Combine multiple wave data into a single wave file"""
   with wave.open(output_path, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      
      for wave_data in wave_data_list:
         wf.writeframes(wave_data)

def tts_story_json(json_path, audio_out_path, api_key, voice_name='Kore'):
   """Convert story JSON to audio file using Google TTS API"""
   print(f"🎤 Starting TTS conversion...")
   print(f"📖 Reading story from: {json_path}")
   
   client = genai.Client(api_key=api_key)
   with open(json_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
   story_text = data.get('text', '')
   story_title = data.get('title', 'Unknown Title')
   story_score = data.get('score', 0)
   
   if not story_text.strip():
      print("❌ No text content found in story!")
      return
   
   # Count words to determine if we need to split
   word_count = len(story_text.split())
   print(f"📊 Story: '{story_title}' (Score: {story_score})")
   print(f"📝 Contains {word_count} words")
   
   if word_count <= 800:
      # Short text - process normally
      print("🔄 Processing as single chunk...")
      try:
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
         audio_data = response.candidates[0].content.parts[0].inline_data.data
         os.makedirs(os.path.dirname(audio_out_path), exist_ok=True)
         wave_file(audio_out_path, audio_data)
      except Exception as e:
         print(f"❌ Error generating audio: {e}")
         return
   else:
      # Long text - split into chunks
      print(f"📝 Text is long ({word_count} words), splitting into chunks...")
      chunks = split_text_smart(story_text)
      print(f"✂️ Split into {len(chunks)} chunks")
      
      # Estimate processing time (roughly 3-5 seconds per chunk + 1 second delay)
      estimated_time = len(chunks) * 5 + (len(chunks) - 1) * 1  # 5 sec per chunk + delays
      print(f"⏱️ Estimated processing time: ~{estimated_time} seconds ({estimated_time//60}m {estimated_time%60}s)")
      
      wave_data_list = []
      successful_chunks = 0
      
      for i, chunk in enumerate(chunks):
         chunk_words = len(chunk.split())
         print(f"🔄 Processing chunk {i+1}/{len(chunks)} ({chunk_words} words)...")
         try:
            response = client.models.generate_content(
               model="gemini-2.5-flash-preview-tts",
               contents=chunk,
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
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            wave_data_list.append(audio_data)
            successful_chunks += 1
            print(f"✅ Chunk {i+1} completed successfully")
            
            # Add a small delay between chunks to avoid rate limiting
            if i < len(chunks) - 1:  # Don't delay after the last chunk
               print("⏱️ Waiting 1 second before next chunk...")
               time.sleep(1)
               
         except Exception as e:
            print(f"❌ Error processing chunk {i+1}: {e}")
            continue
      
      if wave_data_list:
         print(f"🔗 Combining {successful_chunks}/{len(chunks)} successful audio chunks...")
         os.makedirs(os.path.dirname(audio_out_path), exist_ok=True)
         combine_wave_files(audio_out_path, wave_data_list)
         if successful_chunks < len(chunks):
            print(f"⚠️ Warning: {len(chunks) - successful_chunks} chunks failed, but audio was still generated")
      else:
         print("❌ No audio data generated. All chunks failed.")
         return
   
   print(f"🎵 Audio successfully saved to: {audio_out_path}")

if __name__ == "__main__":
   api_key = "AIzaSyBh3qOMFjY3rgNWpV5Ko_D9soZrTE1w--M"
   json_path = os.path.join(os.getcwd(), 'reddit_stories', 'scary_stories_quick.json')
   audio_out_path = os.path.join('audio', 'out.wav')
   tts_story_json(json_path, audio_out_path, api_key)