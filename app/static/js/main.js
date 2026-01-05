// Jarvis-ADA AI Assistant - Main JavaScript

class JarvisAssistant {
    constructor() {
        this.voiceBtn = document.getElementById('voiceBtn');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.textInput = document.getElementById('textInput');
        this.chatMessages = document.getElementById('chatMessages');
        this.status = document.getElementById('status');
        this.visualizer = document.getElementById('visualizer');
        this.isListening = false;
        this.recognition = null;
        
        this.init();
    }

    init() {
        // Text input events
        this.sendBtn.addEventListener('click', () => this.sendTextMessage());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendTextMessage();
        });

        // Voice button event
        this.voiceBtn.addEventListener('click', () => this.toggleListening());
        
        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearChat());

        // Check speech recognition support
        if (('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window)) {
            this.initSpeechRecognition();
        } else {
            this.updateStatus('Voice recognition not supported in this browser');
        }

        console.log('Jarvis-ADA Initialized');
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'es-ES';

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.addMessage(transcript, 'user');
            this.processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopListening();
        };

        this.recognition.onend = () => {
            this.stopListening();
        };
    }

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.recognition) {
            this.updateStatus('Voice recognition not available');
            return;
        }
        
        this.isListening = true;
        this.voiceBtn.classList.add('listening');
        this.visualizer.querySelector('.pulse').classList.add('listening');
        this.updateStatus('Listening...');
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.stopListening();
        }
    }

    stopListening() {
        this.isListening = false;
        this.voiceBtn.classList.remove('listening');
        this.visualizer.querySelector('.pulse').classList.remove('listening');
        this.updateStatus('Ready to assist');
        
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                // Ignore errors when stopping
            }
        }
    }

    sendTextMessage() {
        const message = this.textInput.value.trim();
        
        if (!message) return;
        
        this.addMessage(message, 'user');
        this.textInput.value = '';
        this.processCommand(message);
    }

    async processCommand(command) {
        this.updateStatus('Processing...');
        
        try {
            const response = await fetch('/api/process_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.addMessage(data.response || data.message, 'assistant');
            } else {
                this.addMessage('Error: ' + data.message, 'assistant');
            }
        } catch (error) {
            console.error('Error processing command:', error);
            this.addMessage('Error al procesar el comando', 'assistant');
        }
        
        this.updateStatus('Ready to assist');
    }

    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const p = document.createElement('p');
        p.textContent = text;
        
        messageDiv.appendChild(p);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    clearChat() {
        this.chatMessages.innerHTML = '<div class="message assistant"><p>Chat cleared. ¿En qué puedo ayudarte?</p></div>';
    }

    updateStatus(message) {
        this.status.querySelector('p').textContent = message;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new JarvisAssistant();
});
