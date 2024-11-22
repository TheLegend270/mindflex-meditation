from flask import Flask, request, jsonify, render_template, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import hashlib
import json
from functools import lru_cache

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
for directory in [static_dir, cache_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# List of available background music files
BACKGROUND_MUSIC_FILES = [
    'background_music.mp3',
    'green-hang-handpan-hangdrum-1765.mp3',
    'relaxing-handpan-music-8d-surround-233447.mp3'
]

@lru_cache(maxsize=100)
def get_cached_meditation(input_text):
    """Cache meditation responses based on input text"""
    # Create a unique hash for the input
    input_hash = hashlib.md5(input_text.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{input_hash}.json")
    
    # Check if we have a cached response
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_to_cache(input_text, response_data):
    """Save meditation response to cache"""
    input_hash = hashlib.md5(input_text.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{input_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

def generate_meditation_text(user_input):
    """Generate meditation text using OpenAI"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a meditation guide creating calming, mindful meditations. First, detect if the user's input is in German or English. Then, provide the ENTIRE meditation in that same language, including the introduction. For English, start with 'This is your meditation about [topic] which intends to [intention]'. For German, start with 'Dies ist deine Meditation über [Thema], die darauf abzielt [Intention]'. NEVER mix languages - if the input is German, the entire meditation must be in German, if it's English, everything must be in English. Keep the language simple, direct, and maintain a slow, calming pace."},
            {"role": "user", "content": f"Create a meditation script based on: {user_input}"}
        ]
    )
    return response.choices[0].message.content

def generate_speech(text):
    """Generate speech using OpenAI TTS"""
    return client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        speed=0.95,  # Slowing down the speech to 95% of normal speed
        input=text
    )

@app.route('/generate-meditation', methods=['POST'])
def generate_meditation():
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        # Check cache first
        cached_response = get_cached_meditation(user_input)
        if cached_response:
            return jsonify(cached_response)
        
        # Generate new meditation if not cached
        meditation_script = generate_meditation_text(user_input)
        speech_response = generate_speech(meditation_script)
        
        # Select a random background track
        background_track = random.choice(BACKGROUND_MUSIC_FILES)
        
        # Save the audio temporarily
        speech_file_path = os.path.join(static_dir, 'temp_meditation.mp3')
        speech_response.stream_to_file(speech_file_path)
        
        response_data = {
            "script": meditation_script,
            "audio_url": "/static/temp_meditation.mp3",
            "background_music": background_track
        }
        
        # Save to cache
        save_to_cache(user_input, response_data)
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
