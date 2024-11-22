from flask import Flask, request, jsonify, render_template, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# List of available background music files
BACKGROUND_MUSIC_FILES = [
    'background_music.mp3',
    'green-hang-handpan-hangdrum-1765.mp3',
    'relaxing-handpan-music-8d-surround-233447.mp3'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/generate-meditation', methods=['POST'])
def generate_meditation():
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        # Create the meditation using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a meditation guide creating calming, mindful meditations. First, detect if the user's input is in German or English, then provide the meditation in that same language. Provide the meditation script in plain text format without any markdown, formatting, or special characters. Always start with 'This is your meditation about [topic] which intends to [intention]' (or in German: 'Dies ist deine Meditation über [Thema], die darauf abzielt [Intention]'). Then continue with the guided meditation in a natural, flowing way. Keep the language simple and direct."},
                {"role": "user", "content": f"Create a meditation script based on: {user_input}"}
            ]
        )
        
        meditation_script = response.choices[0].message.content
        
        # Generate speech using OpenAI TTS
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=meditation_script
        )
        
        # Select a random background track
        background_track = random.choice(BACKGROUND_MUSIC_FILES)
        
        # Save the audio temporarily
        speech_file_path = os.path.join(static_dir, 'temp_meditation.mp3')
        speech_response.stream_to_file(speech_file_path)
        
        return jsonify({
            "script": meditation_script,
            "audio_url": "/static/temp_meditation.mp3",
            "background_music": background_track
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
