# flask_app.py
from flask import Flask, render_template, request, jsonify, session
from northstar_chatbot import NorthstarSupportBot
from config import APP_CONFIG
from datetime import datetime
import json
import os
import requests

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = APP_CONFIG["secret_key"]
app.config['DEBUG'] = APP_CONFIG["debug"]

BACKEND_URL = os.environ.get("NORTHSTAR_BACKEND_URL", "http://127.0.0.1:8000")

# Ensure data directory exists
os.makedirs(APP_CONFIG["data_dir"], exist_ok=True)

# Initialize global bot instance
bot = NorthstarSupportBot(data_dir=APP_CONFIG["data_dir"])


@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html', config=APP_CONFIG)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        print(f"[CHAT] Received message: {user_message}")

        if not user_message:
            print("[CHAT] Message is empty")
            return jsonify({'error': 'Empty message'}), 400

        backend_payload = None
        try:
            backend_response = requests.post(
                f"{BACKEND_URL}/support/message",
                json={"customer_id": 1, "message": user_message},
                timeout=3
            )
            if backend_response.ok:
                backend_payload = backend_response.json()
                print(f"[CHAT] Backend response: {backend_payload}")
        except Exception as backend_error:
            print(f"[CHAT] Backend unavailable: {backend_error}")

        response = bot.process_message(user_message)
        if backend_payload and backend_payload.get('reply'):
            response = backend_payload.get('reply', response)

        print(f"[CHAT] Bot response: {response[:120]}...")
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'backend_used': bool(backend_payload)
        })
    except Exception as e:
        print(f"[CHAT ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get bot analytics"""
    return jsonify(bot.get_analytics())


@app.route('/api/readiness', methods=['GET'])
def get_readiness():
    """Get go-live readiness note"""
    return jsonify({'note': bot.get_golive_readiness()})


@app.route('/api/reset', methods=['POST'])
def reset_bot():
    """Reset bot session"""
    global bot
    bot = NorthstarSupportBot(data_dir=APP_CONFIG["data_dir"])
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=APP_CONFIG["debug"]
    )