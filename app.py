from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import os
import tempfile
import base64
from datetime import datetime
from faster_whisper import WhisperModel
import torch
import soundfile as sf
from voxcpm import VoxCPM
import io
import wave
import threading

# Disable torch compile to avoid CUDA graph issues in Flask
torch._dynamo.config.suppress_errors = True
os.environ['TORCH_COMPILE_DISABLE'] = '1'

# Lock for VoxCPM to avoid concurrent access issues
voxcpm_lock = threading.Lock()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAnbHxU49Nsza7bPh7eKNfVpdP1q6dLOYQ"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')

# Initialize Whisper model for speech-to-text
print("Loading Whisper model...")
whisper_model = WhisperModel("base", device="cuda" if torch.cuda.is_available() else "cpu")

# Initialize VoxCPM model for text-to-speech
print("Loading VoxCPM model...")
voxcpm_model = VoxCPM.from_pretrained("openbmb/VoxCPM1.5")

# VoxCPM reference configuration
REFERENCE_WAV = "reference_audio.wav"
REFERENCE_TRANSCRIPT = (
    "有许多人凭着自身的努力或者说幸运站在了潮头之上，在潮头之上是风光无限、诱惑无限，也风险无限，"
    "就看你如何把握了。看未来远不如看过去要来得清楚，激昂和困惑交织在每一个人的心头，"
    "要留一份敬畏在心中，看别的可以模糊，但看底线一定要清楚。"
)

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle text chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })

        # Generate AI response using Gemini
        response = gemini_model.generate_content(user_message)
        ai_message = response.text

        # Add AI response to history
        conversation_history.append({
            'role': 'assistant',
            'content': ai_message
        })

        # Generate audio for AI response using VoxCPM
        audio_base64 = generate_audio(ai_message)

        return jsonify({
            'message': ai_message,
            'audio': audio_base64
        })

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/voice', methods=['POST'])
def voice():
    """Handle voice input (audio file upload)"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        try:
            # Transcribe audio using Whisper
            segments, info = whisper_model.transcribe(temp_audio_path)
            transcription = ' '.join([segment.text for segment in segments])

            # Process as regular chat message
            conversation_history.append({
                'role': 'user',
                'content': transcription
            })

            # Generate AI response using Gemini
            response = gemini_model.generate_content(transcription)
            ai_message = response.text

            # Add AI response to history
            conversation_history.append({
                'role': 'assistant',
                'content': ai_message
            })

            # Generate audio for AI response
            audio_base64 = generate_audio(ai_message)

            return jsonify({
                'transcription': transcription,
                'message': ai_message,
                'audio': audio_base64
            })

        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)

    except Exception as e:
        print(f"Error in voice: {e}")
        return jsonify({'error': str(e)}), 500

def generate_audio(text):
    """Generate audio from text using VoxCPM"""
    try:
        # Use lock to prevent concurrent VoxCPM access (CUDA graph incompatibility)
        with voxcpm_lock:
            # Generate audio using VoxCPM with inference mode
            with torch.inference_mode():
                output_audio = voxcpm_model.generate(
                    text=text,
                    prompt_wav_path=REFERENCE_WAV,
                    prompt_text=REFERENCE_TRANSCRIPT
                )

        # Convert numpy array to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, output_audio, 44100, format='WAV')
        buffer.seek(0)

        # Convert to base64 for JSON transmission
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return audio_base64

    except Exception as e:
        import traceback
        print(f"Error generating audio: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return None

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({'history': conversation_history})

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'success': True})

if __name__ == '__main__':
    print("Starting AI Chat Server...")
    print(f"Gemini API configured")
    print(f"Whisper model: loaded")
    print(f"VoxCPM model: loaded")
    print(f"\n{'='*60}")
    print(f"🌐 Access the app at: http://207.102.87.207:53334")
    print(f"{'='*60}\n")

    # Use Waitress production server instead of Flask dev server
    from waitress import serve
    print("Starting production server with Waitress...")
    serve(app, host='0.0.0.0', port=1111, threads=1)
