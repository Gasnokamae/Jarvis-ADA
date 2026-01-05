from flask import Flask, render_template, request, jsonify
import os
import sys
import requests
import json
from pathlib import Path

# Add modules to path
app_dir = Path(__file__).parent
sys.path.append(str(app_dir / 'modules'))

# Initialize Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    """Process voice command"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'status': 'error', 'message': 'No command provided'}), 400
        
        # Try Ollama first with llama3.2:1b model
        try:
            ollama_response = requests.post(
                f'{OLLAMA_URL}/api/generate',
                json={
                    'model': 'llama3.2:1b',
                    'prompt': f'Eres Jarvis, un asistente inteligente estilo Iron Man. Responde en español de forma breve y concisa: {command}',
                    'stream': False
                },
                timeout=30
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response_text = result.get('response', 'Sin respuesta')
                
                return jsonify({
                    'status': 'success',
                    'message': response_text,
                    'source': 'ollama'
                })
        except Exception as e:
            print(f"Ollama error: {e}")
        
        # Fallback to Gemini if Ollama fails
        if GEMINI_API_KEY:
            try:
                gemini_response = requests.post(
                    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}',
                    json={
                        'contents': [{
                            'parts': [{
                                'text': f'Eres Jarvis, un asistente inteligente estilo Iron Man. Responde en español de forma breve y concisa: {command}'
                            }]
                        }]
                    }
                )
                
                if gemini_response.status_code == 200:
                    result = gemini_response.json()
                    response_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sin respuesta')
                    
                    return jsonify({
                        'status': 'success',
                        'message': response_text,
                        'source': 'gemini'
                    })
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # If both fail, return fallback
        return jsonify({
            'status': 'success',
            'message': f'Comando recibido: {command}. Sistemas AI temporalmente no disponibles.',
            'source': 'fallback'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
