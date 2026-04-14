import cv2
import numpy as np
from ultralytics import YOLO
import os
import time

# --- CONFIGURATION ---
VEGETABLE_DIR = "vegetable"
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
}

class VisualMemoryEngine:
    """Matches live camera frames against images in the 'vegetable' folder."""
    def __init__(self, gallery_path=VEGETABLE_DIR):
        self.gallery_path = gallery_path
        self.memory = {}
        self.load_memory()

    def load_memory(self):
        if not os.path.exists(self.gallery_path):
            os.makedirs(self.gallery_path)
            return

        print(f"[MEMORY] Learning from {self.gallery_path} folder...")
        for file in os.listdir(self.gallery_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(self.gallery_path, file)
                img = cv2.imread(img_path)
                if img is not None:
                    # Use color histogram as a visual signature
                    hist = cv2.calcHist([cv2.cvtColor(img, cv2.COLOR_BGR2HSV)], [0, 1], None, [180, 256], [0, 180, 0, 256])
                    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                    # Name is filename without extension
                    name = os.path.splitext(file)[0].lower()
                    self.memory[name] = hist
        print(f"[MEMORY] Loaded {len(self.memory)} custom visual signatures.")

    def find_match(self, crop):
        if not self.memory: return None
        hsv_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        crop_hist = cv2.calcHist([hsv_crop], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(crop_hist, crop_hist, 0, 1, cv2.NORM_MINMAX)

        best_score = 0
        best_match = None

        for name, sig_hist in self.memory.items():
            score = cv2.compareHist(crop_hist, sig_hist, cv2.HISTCMP_CORREL)
            if score > best_score:
                best_score = score
                best_match = name

        return best_match if best_score > 0.85 else None

class AdvancedVisionEngine:
    def __init__(self, model_path="yolov8n-oiv7.pt"): 
        print(f"[SYSTEM] Initializing Vision Engine...")
        self.model = YOLO(model_path)
        self.visual_memory = VisualMemoryEngine()
        self.last_item = "None"
        self.last_insight = "Ready to scan items."
        self.last_data = {}

    def get_item_data(self, name):
        return OBJECT_DATA.get(name.lower(), {
            "type": "Matched Item", 
            "calories": "50 kcal", 
            "color": "Natural", 
            "price": "₹60/kg", 
            "insight": "High quality item from your gallery!"
        })

    def process_frame(self, frame):
        # Sensitive mode for diverse environments
        results = self.model(frame, stream=True, conf=0.15, imgsz=640, verbose=False)
        detected_any = False
        
        for res in results:
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_name = self.model.names[int(box.cls[0])].lower()
                
                # Check visual memory first (User's folder)
                crop = frame[max(0,y1):min(y2,480), max(0,x1):min(x2,640)]
                memory_match = self.visual_memory.find_match(crop) if crop.size > 0 else None
                
                final_name = memory_match if memory_match else cls_name
                
                # STRICT GOAL MODE: Only show if it's a fruit/veg or memory match
                is_known = final_name.lower() in OBJECT_DATA or memory_match
                
                if is_known:
                    data = self.get_item_data(final_name)
                    box_color = (0, 255, 0) # Clear Green
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                    label = f"{final_name.upper()}"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
                    
                    self.last_item = final_name.capitalize()
                    self.last_insight = data.get("insight")
                    self.last_data = data
                    detected_any = True

        if not detected_any:
            self.last_item = "None"
            self.last_insight = "Scanning items..."
            
        # HUD Overlay (Minimalist)
        cv2.rectangle(frame, (0, 0), (640, 40), (30, 30, 30), -1)
        cv2.putText(frame, "VEGDETECTOR v8.0 / MEMORY_MATCH_ACTIVE", (20, 25), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (100, 215, 255), 1)
        return frame

engine = AdvancedVisionEngine()
