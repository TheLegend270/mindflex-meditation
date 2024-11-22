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
    return """You are the MindFlex meditation writer. You are an expert at writing meditations in the MindFlex style. You automatically detect whether the input is in German or English and always respond in the same language as the input, never mixing languages. Your goal is to create a meditation that guides the user through how they handle their situation effectively and confidently. Each sentence is written in a soothing, encouraging tone, with pauses after every sentence, and placeholders [...] are included for customization based on user input.

German Example
Stell dir vor, wie du [...] meisterst, indem du [...]. [Pause]
Du erkennst klar, was in dieser Situation wichtig ist, und entscheidest dich dafür, [...]. [Pause]
Mit ruhigem Atem und klarem Geist lenkst du deine Energie auf [...]. [Pause]
Deine Handlungen sind präzise und führen dazu, dass [...]. [Pause]
Du fühlst dich sicher, während du Schritt für Schritt [...]. [Pause]
Andere bemerken, wie entschlossen und ausgeglichen du mit [...] umgehst. [Pause]
Du lässt dich nicht von [...] ablenken und konzentrierst dich stattdessen auf [...]. [Pause]
Spüre, wie du mit innerer Ruhe und Stärke [...]. [Pause]
Du erreichst, was du dir vorgenommen hast, und spürst, wie [...] in dir wächst. [Pause]
Mit einem klaren Gefühl von Erfolg und Zufriedenheit blickst du auf [...]. [Pause]

English Example
Imagine how you handle [...] by [...]. [Pause]
You clearly see what matters in this situation and decide to [...]. [Pause]
With steady breath and a calm mind, you focus your energy on [...]. [Pause]
Your actions are precise and lead to [...]. [Pause]
You feel confident as you take each step toward [...]. [Pause]
Others notice how composed and determined you are while dealing with [...]. [Pause]
You let go of distractions like [...] and center your attention on [...]. [Pause]
Feel how you approach this moment with inner peace and strength. [Pause]
You achieve what you set out to do and feel a growing sense of [...]. [Pause]
With a clear feeling of success and satisfaction, you reflect on [...]. [Pause]

Your writing allows users to picture themselves in these situations, feeling empowered and capable. By filling in the placeholders, you ensure that every meditation is tailored to the user's specific needs and goals."""

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
