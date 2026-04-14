import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
from datetime import datetime

# --- PREMIUM CONFIGURATION ---
THEME_GOLD = (100, 215, 255)
THEME_NEON = (57, 255, 20)
THEME_SLATE = (45, 45, 45)

# Mapping classes to their expected dominant colors (HSV Range)
COLOR_MAP = {
    "red": [((0, 70, 50), (10, 255, 255)), ((160, 70, 50), (180, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "orange": [((10, 100, 100), (25, 255, 255))],
    "green": [((35, 40, 40), (85, 255, 255))],
}

CLASS_COLORS = {
    "apple": "red",
    "tomato": "red",
    "strawberry": "red",
    "banana": "yellow",
    "mango": "orange",
    "lemon": "yellow",
    "orange": "orange",
    "broccoli": "green",
    "cucumber": "green",
    "cabbage": "green",
    "zucchini": "green",
    "bell pepper": "green",
    "carrot": "orange",
    "watermelon": "green",
    "grape": "green",
    "pear": "green",
    "pomegranate": "red",
    "peach": "orange",
    "potato": "brown",
    "mushroom": "white",
    "pumpkin": "orange",
}

CLASS_REMAP = {
    "goldfish": "carrot", 
    "gold fish": "carrot",
    "sports ball": "tomato",
}

# Visual Knowledge Base
GALLERY_DIR = "gallery"

OBJECT_DATA = {
    # Fruit - 10
    "apple": {"type": "fruit", "calories": "52 kcal", "color": "Red/Green", "price": "₹150/kg", "insight": "Apples are rich in fiber and keep the heart healthy."},
    "banana": {"type": "fruit", "calories": "89 kcal", "color": "Yellow", "price": "₹60/doz", "insight": "Great for energy and packed with potassium."},
    "mango": {"type": "fruit", "calories": "60 kcal", "color": "Orange/Yellow", "price": "₹600/box", "insight": "The King of Fruits, loaded with Vitamin A."},
    "orange": {"type": "fruit", "calories": "47 kcal", "color": "Orange", "price": "₹80/kg", "insight": "High in Vitamin C to boost your immunity."},
    "strawberry": {"type": "fruit", "calories": "33 kcal", "color": "Red", "price": "₹100/pkt", "insight": "Berries are great for skin and brain health."},
    "grape": {"type": "fruit", "calories": "69 kcal", "color": "Green/Purple", "price": "₹120/kg", "insight": "Contain antioxidants called polyphenols."},
    "pear": {"type": "fruit", "calories": "57 kcal", "color": "Green", "price": "₹160/kg", "insight": "Highly nutritional and easy to digest."},
    "pomegranate": {"type": "fruit", "calories": "83 kcal", "color": "Dark Red", "price": "₹200/kg", "insight": "Great for blood health and circulation."},
    "watermelon": {"type": "fruit", "calories": "30 kcal", "color": "Green", "price": "₹40/kg", "insight": "92% water, perfect for hydration!"},
    "peach": {"type": "fruit", "calories": "39 kcal", "color": "Peach/Orange", "price": "₹180/kg", "insight": "Contains Vitamin C and helps skin health."},

    # Vegetables - 10
    "broccoli": {"type": "vegetable", "calories": "34 kcal", "color": "Green", "price": "₹120/kg", "insight": "A superfood high in Vitamin K and fiber."},
    "carrot": {"type": "vegetable", "calories": "41 kcal", "color": "Orange", "price": "₹40/kg", "insight": "Great for your eyes and overall vision."},
    "tomato": {"type": "vegetable", "calories": "18 kcal", "color": "Red", "price": "₹30/kg", "insight": "Rich in Lycopene, great for skin health."},
    "cucumber": {"type": "vegetable", "calories": "15 kcal", "color": "Green", "price": "₹40/kg", "insight": "Keeps you cool and hydrated."},
    "potato": {"type": "vegetable", "calories": "77 kcal", "color": "Brown", "price": "₹25/kg", "insight": "An energy-rich staple food worldwide."},
    "bell pepper": {"type": "vegetable", "calories": "31 kcal", "color": "Multi", "price": "₹80/kg", "insight": "Crunchy and rich in Vitamin C."},
    "cabbage": {"type": "vegetable", "calories": "25 kcal", "color": "Green/Purple", "price": "₹30/pc", "insight": "Low in calories, high in vitamins."},
    "zucchini": {"type": "vegetable", "calories": "17 kcal", "color": "Green", "price": "₹60/kg", "insight": "Great for weight loss and digestion."},
    "mushroom": {"type": "vegetable", "calories": "22 kcal", "color": "White/Brown", "price": "₹50/pkt", "insight": "A great source of B vitamins and selenium."},
    "pumpkin": {"type": "vegetable", "calories": "26 kcal", "color": "Orange", "price": "₹40/kg", "insight": "Rich in beta-carotene and antioxidants."},
    
    # Extra fallback
    "cauliflower": {"type": "vegetable", "calories": "25 kcal", "color": "White", "price": "₹40/pc", "insight": "High in fiber and Vitamin C."},
    "lemon": {"type": "citrus", "calories": "29 kcal", "color": "Yellow", "price": "₹5/pc", "insight": "Aids digestion and detoxification."},
}

class AdvancedVisionEngine:
    def __init__(self, model_path="yolov8n-oiv7.pt"): 
        print(f"[SYSTEM] Initializing Premium Vision Engine ({model_path})...")
        self.model = YOLO(model_path)
        self.last_item = "None"
        self.last_insight = "Ready to scan items."
        self.last_data = {}
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self):
        kb = {}
        if os.path.exists(GALLERY_DIR):
            for class_name in os.listdir(GALLERY_DIR):
                class_path = os.path.join(GALLERY_DIR, class_name)
                if os.path.isdir(class_path):
                    kb[class_name.lower()] = len(os.listdir(class_path))
        return kb

    def get_item_data(self, name):
        return OBJECT_DATA.get(name.lower(), {"type": "unknown", "calories": "0", "color": "unknown", "price": "₹0", "insight": "Unknown item."})

    def get_dominant_color(self, crop):
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        results = {}
        for color_name, ranges in COLOR_MAP.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for (lower, upper) in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))
            results[color_name] = np.sum(mask > 0)
        
        dominant = max(results, key=results.get)
        if results[dominant] < (crop.shape[0] * crop.shape[1] * 0.1):
            return "unknown"
        return dominant

    def validate_detection(self, name, crop):
        expected = CLASS_COLORS.get(name)
        if not expected: return True
        
        dominant = self.get_dominant_color(crop)
        # Fix common mis-classifications based on color
        if expected == "red" and dominant == "yellow" and name == "tomato":
            return "banana" # Switch
        if expected == "yellow" and dominant == "red" and name == "banana":
            return "tomato" # Switch
            
        return True # Soft validation for now to avoid missing detections

    def process_frame(self, frame):
        # SENSITIVE MODE: HD(640), Sensitive(0.15)
        results = self.model(frame, stream=True, conf=0.15, imgsz=640, verbose=False)
        detected_any = False
        
        for res in results:
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_name = self.model.names[int(box.cls[0])].lower()
                
                # RE-MAP certain things for accuracy
                cls_name = CLASS_REMAP.get(cls_name, cls_name)

                # STRICT WHITELIST: Only show what the user asked for
                is_item = cls_name in OBJECT_DATA
                is_context = cls_name in ["human face", "clothing"]
                
                # EXPLICITLY SKIP 'MAN' AND 'WOMAN'
                if cls_name in ["man", "woman"] or (not is_item and not is_context):
                    continue

                # Categories: Green for Items, Blue for Context
                data = self.get_item_data(cls_name)
                box_color = (0, 255, 0) if is_item else (235, 206, 135) 
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                label = f"{cls_name.upper()} {int(conf*100)}%"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)
                
                if is_item:
                    self.last_item = cls_name.capitalize()
                    self.last_insight = data.get("insight")
                    self.last_data = data
                    detected_any = True

        if not detected_any:
            self.last_item = "None"
            self.last_insight = "Scanning for items..."
            
        cv2.rectangle(frame, (0, 0), (640, 40), THEME_SLATE, -1)
        cv2.putText(frame, "VEGDETECTOR v8.0 / RELOADED / PAY_STATION", (20, 25), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (100, 215, 255), 1)
        return frame

engine = AdvancedVisionEngine()

