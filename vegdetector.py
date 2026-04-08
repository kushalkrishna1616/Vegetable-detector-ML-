import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime

# --- PREMIUM CONFIGURATION ---
THEME_GOLD = (100, 215, 255)  # Soft Gold (BGR)
THEME_SLATE = (45, 45, 45)    # Deep Slate
THEME_TEXT = (255, 255, 255)  # Off-White
THEME_NEON = (57, 255, 20)    # Neon Green for high confidence

# Object features with enriched nutrition data & pricing
OBJECT_DATA = {
    "bottle": {"info": "Volume: 1L | Recyclable", "price": "$1.50", "calories": "0 kcal"},
    "apple": {"info": "Fresh Gala | Vitamin C", "price": "$0.75", "calories": "52 kcal/100g"},
    "banana": {"info": "Organic Cavendish", "price": "$0.30", "calories": "89 kcal/100g"},
    "orange": {"info": "Valencia | Citrus", "price": "$0.90", "calories": "47 kcal/100g"},
    "carrot": {"info": "Deep Orange | Vitamin A", "price": "$0.40", "calories": "41 kcal/100g"},
    "broccoli": {"info": "Cruciferous | Fiber", "price": "$1.20", "calories": "34 kcal/100g"},
    "tomato": {"info": "Vine-Ripened | Lycopene", "price": "$0.50", "calories": "18 kcal/100g"},
    "potato": {"info": "Russet | High Starch", "price": "$0.20", "calories": "77 kcal/100g"},
    "onion": {"info": "Red Onion | Flavor Base", "price": "$0.15", "calories": "40 kcal/100g"},
    "mango": {"info": "Alphonso | Vitamin A, C", "price": "$2.00", "calories": "60 kcal/100g"},
    "pineapple": {"info": "Tropical Gold", "price": "$3.50", "calories": "50 kcal/100g"},
    "cucumber": {"info": "Seedless | Hydrating", "price": "$0.80", "calories": "15 kcal/100g"},
    "bell pepper": {"info": "Triple Pack | Vitamin C", "price": "$1.10", "calories": "20 kcal/100g"},
    "strawberry": {"info": "Local | Antioxidants", "price": "$4.50", "calories": "32 kcal/100g"},
    "cabbage": {"info": "Green | Vitamin K", "price": "$1.00", "calories": "25 kcal/100g"},
    "spinach": {"info": "Baby Leaves | Iron", "price": "$2.50", "calories": "23 kcal/100g"},
    "garlic": {"info": "Organic | Allicin", "price": "$0.10", "calories": "149 kcal/100g"},
    "ginger": {"info": "Root | Digestion", "price": "$0.50", "calories": "80 kcal/100g"},
    "zucchini": {"info": "Summer Squash", "price": "$0.95", "calories": "17 kcal/100g"},
    "eggplant": {"info": "Globe Brinjals", "price": "$1.40", "calories": "25 kcal/100g"},
    "pumpkin": {"info": "Pantry Staple", "price": "$5.00", "calories": "26 kcal/100g"},
    "lettuce": {"info": "Romaine Heart", "price": "$1.50", "calories": "15 kcal/100g"},
    "cauliflower": {"info": "White Florets", "price": "$2.75", "calories": "25 kcal/100g"},
    "mushroom": {"info": "Button | B-Vitamins", "price": "$3.00", "calories": "22 kcal/100g"},
    "corn": {"info": "Sweet Corn", "price": "$0.60", "calories": "86 kcal/100g"},
    "person": {"info": "Customer Registered", "price": "N/A", "calories": "N/A"}
}

# --- FIX: Misclassification mapping for common OIV7 errors ---
CLASS_REMAP = {
    "goldfish": "carrot",
    "gold fish": "carrot",
    "man": "person", 
    "woman": "person",
    "boy": "person",
    "girl": "person"
}

class PremiumDetector:
    def __init__(self, model_path="yolov8s-oiv7.pt"):
        print(f"[SYSTEM] Initializing AI Engine with {model_path}...")
        self.model = YOLO(model_path)
        self.history = []
        self.fps = 0
        self.start_time = time.time()
        self.frame_count = 0

    def draw_hud(self, frame, person_count, status_text="SCANNING READY"):
        h, w, _ = frame.shape
        
        # Upper Dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), THEME_SLATE, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Branding
        cv2.putText(frame, "KUSHALZZ AI VISION v2.0", (20, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.7, THEME_GOLD, 2)
        
        # Status & Stats
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"FPS: {self.fps:.1f} | {timestamp}", (w - 220, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, THEME_GOLD, 1)
        
        # Lower Console
        cv2.rectangle(frame, (10, h - 40), (250, h - 10), THEME_SLATE, -1)
        cv2.putText(frame, f"STATUS: {status_text}", (20, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, THEME_NEON, 1)
        cv2.putText(frame, f"QUEUE: {len(self.history)} ITEMS", (w - 200, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, THEME_GOLD, 1)

    def draw_glass_box(self, frame, x1, y1, x2, y2, name, conf, data):
        # Premium Bounding Box (L-Cuts)
        color = THEME_GOLD if "person" not in name else (255, 100, 100)
        thickness = 2
        l = 25 # line length
        
        # Draw Corners
        cv2.line(frame, (x1, y1), (x1 + l, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + l), color, thickness)
        cv2.line(frame, (x2, y1), (x2 - l, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + l), color, thickness)
        cv2.line(frame, (x1, y2), (x1 + l, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - l), color, thickness)
        cv2.line(frame, (x2, y2), (x2 - l, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - l), color, thickness)

        # Translucent Label
        lbl_h = 60
        sub_overlay = frame.copy()
        cv2.rectangle(sub_overlay, (x1, y1 - lbl_h), (x1 + 220, y1), THEME_SLATE, -1)
        cv2.addWeighted(sub_overlay, 0.5, frame, 0.5, 0, frame)
        
        # Text details
        cv2.putText(frame, f"{name.upper()} {conf:.0%}", (x1 + 10, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, THEME_GOLD, 2)
        cv2.putText(frame, data.get("info", "N/A"), (x1 + 10, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(frame, f"PRICE: {data.get('price', '$0.00')} | {data.get('calories', '0 kcal')}", (x1 + 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, THEME_NEON, 1)

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            self.frame_count += 1
            if self.frame_count % 10 == 0:
                curr_time = time.time()
                self.fps = 10 / (curr_time - self.start_time)
                self.start_time = curr_time

            # Detection
            results = self.model(frame, stream=True, conf=0.20, verbose=False)
            
            person_count = 0
            current_detections = []

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    raw_name = self.model.names[cls_id].lower()
                    
                    # Remap
                    cls_name = CLASS_REMAP.get(raw_name, raw_name)
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    if "person" in cls_name:
                        person_count += 1
                    
                    data = OBJECT_DATA.get(cls_name, {"info": f"Cat: {cls_name.capitalize()}", "price": "TBD", "calories": "N/A"})
                    self.draw_glass_box(frame, x1, y1, x2, y2, cls_name, conf, data)
                    
                    if conf > 0.6 and cls_name not in [d['name'] for d in current_detections]:
                        current_detections.append({"name": cls_name, "time": time.time()})

            self.draw_hud(frame, person_count, "ACTIVE VISION" if current_detections else "IDLE SCANNING")

            cv2.imshow("KUSHALZZ AI - SMART CHECKOUT", frame)
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            elif key & 0xFF == ord('s'):
                # Snapshot / Save detection
                print(f"[LOG] Saving session state with {len(current_detections)} items.")

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = PremiumDetector()
    detector.run()
