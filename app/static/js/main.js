// Jarvis-ADA Voice Assistant - Main JavaScript

class JarvisAssistant {
    constructor() {
        this.voiceBtn = document.getElementById('voiceBtn');
        this.status = document.getElementById('status');
        this.response = document.getElementById('response');
        this.isListening = false;
        
        this.init();
    }
    
    init() {
        // Add event listener to voice button
        this.voiceBtn.addEventListener('click', () => this.toggleListening());
        
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.updateStatus('Voice recognition not supported in this browser');
        }
        
        console.log('Jarvis-ADA initialized');
    }
    
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    startListening() {
        this.isListening = true;
        this.voiceBtn.style.background = 'linear-gradient(135deg, #ff4444 0%, #cc0000 100%)';
        this.voiceBtn.querySelector('.btn-text').textContent = 'Listening...';
        this.updateStatus('Listening...');
        
        // TODO: Implement actual voice recognition
        console.log('Voice recognition started');
    }
    
    stopListening() {
        this.isListening = false;
        this.voiceBtn.style.background = 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)';
        this.voiceBtn.querySelector('.btn-text').textContent = 'Click to speak';
        this.updateStatus('Ready to assist');
        
        console.log('Voice recognition stopped');
    }
    
    updateStatus(message) {
        this.status.querySelector('p').textContent = message;
    }
    
    async processCommand(command) {
        try {
            this.updateStatus('Processing...');
            
            const response = await fetch('/api/process_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            const data = await response.json();
            this.displayResponse(data.response);
            this.updateStatus('Ready to assist');
            
        } catch (error) {
            console.error('Error:', error);
            this.updateStatus('Error processing command');
        }
    }
    
    displayResponse(text) {
        const p = document.createElement('p');
        p.textContent = text;
        p.style.marginBottom = '10px';
        this.response.appendChild(p);
        
        // Scroll to bottom
        this.response.scrollTop = this.response.scrollHeight;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const jarvis = new JarvisAssistant();
});
