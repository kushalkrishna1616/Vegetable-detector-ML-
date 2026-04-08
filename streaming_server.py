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
    return jsonify({
        "last_item": engine.last_item,
        "last_insight": engine.last_insight,
        "engine": "DeepMatch Hybrid v4.0"
    })

if __name__ == '__main__':
    print("[SERVER] Starting DeepMatch Multi-Brain Streamer on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
