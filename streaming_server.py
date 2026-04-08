from flask import Flask, render_template, Response
import cv2
from vegdetector import PremiumDetector, CLASS_REMAP, OBJECT_DATA, THEME_GOLD, THEME_SLATE, THEME_NEON
import time

app = Flask(__name__)
detector = PremiumDetector()

def gen_frames():
    cap = cv2.VideoCapture(0)
    # Set to 720p for quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Process frame using the detector's logic
            results = detector.model(frame, stream=True, conf=0.20, verbose=False)
            person_count = 0
            
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    raw_name = detector.model.names[cls_id].lower()
                    cls_name = CLASS_REMAP.get(raw_name, raw_name)
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    if "person" in cls_name:
                        person_count += 1
                        
                    data = OBJECT_DATA.get(cls_name, {"info": f"Cat: {cls_name.capitalize()}", "price": "TBD", "calories": "N/A"})
                    detector.draw_glass_box(frame, x1, y1, x2, y2, cls_name, conf, data)
            
            detector.draw_hud(frame, person_count, "WEB STREAM ACTIVE")
            
            # Encode for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "AI Vision Stream Active at /video_feed"

if __name__ == '__main__':
    print("[SERVER] Starting Flask Streamer on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
