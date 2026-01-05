from flask import Flask, render_template, request, jsonify
import os
import sys
import requests
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
        
        # Try Ollama first
        try:
            ollama_response = requests.post(
                f'{OLLAMA_URL}/api/generate',
                json={
                    'model': 'llama3.2',
                    'prompt': f'Eres Jarvis, un asistente inteligente. Responde en español: {command}',
                    'stream': False
                },
                timeout=10
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response_text = result.get('response', 'No response')
                
                return jsonify({
                    'status': 'success',
                    'message': f'Procesando: {command}',
                    'response': response_text,
                    'source': 'Ollama'
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
                                    'text': f'Eres Jarvis, un asistente inteligente. Responde en español de forma concisa: {command}'
                                }]
                            }]
                        },
                        timeout=10
                    )
                    
                    if gemini_response.status_code == 200:
                        result = gemini_response.json()
                        response_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sin respuesta')
                        
                        return jsonify({
                            'status': 'success',
                            'message': f'Procesando: {command}',
                            'response': response_text,
                            'source': 'Gemini'
                        })
                except Exception as gemini_error:
                    print(f'Gemini error: {gemini_error}')
            
            # If both fail, return mock response
            return jsonify({
                'status': 'success',
                'message': f'Procesando: {command}',
                'response': f'Comando recibido: "{command}". Los servicios de IA están temporalmente no disponibles.',
                'source': 'Mock'
            })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Jarvis-ADA'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7777))
    app.run(host='0.0.0.0', port=port, debug=True)
