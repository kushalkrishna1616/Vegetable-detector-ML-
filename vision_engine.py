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
    
    # New detections from user gallery
    "kiwi": {"type": "fruit", "calories": "61 kcal", "color": "Brown/Green", "price": "₹150/kg", "insight": "Full of Vitamin C and dietary fiber."},
    "papaya": {"type": "fruit", "calories": "43 kcal", "color": "Orange", "price": "₹50/kg", "insight": "Great for digestion and high in Vitamin A."},
    "pineapple": {"type": "fruit", "calories": "50 kcal", "color": "Yellow/Brown", "price": "₹80/pc", "insight": "Contains bromelain, which aids digestion."},
    "blackgrapes": {"type": "fruit", "calories": "67 kcal", "color": "Black/Purple", "price": "₹140/kg", "insight": "Rich in antioxidants and great for heart health."},
    "green_grapes": {"type": "fruit", "calories": "69 kcal", "color": "Green", "price": "₹120/kg", "insight": "Refreshing and good for hydration and energy."},
    
    # Generic fallbacks
    "fruit": {"type": "fruit", "calories": "Varies", "color": "Natural", "price": "₹50-200/kg", "insight": "Fresh fruit detected! Great for a healthy diet."},
    "vegetable": {"type": "vegetable", "calories": "Varies", "color": "Green", "price": "₹30-100/kg", "insight": "Fresh vegetable detected! Natural and healthy."},
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
                    cv2.normalize(hist, hist, 1, 0, cv2.NORM_L1)
                    # Name is filename without extension
                    name = os.path.splitext(file)[0].lower()
                    self.memory[name] = hist
        print(f"[MEMORY] Loaded {len(self.memory)} custom visual signatures.")

    def find_match(self, crop):
        if not self.memory: return None
        hsv_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        crop_hist = cv2.calcHist([hsv_crop], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(crop_hist, crop_hist, 1, 0, cv2.NORM_L1)

        best_score = 0
        best_match = None

        for name, sig_hist in self.memory.items():
            # Using Correlation AND Intersection for better accuracy
            score_correl = cv2.compareHist(crop_hist, sig_hist, cv2.HISTCMP_CORREL)
            score_intersect = cv2.compareHist(crop_hist, sig_hist, cv2.HISTCMP_INTERSECT)
            
            # Combine scores (Correlation is sensitive to shape of distro, Intersect to overlap)
            combined_score = (score_correl + score_intersect) / 2
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = name

        return best_match if best_score > 0.80 else None

class AdvancedVisionEngine:
    def __init__(self, model_path="yolov8s-oiv7.pt"): 
        print(f"[SYSTEM] Initializing Vision Engine...")
        self.model = YOLO(model_path)
        self.visual_memory = VisualMemoryEngine()
        self.last_item = "None"
        self.last_insight = "Ready to scan items."
        self.last_data = {}
        self.knowledge_base = {name: 1 for name in self.visual_memory.memory.keys()}
        self.whitelist = {"apple", "banana", "broccoli", "cabbage", "carrot", "cucumber", "grape", "mango", 
                         "mushroom", "orange", "peach", "pear", "pomegranate", "potato", "pumpkin", 
                         "strawberry", "tomato", "zucchini", "fruit", "vegetable", "watermelon", "pineapple", "kiwi", "papaya", "food"}

    def get_item_data(self, name):
        return OBJECT_DATA.get(name.lower(), {
            "type": "Matched Item", 
            "calories": "50 kcal", 
            "color": "Natural", 
            "price": "₹60/kg", 
            "insight": "High quality item from your gallery!"
        })

    def process_frame(self, frame):
        # 1. Enhance frame (Glare removal + Sharpening)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced_frame = cv2.merge((cl,a,b))
        enhanced_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_LAB2BGR)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced_frame = cv2.filter2D(enhanced_frame, -1, kernel)

        # 2. High-precision Small model (conf boosted)
        results = self.model(enhanced_frame, stream=True, conf=0.15, imgsz=640, verbose=False)
        detected_any = False
        candidates = []

        # Classes to explicitly ignore
        IGNORE_CLASSES = {"person", "man", "woman", "human", "face", "boy", "girl"}

        for res in results:
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_name = self.model.names[int(box.cls[0])].lower()
                
                # CRITICAL: If the AI thinks it's a person/face, Skip it!
                if cls_name in IGNORE_CLASSES:
                    continue
                
                if cls_name in ["goldfish", "gold fish"]: cls_name = "carrot"

                # Check visual memory match
                crop = enhanced_frame[max(0,y1):min(y2,480), max(0,x1):min(x2,640)]
                memory_match = self.visual_memory.find_match(crop) if crop.size > 0 else None
                
                # We only trust memory match if it's high quality (0.80+)
                final_name = memory_match if memory_match else cls_name
                
                # Selection logic:
                if memory_match:
                    candidates.append((x1, y1, x2, y2, final_name, conf + 1.0)) # Massive boost for gallery matches
                elif cls_name in self.whitelist:
                    candidates.append((x1, y1, x2, y2, final_name, conf))

        candidates.sort(key=lambda x: x[5], reverse=True) 
        
        seen_names = set()
        for x1, y1, x2, y2, name, c in candidates:
            if name in seen_names or name == "none": continue
            data = self.get_item_data(name)
            
            box_color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.putText(frame, name.upper(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
            
            self.last_item, self.last_insight, self.last_data, detected_any = name.capitalize(), data.get("insight"), data, True
            seen_names.add(name)
            # Removed 'break' to allow multiple detections (Carrot + Orange etc)

        if not detected_any:
            self.last_item = "None"
            self.last_insight = "Scanning items..."
        
        return frame
            
        # HUD Overlay (Minimalist)
        cv2.rectangle(frame, (0, 0), (640, 40), (30, 30, 30), -1)
        cv2.putText(frame, "VEGDETECTOR v8.0 / MEMORY_MATCH_ACTIVE", (20, 25), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (100, 215, 255), 1)
        return frame

engine = AdvancedVisionEngine()
