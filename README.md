# MindFlex AI Meditation Generator

An AI-powered meditation application that creates personalized, empowering meditations in real-time, with dynamic text-to-speech streaming and background music.

## Core Features

### Meditation Generation
- Real-time, personalized meditation creation
- Automatic language detection (English/German)
- Empowerment-focused content
- Situation-specific guidance
- Dynamic placeholder system for personalization

### Audio Experience
- Streaming text-to-speech using OpenAI TTS-1
- High-quality "onyx" voice model
- Optimized voice speed (0.8x)
- Soothing background music
- Synchronized audio layers
- Precise pause timing with [Pause] tags

### User Interface
- Clean, minimalist design
- Responsive play/pause controls
- Real-time streaming feedback
- Seamless audio transitions
- Mobile-friendly layout

## Technology Stack

### AI & Language
- OpenAI GPT-3.5-turbo for meditation generation
- OpenAI TTS-1 for voice synthesis
- Custom prompt engineering for empowerment focus
- Dynamic language detection and adaptation

### Audio Processing
- MediaSource API for streaming
- Multi-threaded audio generation
- Real-time chunk processing
- Synchronized playback system
- Background music integration

### Backend
- Flask web framework
- Flask-CORS for API access
- Gunicorn WSGI server
- Python 3.11+
- Environment-based configuration

### Frontend
- Vanilla JavaScript
- HTML5 Audio API
- CSS3 animations
- Responsive design
- State management

### Deployment
- Continuous deployment via GitHub
- Render.com hosting
- Environment variable management
- Production-grade WSGI server

## Meditation Capabilities

### Language Support
- English meditations with natural flow
- German meditations with native phrasing
- Automatic language detection
- Consistent tone across languages

### Content Focus
- Situation handling strategies
- Confidence building
- Personal empowerment
- Action-oriented guidance
- Success visualization

### Audio Features
- Natural speech patterns
- Strategic pause placement
- Ambient background music
- Volume balancing
- Seamless transitions

## Security & Performance

### Security
- Secure API key management
- Environment-based configuration
- CORS protection
- Input sanitization

### Performance
- Optimized streaming
- Efficient chunk processing
- Minimal latency
- Responsive interface
- Error resilience

## Deployment

The application is automatically deployed to Render.com via GitHub integration. Updates to the main branch trigger automatic rebuilds and deployments.

## Environment Variables

Required for deployment:
- `OPENAI_API_KEY`: OpenAI API key for text and speech generation
- `FLASK_ENV`: Set to 'production' for deployment
