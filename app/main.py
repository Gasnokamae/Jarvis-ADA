from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Add modules to path
app_dir = Path(__file__).parent
sys.path.append(str(app_dir / 'modules'))

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

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
        
        # TODO: Process command with AI
        response = {
            'status': 'success',
            'message': f'Processing command: {command}',
            'response': 'Command received'
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Jarvis-ADA'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7777))
    app.run(host='0.0.0.0', port=port, debug=True)
