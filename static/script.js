// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Voice Chat: DOM loaded, initializing...');
    initializeApp();
});

function initializeApp() {
// DOM elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const voiceBtnText = document.getElementById('voice-btn-text');
const clearBtn = document.getElementById('clear-btn');
const status = document.getElementById('status');

console.log('Elements found:', {
    chatMessages: !!chatMessages,
    messageInput: !!messageInput,
    sendBtn: !!sendBtn,
    voiceBtn: !!voiceBtn
});

// State
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Send message on Enter (Shift+Enter for new line)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendBtn.addEventListener('click', sendMessage);

// Voice button click
voiceBtn.addEventListener('click', toggleRecording);

// Clear button click
clearBtn.addEventListener('click', clearChat);

// Send text message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Disable input while processing
    setLoading(true, 'AI is thinking...');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error('Failed to get response');
        }

        const data = await response.json();

        // Add AI message to chat
        addMessage('assistant', data.message, data.audio);
        setLoading(false);

    } catch (error) {
        console.error('Error:', error);
        setStatus('Error: ' + error.message, 'error');
        setLoading(false);
    }
}

// Toggle voice recording
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        await stopRecording();
    }
}

// Start recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await sendVoiceMessage(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;

        voiceBtn.classList.add('recording');
        voiceBtnText.textContent = 'Stop';
        setStatus('Recording... Speak now', 'loading');

    } catch (error) {
        console.error('Error accessing microphone:', error);
        setStatus('Error: Could not access microphone', 'error');
    }
}

// Stop recording
async function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;

        voiceBtn.classList.remove('recording');
        voiceBtnText.textContent = 'Record';
        setStatus('Processing voice...', 'loading');
    }
}

// Send voice message
async function sendVoiceMessage(audioBlob) {
    setLoading(true, 'Processing voice...');

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('/voice', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to process voice');
        }

        const data = await response.json();

        // Add user message (transcription) to chat
        addMessage('user', data.transcription, null, true);

        // Add AI response to chat
        addMessage('assistant', data.message, data.audio);
        setLoading(false);

    } catch (error) {
        console.error('Error:', error);
        setStatus('Error: ' + error.message, 'error');
        setLoading(false);
    }
}

// Add message to chat
function addMessage(role, text, audioBase64 = null, isTranscription = false) {
    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;

    messageDiv.appendChild(contentDiv);

    // Add transcription indicator for voice messages
    if (isTranscription) {
        const transcriptionDiv = document.createElement('div');
        transcriptionDiv.className = 'transcription';
        transcriptionDiv.textContent = '(Voice message)';
        messageDiv.appendChild(transcriptionDiv);
    }

    // Add audio player if audio is provided
    if (audioBase64) {
        const audioDiv = document.createElement('div');
        audioDiv.className = 'message-audio';

        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = `data:audio/wav;base64,${audioBase64}`;

        audioDiv.appendChild(audio);
        messageDiv.appendChild(audioDiv);

        // Auto-play the AI response
        setTimeout(() => {
            audio.play().catch(e => console.log('Auto-play prevented:', e));
        }, 100);
    }

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear chat
async function clearChat() {
    if (!confirm('Are you sure you want to clear the chat history?')) {
        return;
    }

    try {
        const response = await fetch('/clear', {
            method: 'POST'
        });

        if (response.ok) {
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <p>Welcome! Start chatting by typing a message or recording your voice.</p>
                </div>
            `;
            setStatus('Chat cleared', '');
            setTimeout(() => setStatus('', ''), 2000);
        }
    } catch (error) {
        console.error('Error clearing chat:', error);
        setStatus('Error clearing chat', 'error');
    }
}

// Set loading state
function setLoading(loading, message = '') {
    sendBtn.disabled = loading;
    voiceBtn.disabled = loading;
    messageInput.disabled = loading;

    if (loading) {
        setStatus(message, 'loading');
    }
}

// Set status message
function setStatus(message, type = '') {
    status.textContent = message;
    status.className = 'status ' + type;
}

// Initialize
console.log('AI Voice Chat initialized successfully');
setStatus('Ready to chat!', '');
setTimeout(() => setStatus('', ''), 2000);

} // End of initializeApp function
