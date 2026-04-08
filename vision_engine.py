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

# Visual Knowledge Base (User can drop any photo here to "Teach" the AI)
GALLERY_DIR = "gallery"

OBJECT_DATA = {
    "cauliflower": {"info": "Cruciferous", "price": "₹40/pc", "insight": "High in fiber and Vitamin C."},
    "dragonfruit": {"info": "Tropical Pitaya", "price": "₹120/pc", "insight": "Rich in antioxidants and magnesium."},
    "mango": {"info": "Alphonso", "price": "₹600/box", "insight": "Rich in Vitamin A."},
    "tomato": {"info": "Vegetable", "price": "₹30/kg", "insight": "Packed with Lycopene."},
    "strawberry": {"info": "Berries", "price": "₹100/pkt", "insight": "Low in calories, high in flavor."},
    "banana": {"info": "Fruit", "price": "₹60/doz", "insight": "Great for energy and potassium."}
}

class AdvancedVisionEngine:
    def __init__(self, model_path="yolov8s-oiv7.pt"):
        print("[SYSTEM] Initializing Multi-Brain Engine (CNN + Feature Matching)...")
        self.model = YOLO(model_path)
        self.orb = cv2.ORB_create(nfeatures=500)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.gallery_features = {}
        self.load_gallery()
        self.last_item = "None"
        self.last_insight = "Scan anything (Fruits/Veg) for AI analysis."

    def load_gallery(self):
        """Pre-load visual features of reference photos from the gallery folder."""
        if not os.path.exists(GALLERY_DIR): return
        for category in os.listdir(GALLERY_DIR):
            cat_path = os.path.join(GALLERY_DIR, category)
            if not os.path.isdir(cat_path): continue
            
            self.gallery_features[category] = []
            for img_file in os.listdir(cat_path):
                img_path = os.path.join(cat_path, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None: continue
                # Resize for consistency
                img = cv2.resize(img, (300, 300))
                kp, des = self.orb.detectAndCompute(img, None)
                if des is not None:
                    self.gallery_features[category].append(des)
        print(f"[GALLERY] Loaded {len(self.gallery_features)} reference categories.")

    def match_item(self, crop):
        """Compare a detected crop against the custom photo library."""
        if not self.gallery_features: return None
        gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray_crop = cv2.resize(gray_crop, (300, 300))
        kp_q, des_q = self.orb.detectAndCompute(gray_crop, None)
        if des_q is None: return None

        best_match = None
        max_matches = 0
        
        for category, ref_descriptors in self.gallery_features.items():
            for des_ref in ref_descriptors:
                matches = self.matcher.match(des_q, des_ref)
                good_matches = len([m for m in matches if m.distance < 50])
                if good_matches > max_matches:
                    max_matches = good_matches
                    best_match = category
        
        return best_match if max_matches > 15 else None

    def draw_hud(self, frame, status):
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 50), THEME_SLATE, -1)
        cv2.putText(frame, f"AI ENGINE: {status}", (20, 32), cv2.FONT_HERSHEY_TRIPLEX, 0.6, THEME_GOLD, 1)

    def process_frame(self, frame):
        results = self.model(frame, stream=True, conf=0.15, imgsz=416, verbose=False)
        detected_any = False
        
        for res in results:
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                name = self.model.names[int(box.cls[0])].lower()
                
                # If it's a generic fruit/veg or something we track, try Deep Match
                crop = frame[max(0, y1):y2, max(0, x1):x2]
                if crop.size == 0: continue
                
                deep_name = self.match_item(crop)
                final_name = deep_name if deep_name else name
                
                # Filter: We only care about fruits/veggies
                if final_name not in OBJECT_DATA and "fruit" not in final_name and "vegetable" not in final_name:
                    continue

                data = OBJECT_DATA.get(final_name, {"info": "Fresh", "price": "₹40/kg", "insight": f"Detected: {final_name.capitalize()}"})
                
                # Drawing
                color = THEME_NEON if deep_name else THEME_GOLD
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                lbl = f"{final_name.upper()} (DeepMatch)" if deep_name else final_name.upper()
                cv2.putText(frame, lbl, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                self.last_item = final_name.capitalize()
                self.last_insight = data.get("insight")
                detected_any = True

        if not detected_any:
            self.last_item = "None"
            self.last_insight = "Scanning for any Fruit or Vegetable..."
            
        self.draw_hud(frame, "HYBRID_SCANNER_ACTIVE")
        return frame

# Update the global instance
engine = AdvancedVisionEngine()
