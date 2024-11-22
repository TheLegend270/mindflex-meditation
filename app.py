from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# List of available background music files
BACKGROUND_MUSIC_FILES = [
    'background_music.mp3',
    'green-hang-handpan-hangdrum-1765.mp3',
    'hari-om-namaha-shivaya-with-handpan-music-240022.mp3',
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
                {"role": "system", "content": "You are a meditation guide creating calming, mindful meditations. Provide the meditation script in plain text format without any markdown, formatting, or special characters. Always start with 'This is your meditation about [topic] which intends to [intention].' Then continue with the guided meditation in a natural, flowing way. Keep the language simple and direct."},
                {"role": "user", "content": f"Create a meditation script based on: {user_input}"}
            ]
        )
        
        # Select a random background track
        background_track = random.choice(BACKGROUND_MUSIC_FILES)
        
        meditation_script = response.choices[0].message.content
        return jsonify({
            "script": meditation_script,
            "background_music": background_track
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
