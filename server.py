from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO
import os
import base64
from datetime import datetime
import socket
from config import config

# Get environment configuration
env = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])

socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure screenshots directory exists
SCREENSHOTS_DIR = app.config['SCREENSHOTS_DIR']
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screenshots')
def list_screenshots():
    screenshots = []
    for filename in os.listdir(SCREENSHOTS_DIR):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            screenshots.append({
                'url': f'/screenshots/{filename}',
                'timestamp': datetime.fromtimestamp(os.path.getctime(os.path.join(SCREENSHOTS_DIR, filename))).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(sorted(screenshots, key=lambda x: x['timestamp'], reverse=True))

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)

@socketio.on('screenshot')
def handle_screenshot(data):
    try:
        device_info = data.get('device_info', {})
        platform = device_info.get('platform', 'unknown')
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1])
        
        # Generate filename with timestamp and device info
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{platform}_{timestamp}.png'
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_data)
            
        # Notify all clients
        socketio.emit('screenshot', {'status': 'success', 'filename': filename})
        return {'status': 'success', 'filename': filename}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    if env == 'production':
        print(f"\nRunning in PRODUCTION mode")
        socketio.run(app, 
                    host='0.0.0.0',
                    port=int(os.environ.get('PORT', 8080)),
                    debug=False)
    else:
        local_ip = get_local_ip()
        print(f"\nRunning in DEVELOPMENT mode")
        print(f"Server running at:")
        print(f"- Local: http://localhost:5000")
        print(f"- Network: http://{local_ip}:5000")
        print("\nShare these URLs with anyone who needs to take screenshots!")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
