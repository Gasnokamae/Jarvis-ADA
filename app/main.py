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
        
        # Try Ollama first with mistral model
        try:
            ollama_response = requests.post(
                f'{OLLAMA_URL}/api/generate',
                json={
                    'model': 'mistral',
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
                    'message': f'Comando procesado',
                    'response': response_text,
                    'source': 'Ollama Mistral',
                    'speak': True
                })
        except Exception as ollama_error:
            print(f'Ollama error: {ollama_error}')
        
        # Fallback to Gemini if Ollama fails
        if GEMINI_API_KEY:
            try:
                gemini_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}'
                gemini_response = requests.post(
                    gemini_url,
                    json={
                        'contents': [{
                            'parts': [{
                                'text': f'Eres Jarvis, un asistente inteligente estilo Iron Man. Responde en español de forma breve y concisa: {command}'
                            }]
                        }]
                    },
                    timeout=30
                )
                
                if gemini_response.status_code == 200:
                    result = gemini_response.json()
                    response_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sin respuesta')
                    
                    return jsonify({
                        'status': 'success',
                        'message': f'Comando procesado',
                        'response': response_text,
                        'source': 'Google Gemini',
                        'speak': True
                    })
            except Exception as gemini_error:
                print(f'Gemini error: {gemini_error}')
        
        # If both fail, return fallback response
        return jsonify({
            'status': 'success',
            'message': f'Comando recibido',
            'response': f'Entendido, "{command}". Actualmente estoy configurando los servicios de IA. En breve podré responder con más detalle.',
            'source': 'Fallback',
            'speak': True
        })
        
    except Exception as e:
        print(f'Error general: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e), 'speak': False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Jarvis-ADA',
        'ollama_url': OLLAMA_URL,
        'gemini_configured': bool(GEMINI_API_KEY)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7777))
    print(f'Starting Jarvis-ADA on port {port}')
    print(f'Ollama URL: {OLLAMA_URL}')
    print(f'Gemini API configured: {bool(GEMINI_API_KEY)}')
    app.run(host='0.0.0.0', port=port, debug=True)
