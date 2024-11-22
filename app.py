from flask import Flask, request, jsonify, render_template, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import hashlib
import json
from functools import lru_cache
from datetime import datetime

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
            {"role": "system", "content": "You are a meditation guide creating calming, mindful meditations. First, detect if the user's input is in German or English. Then, provide the ENTIRE meditation in that same language, including the introduction. For English, start with 'This is your meditation about [topic] which intends to [intention]...'. For German, start with 'Dies ist deine Meditation über [Thema], die darauf abzielt [Intention]...'. NEVER mix languages - if the input is German, the entire meditation must be in German, if it's English, everything must be in English. Keep the language simple, direct, and add '...' after each sentence to create natural pauses. This helps create a slower, more meditative pace."},
            {"role": "user", "content": f"Create a meditation script based on: {user_input}"}
        ]
    )
    return response.choices[0].message.content

def generate_speech(text):
    """Generate speech using OpenAI TTS"""
    return client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        speed=0.9,  # Setting speech speed to 90% of normal speed
        input=text
    )

@app.route('/generate-meditation', methods=['POST'])
def generate_meditation():
    """Generate meditation audio from user input"""
    try:
        data = request.get_json()
        user_input = data.get('input', '')

        if not user_input:
            return 'No input provided', 400

        # Generate meditation text
        meditation_text = generate_meditation_text(user_input)
        
        # Generate speech in a separate thread to not block
        speech_response = generate_speech(meditation_text)
        
        # Save the audio file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_filename = f'meditation_{timestamp}.mp3'
        audio_path = os.path.join(app.static_folder, audio_filename)
        
        with open(audio_path, 'wb') as f:
            speech_response.stream_to_file(audio_path)
        
        # Return the URL for the generated audio file
        return f'/static/{audio_filename}'

    except Exception as e:
        print(f"Error generating meditation: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
