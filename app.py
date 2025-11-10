from flask import Flask, render_template, request, jsonify
from chatbot_core import Chatbot
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize chatbot
chatbot = Chatbot()

# --- Compatibility patch ---
# Flask 3.x removed before_first_request, so we use getattr to handle both
if hasattr(app, 'before_first_request'):
    decorator = app.before_first_request
else:
    decorator = app.before_request
# --------------------------------

@decorator
def initialize_chatbot():
    """Initialize chatbot before first request (Flask 2.x) or at startup (Flask 3.x fallback)"""
    if not chatbot.initialize():
        print("⚠️ WARNING: Failed to initialize chatbot")
    else:
        print("🤖 Chatbot initialized successfully")

@app.route('/')
def home():
    """Render home page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({
                'success': False,
                'message': 'No message provided'
            }), 400
        
        response = chatbot.process_message(user_message)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get list of available tables"""
    try:
        tables = chatbot.get_available_tables()
        return jsonify({'success': True, 'tables': tables})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database_connected': chatbot.is_connected
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
