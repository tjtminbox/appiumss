from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import base64
from datetime import datetime

app = Flask(__name__)

# Ensure screenshots directory exists
SCREENSHOTS_DIR = 'screenshots'
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)

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

@app.route('/upload', methods=['POST'])
def upload_screenshot():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove the data:image/png;base64 prefix
        device_info = data.get('device_info', {})
        
        # Generate filename with device info and timestamp
        device_type = device_info.get('type', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{device_type}_{timestamp}.png'
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
            
        return jsonify({'status': 'success', 'filename': filename})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
