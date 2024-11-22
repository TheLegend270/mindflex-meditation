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
from streaming import StreamingManager

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
streaming_manager = StreamingManager(client)

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

def create_system_prompt(language):
    if language == "de":
        return """Du bist ein professioneller Meditationsleiter. Erstelle eine beruhigende und personalisierte Meditation basierend auf der Eingabe des Benutzers.
        Verwende eine sanfte, beruhigende Sprache. Füge '<break time="2s" />' hinter jeden Satz ein, um natürliche Pausen zu erzeugen.
        Sprich den Benutzer direkt an und führe ihn durch die Meditation. Die Meditation sollte etwa 5-7 Minuten dauern."""
    else:
        return """You are a professional meditation guide. Create a calming and personalized meditation based on the user's input.
        Use gentle, soothing language. Add '<break time="2s" />' after each sentence to create natural pauses.
        Address the user directly and guide them through the meditation. The meditation should last about 5-7 minutes."""

@app.route('/stream-meditation', methods=['POST'])
def stream_meditation():
    """Stream meditation text and audio"""
    try:
        data = request.get_json()
        user_input = data.get('input', '')

        if not user_input:
            return 'No input provided', 400

        language = "de" if user_input.startswith("de") else "en"
        system_prompt = create_system_prompt(language)

        return streaming_manager.stream_meditation(system_prompt, user_input)

    except Exception as e:
        print(f"Error streaming meditation: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
