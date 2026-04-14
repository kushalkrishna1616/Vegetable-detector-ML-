from flask import Flask, Response, jsonify
import cv2
import numpy as np
from vision_engine import engine
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Multi-Brain Processing
            frame = engine.process_frame(frame)
            
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    item_name = engine.last_item
    data = engine.get_item_data(item_name.lower())
    learned = engine.knowledge_base.get(item_name.lower(), 0)
    return jsonify({
        "last_item": item_name,
        "last_insight": engine.last_insight,
        "price": data.get("price", "₹0"),
        "calories": data.get("calories", "0 kcal"),
        "type": data.get("type", "Fresh"),
        "color": data.get("color", "N/A"),
        "learned_samples": learned,
        "engine": "Kushalzz Premium Hybrid v5.0"
    })

@app.route('/knowledge')
def get_knowledge():
    return jsonify(engine.knowledge_base)

if __name__ == '__main__':
    print("[SERVER] Starting DeepMatch Multi-Brain Streamer on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
