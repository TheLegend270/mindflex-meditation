# AI Meditation Generator

A web application that creates personalized meditation experiences using AI-generated scripts and text-to-speech technology.

## Features

- Generate custom meditation scripts based on user input
- Text-to-speech playback with play, pause, and stop controls
- Clean, modern interface with a calming design
- Powered by OpenAI's GPT-3.5 for script generation

## Setup

1. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter your meditation preferences or topic in the text area
2. Click "Generate Meditation" to create a personalized meditation script
3. Use the playback controls to start, pause, or stop the meditation

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- AI: OpenAI GPT-3.5
- Audio: Web Speech API
