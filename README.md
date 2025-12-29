# AI Voice Chat Application

An interactive web application that lets you chat with AI using text or voice, with AI responses generated as audio using voice cloning.

## Features

- 💬 **Text Chat**: Type messages and get AI responses from Google Gemini
- 🎤 **Voice Input**: Record your voice - automatically transcribed using Whisper AI
- 🔊 **Voice Output**: AI responses are spoken in a cloned voice using VoxCPM
- 🎨 **Modern UI**: Clean, responsive interface with animations

## Quick Start

### Start the Application

```bash
./start.sh
```

Wait 30-60 seconds for models to load, then access the app at:

**Public URL:** http://207.102.87.207:53334

### Stop the Application

Press `Ctrl+C` in the terminal where the server is running.

## Manual Start

If you prefer to start manually:

```bash
# Kill any existing process on port 1111
lsof -ti:1111 | xargs kill -9 2>/dev/null

# Start the server
python app.py
```

## System Requirements

- Python 3.11+
- CUDA-compatible GPU (for fast inference)
- Required packages (already installed):
  - Flask, Flask-CORS
  - google-generativeai (Gemini API)
  - faster-whisper (speech-to-text)
  - voxcpm (voice cloning)
  - torch, soundfile, etc.

## How to Use

1. Open http://207.102.87.207:53526 in your web browser
2. **For text chat**: Type your message and click "Send"
3. **For voice chat**: Click "Record", speak, then click "Stop"
4. The AI will respond with both text and audio
5. Click "Clear" to reset the conversation

## Technical Details

- **AI Model**: Google Gemini 2.5 Flash
- **Speech-to-Text**: Faster Whisper (base model, CUDA)
- **Text-to-Speech**: VoxCPM 1.5 (voice cloning)
- **Reference Voice**: gaoyuliang.MP3 → reference_audio.wav
- **Server**: Flask on port 1111 → public port 53334 (single-threaded for CUDA compatibility)

## Project Structure

```
/workspace/
├── start.sh              # Startup script
├── app.py                # Flask application
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
├── reference_audio.wav   # Reference voice for cloning
└── gaoyuliang.MP3        # Original reference voice
```

## Troubleshooting

**Server won't start:**
- Make sure port 8080 is available
- Check if models are downloaded (first run takes longer)

**No audio output:**
- Allow audio permissions in your browser
- Check browser console for errors

**Voice recording doesn't work:**
- Allow microphone permissions in your browser
- Use Chrome/Edge for best compatibility

## API Endpoints

- `GET /` - Web interface
- `POST /chat` - Send text message
- `POST /voice` - Upload voice recording
- `GET /history` - Get conversation history
- `POST /clear` - Clear conversation

---

Built with Flask, Gemini, Whisper, and VoxCPM
