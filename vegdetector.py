import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
import os

# --- PREMIUM CONFIGURATION (INDIAN RUPEE EDITION) ---
THEME_GOLD = (100, 215, 255)  
THEME_SLATE = (45, 45, 45)    
THEME_TEXT = (255, 255, 255)  
THEME_NEON = (57, 255, 20)    

# Mapping classes to their expected dominant colors (HSV Range)
# Lower, Upper bounds for H (Hue is 0-180 in OpenCV)
COLOR_MAP = {
    "red": [((0, 70, 50), (10, 255, 255)), ((160, 70, 50), (180, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "orange": [((10, 100, 100), (25, 255, 255))],
    "green": [((35, 40, 40), (85, 255, 255))],
}

# Validation logic: Which class must be which color
CLASS_COLORS = {
    "apple": "red",
    "tomato": "red",
    "strawberry": "red",
    "banana": "yellow",
    "mango": "orange", # Mangoes are often more orange/yellow
    "lemon": "yellow",
    "orange": "orange",
    "broccoli": "green",
    "cucumber": "green",
    "cabbage": "green",
    "zucchini": "green",
}

VALID_CLASSES = [
    "apple", "banana", "bell pepper", "broccoli", "cabbage", "carrot", 
    "cucumber", "lemon", "mango", "mushroom", "orange", "pear", "pineapple", 
    "pomegranate", "potato", "pumpkin", "strawberry", "tomato", "watermelon", "zucchini"
]

OBJECT_DATA = {
    "apple": {"info": "Fresh Gala", "price": "₹150/kg", "insight": "Apples are high in fiber and Vitamin C."},
    "banana": {"info": "Robusta", "price": "₹60/doz", "insight": "High in potassium for energy."},
    "orange": {"info": "Nagpur", "price": "₹80/kg", "insight": "Packed with Vitamin C for immunity."},
    "carrot": {"info": "Organic", "price": "₹40/kg", "insight": "Excellent for eye health (Vitamin A)."},
    "tomato": {"info": "Hybrid", "price": "₹30/kg", "insight": "Rich in Lycopene and antioxidants."},
    "mango": {"info": "Alphonso", "price": "₹600/box", "insight": "The King of Fruits, rich in Vitamin A."},
    "strawberry": {"info": "Fresh", "price": "₹100/pkt", "insight": "Low calorie antioxidant powerhouse."},
    "lemon": {"info": "Citrus", "price": "₹5/pc", "insight": "Aids digestion and detoxification."},
    "broccoli": {"info": "Green", "price": "₹120/kg", "insight": "Superfood rich in Vitamin K."},
    "cucumber": {"info": "Hydrating", "price": "₹40/kg", "insight": "95% water for hydration."},
    # ... more added implicitly below
}

CLASS_REMAP = {"goldfish": "carrot", "gold fish": "carrot"}

class PremiumDetector:
    def __init__(self, model_path="yolov8s-oiv7.pt"):
        print(f"[SYSTEM] Initializing AI Engine with Color-Verification Logic...")
        self.model = YOLO(model_path)
        self.fps = 0
        self.start_time = time.time()
        self.frame_count = 0
        self.last_item = "None"
        self.last_insight = "Place an item in view."

    def get_dominant_color(self, crop):
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        results = {}
        for color_name, ranges in COLOR_MAP.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for (lower, upper) in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))
            results[color_name] = np.sum(mask > 0)
        
        # Return the color with the most masked pixels
        dominant = max(results, key=results.get)
        # If very few pixels matched, return 'unknown'
        if results[dominant] < (crop.shape[0] * crop.shape[1] * 0.1):
            return "unknown"
        return dominant

    def validate_detection(self, cls_name, crop):
        expected = CLASS_COLORS.get(cls_name)
        if not expected: return True # No color rule for this class
        
        dominant = self.get_dominant_color(crop)
        
        # LOGIC: If it's Yellow and model says Tomato (Red), it's likely a misclassification
        if expected == "red" and dominant == "yellow":
            # Switch to Banana or Mango if likely
            return False 
        if expected == "yellow" and dominant == "red":
            return False
            
        return True

    def draw_hud(self, frame, status_text="SCANNING"):
        h, w, _ = frame.shape
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), THEME_SLATE, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "KUSHALZZ SMART AI VISION", (20, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.7, THEME_GOLD, 1)
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"FPS: {self.fps:.1f} | {timestamp}", (w-200, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, THEME_GOLD, 1)

    def draw_glass_box(self, frame, x1, y1, x2, y2, name, conf, data):
        color = THEME_GOLD
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{name.upper()} {conf:.0%}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, THEME_NEON, 2)
        cv2.putText(frame, f"{data.get('price', 'TBD')}", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, THEME_GOLD, 1)

    def run(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            self.frame_count += 1
            if self.frame_count % 10 == 0:
                self.fps = 10 / (time.time() - self.start_time)
                self.start_time = time.time()

            results = self.model(frame, stream=True, conf=0.15, imgsz=416, verbose=False)
            detected_any = False
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    name = self.model.names[cls_id].lower()
                    name = CLASS_REMAP.get(name, name)
                    if name not in VALID_CLASSES: continue
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Crop and Verify Color
                    crop = frame[max(0, y1):y2, max(0, x1):x2]
                    if crop.size == 0: continue
                    
                    if not self.validate_detection(name, crop):
                        # Special re-classification for Banana/Tomato confusion
                        found_color = self.get_dominant_color(crop)
                        if found_color == "yellow" and name == "tomato":
                            name = "banana" # Fix for the common misclassification seen
                        else:
                            continue # Discard shaky prediction

                    conf = float(box.conf[0])
                    data = OBJECT_DATA.get(name, {"info": "Fresh", "price": "₹40/kg", "insight": "Good for health."})
                    self.draw_glass_box(frame, x1, y1, x2, y2, name, conf, data)
                    self.last_item, self.last_insight, detected_any = name.capitalize(), data.get("insight"), True

            if not detected_any: self.last_item = "None"
            self.draw_hud(frame)
            cv2.imshow("KUSHALZZ AI", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release()

if __name__ == "__main__":
    PremiumDetector().run()
