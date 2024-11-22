from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import yt_dlp
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# List of available background music tracks
BACKGROUND_TRACKS = [
    'background_music.mp3',  # Original track
    'green-hang-handpan-hangdrum-1765.mp3',
    'hari-om-namaha-shivaya-with-handpan-music-240022.mp3',
    'relaxing-handpan-music-8d-surround-233447.mp3'
]

# Download YouTube audio if not already downloaded
def download_background_music(url):
    output_path = os.path.join('static', 'background_music.mp3')
    if not os.path.exists(output_path):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    return 'background_music.mp3'

# Download the background music on startup
BACKGROUND_MUSIC_URL = 'https://www.youtube.com/watch?v=CIyiHdxE4gw'
download_background_music(BACKGROUND_MUSIC_URL)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/generate-meditation', methods=['POST'])
def generate_meditation():
    data = request.json
    user_input = data.get('input', '')
    
    try:
        # Generate meditation script using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Create a guided meditation that begins by clearly stating the intent and purpose of the session, personalized to the user's specific situation. The meditation should:  

1. Start with an opening that directly addresses the **stressor** by stating: 'This is your meditation about [insert stressor]. Your meditation will guide you to [insert purpose, e.g., make peace with this situation and find its value].'  
2. Help the user reflect on the **stressor**, acknowledging the emotions it evokes and inviting them to notice where those emotions manifest in their body.  
3. Reframe the user's **appraisal** of the situation by gently guiding them to see the challenge as an opportunity for growth, self-improvement, or understanding. Provide reasons to embrace the stressor rather than resist it.  
4. Address the **consequences** of the stress response by encouraging the user to visualize desired outcomes where they approach the situation with calm, focus, and clarity. Highlight how these outcomes align with their deeper goals and values.  
5. Incorporate visualization and gratitude practices to help the user foster a positive mindset and feel empowered to handle the challenge with resilience and confidence.  

The meditation should adapt seamlessly to the specific details of the stressor, appraisal, and consequences, offering empathetic, constructive, and encouraging guidance while maintaining a soothing and supportive tone."""},
                {"role": "user", "content": f"Create a meditation script based on: {user_input}"}
            ]
        )
        
        # Select a random background track
        background_track = random.choice(BACKGROUND_TRACKS)
        
        meditation_script = response.choices[0].message.content
        return jsonify({
            "script": meditation_script,
            "background_music": background_track
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
