from flask import Flask, Response, jsonify
import cv2
from vegdetector import PremiumDetector, CLASS_REMAP, OBJECT_DATA, THEME_GOLD, THEME_SLATE, THEME_NEON, VALID_CLASSES
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

# Global detector instance using Nano model
detector = PremiumDetector("yolov8n-oiv7.pt")

def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Low complexity inference for speed
            results = detector.model(frame, stream=True, conf=0.25, imgsz=320, verbose=False)
            detected_any = False

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    raw_name = detector.model.names[cls_id].lower()
                    cls_name = CLASS_REMAP.get(raw_name, raw_name)
                    
                    # FILTER: Only show Fruits and Veggies
                    if cls_name not in VALID_CLASSES:
                        continue

                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    data = OBJECT_DATA.get(cls_name, {"info": f"Fresh {cls_name.capitalize()}", "price": "₹40/kg", "insight": f"Add {cls_name} to your daily diet for health."})
                    detector.draw_glass_box(frame, x1, y1, x2, y2, cls_name, conf, data)
                    
                    # Store for API
                    detector.last_item = cls_name.capitalize()
                    detector.last_insight = data.get("insight")
                    detected_any = True
            
            detector.draw_hud(frame, "ACTIVE" if detected_any else "SCANNING")
            
            # Reduce JPEG quality slightly for better streaming performance
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    return jsonify({
        "last_item": detector.last_item,
        "last_insight": detector.last_insight,
        "currency": "INR"
    })

@app.route('/')
def index():
    return "AI Vision Streamer (Nano Optimized) Running..."

if __name__ == '__main__':
    print("[SERVER] Starting Specialized Fruit/Veg Streamer on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
