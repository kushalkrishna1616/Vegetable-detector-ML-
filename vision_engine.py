import cv2
import numpy as np
from ultralytics import YOLO
import os

VEGETABLE_DIR = "vegetable"
OBJECT_DATA = {
    "apple":       {"type": "fruit",     "calories": "52 kcal",  "color": "Red/Green",    "price": "₹150/kg",  "insight": "Apples are rich in fiber and keep the heart healthy."},
    "banana":      {"type": "fruit",     "calories": "89 kcal",  "color": "Yellow",       "price": "₹60/doz",  "insight": "Great for energy and packed with potassium."},
    "mango":       {"type": "fruit",     "calories": "60 kcal",  "color": "Orange/Yellow","price": "₹600/box", "insight": "The King of Fruits, loaded with Vitamin A."},
    "orange":      {"type": "fruit",     "calories": "47 kcal",  "color": "Orange",       "price": "₹80/kg",   "insight": "High in Vitamin C to boost your immunity."},
    "strawberry":  {"type": "fruit",     "calories": "33 kcal",  "color": "Red",          "price": "₹100/pkt", "insight": "Berries are great for skin and brain health."},
    "grape":       {"type": "fruit",     "calories": "69 kcal",  "color": "Green/Purple", "price": "₹120/kg",  "insight": "Contain antioxidants called polyphenols."},
    "pear":        {"type": "fruit",     "calories": "57 kcal",  "color": "Green",        "price": "₹160/kg",  "insight": "Highly nutritional and easy to digest."},
    "pomegranate": {"type": "fruit",     "calories": "83 kcal",  "color": "Dark Red",     "price": "₹200/kg",  "insight": "Great for blood health and circulation."},
    "watermelon":  {"type": "fruit",     "calories": "30 kcal",  "color": "Green/Red",    "price": "₹40/kg",   "insight": "92% water, perfect for hydration!"},
    "peach":       {"type": "fruit",     "calories": "39 kcal",  "color": "Peach/Orange", "price": "₹180/kg",  "insight": "Contains Vitamin C and helps skin health."},
    "pineapple":   {"type": "fruit",     "calories": "50 kcal",  "color": "Yellow/Brown", "price": "₹80/pc",   "insight": "Contains bromelain, which aids digestion."},
    "kiwi":        {"type": "fruit",     "calories": "61 kcal",  "color": "Brown/Green",  "price": "₹150/kg",  "insight": "Full of Vitamin C and dietary fiber."},
    "papaya":      {"type": "fruit",     "calories": "43 kcal",  "color": "Orange",       "price": "₹50/kg",   "insight": "Great for digestion and high in Vitamin A."},
    "blackgrapes": {"type": "fruit",     "calories": "67 kcal",  "color": "Black/Purple", "price": "₹140/kg",  "insight": "Rich in antioxidants and great for heart health."},
    "green_grapes":{"type": "fruit",     "calories": "69 kcal",  "color": "Green",        "price": "₹120/kg",  "insight": "Refreshing and good for hydration and energy."},
    "broccoli":    {"type": "vegetable", "calories": "34 kcal",  "color": "Green",        "price": "₹120/kg",  "insight": "A superfood high in Vitamin K and fiber."},
    "carrot":      {"type": "vegetable", "calories": "41 kcal",  "color": "Orange",       "price": "₹40/kg",   "insight": "Great for your eyes and overall vision."},
    "tomato":      {"type": "vegetable", "calories": "18 kcal",  "color": "Red",          "price": "₹30/kg",   "insight": "Rich in Lycopene, great for skin health."},
    "cucumber":    {"type": "vegetable", "calories": "15 kcal",  "color": "Green",        "price": "₹40/kg",   "insight": "Keeps you cool and hydrated."},
    "potato":      {"type": "vegetable", "calories": "77 kcal",  "color": "Brown",        "price": "₹25/kg",   "insight": "An energy-rich staple food worldwide."},
    "bell pepper": {"type": "vegetable", "calories": "31 kcal",  "color": "Multi",        "price": "₹80/kg",   "insight": "Crunchy and rich in Vitamin C."},
    "cabbage":     {"type": "vegetable", "calories": "25 kcal",  "color": "Green/Purple", "price": "₹30/pc",   "insight": "Low in calories, high in vitamins."},
    "zucchini":    {"type": "vegetable", "calories": "17 kcal",  "color": "Green",        "price": "₹60/kg",   "insight": "Great for weight loss and digestion."},
    "mushroom":    {"type": "vegetable", "calories": "22 kcal",  "color": "White/Brown",  "price": "₹50/pkt",  "insight": "A great source of B vitamins and selenium."},
    "pumpkin":     {"type": "vegetable", "calories": "26 kcal",  "color": "Orange",       "price": "₹40/kg",   "insight": "Rich in beta-carotene and antioxidants."},
}

# Items YOLO OIV7 can detect natively — use YOLO for these
YOLO_CLASSES = {
    "apple", "banana", "broccoli", "carrot", "cabbage", "cucumber",
    "lemon", "mango", "mushroom", "orange", "peach", "pear", "pineapple",
    "pomegranate", "potato", "pumpkin", "strawberry", "tomato",
    "watermelon", "zucchini", "grape", "fruit", "vegetable", "food"
}

IGNORE_CLASSES = {
    "person", "man", "woman", "boy", "girl",
    "human face", "human body", "human head", "human arm", "human hand",
    "human leg", "human hair", "human ear", "human eye", "human mouth", "human nose",
}


class VisualMemoryEngine:
    """ORB feature matching using only the CENTER crop of gallery images to avoid background noise."""
    def __init__(self, gallery_path=VEGETABLE_DIR):
        self.gallery_path = gallery_path
        self.memory = {}
        self.orb = cv2.ORB_create(nfeatures=300)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.load_memory()

    def _center_crop(self, img, fraction=0.7):
        """Crop the center fraction of an image."""
        h, w = img.shape[:2]
        margin_h = int(h * (1 - fraction) / 2)
        margin_w = int(w * (1 - fraction) / 2)
        return img[margin_h:h - margin_h, margin_w:w - margin_w]

    def load_memory(self):
        if not os.path.exists(self.gallery_path):
            os.makedirs(self.gallery_path)
            return
        print(f"[MEMORY] Loading ORB features from gallery centers...")
        for file in os.listdir(self.gallery_path):
            if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            img = cv2.imread(os.path.join(self.gallery_path, file))
            if img is None:
                continue
            # Use center 70% to avoid background features
            center = self._center_crop(cv2.resize(img, (256, 256)), fraction=0.7)
            gray = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
            kp, des = self.orb.detectAndCompute(gray, None)
            name = os.path.splitext(file)[0].lower()
            if des is not None and len(des) >= 15:
                self.memory[name] = des
                print(f"  [MEM] {name}: {len(kp)} keypoints")
            else:
                print(f"  [WARN] {name}: not enough features")
        print(f"[MEMORY] Loaded {len(self.memory)} gallery signatures.")

    def find_match(self, frame):
        """Match frame against all gallery items. Returns (name, count) only if one item clearly dominates."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp2, des2 = self.orb.detectAndCompute(gray, None)
        if des2 is None or len(des2) < 10:
            return None, 0

        scores = {}
        for name, des1 in self.memory.items():
            try:
                matches = self.bf.match(des1, des2)
                # Very strict: only matches with distance < 45
                good = [m for m in matches if m.distance < 45]
                scores[name] = len(good)
            except Exception:
                scores[name] = 0

        if not scores:
            return None, 0

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_name, best_count = sorted_scores[0]
        second_count = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

        # Accept only if:
        # 1. Best match has >= 12 good matches
        # 2. Best match is at least 2.5x better than second best (clear winner)
        if best_count >= 12 and best_count > second_count * 2.5:
            return best_name, best_count

        return None, 0


class AdvancedVisionEngine:
    def __init__(self, model_path="yolov8n-oiv7.pt"):  # Back to Nano - it worked before
        print("[SYSTEM] Initializing Vision Engine...")
        self.model = YOLO(model_path)
        self.visual_memory = VisualMemoryEngine()
        self.last_item = "None"
        self.last_insight = "Ready to scan items."
        self.last_data = {}
        self.knowledge_base = {name: 1 for name in self.visual_memory.memory.keys()}

    def get_item_data(self, name):
        return OBJECT_DATA.get(name.lower(), {
            "type": "Matched Item",
            "calories": "50 kcal",
            "color": "Natural",
            "price": "₹60/kg",
            "insight": "High quality item from your gallery!",
        })

    def process_frame(self, frame):
        detected_any = False
        h, w = frame.shape[:2]

        # ── Step 1: YOLO detection (no preprocessing - works better for screen images) ──
        results = self.model(frame, stream=True, conf=0.10, imgsz=640, verbose=False)
        for res in results:
            for box in res.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_name = self.model.names[int(box.cls[0])].lower()

                if cls_name in IGNORE_CLASSES:
                    continue
                if cls_name not in YOLO_CLASSES:
                    continue

                data = self.get_item_data(cls_name)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{cls_name.upper()} {conf:.0%}",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                self.last_item = cls_name.capitalize()
                self.last_insight = data.get("insight")
                self.last_data = data
                detected_any = True

        # ── Step 2: Gallery ORB matching (only for items YOLO can't detect) ──
        if not detected_any:
            match_name, match_count = self.visual_memory.find_match(frame)
            if match_name:
                data = self.get_item_data(match_name)
                display = match_name.replace("_", " ").upper()
                cv2.rectangle(frame, (10, 50), (w - 10, h - 10), (255, 165, 0), 3)
                cv2.rectangle(frame, (0, h - 70), (w, h), (0, 0, 0), -1)
                cv2.putText(frame, f"GALLERY: {display}",
                            (15, h - 38), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 165, 0), 2)
                self.last_item = match_name.replace("_", " ").capitalize()
                self.last_insight = data.get("insight")
                self.last_data = data
                detected_any = True

        if not detected_any:
            self.last_item = "None"
            self.last_insight = "Hold item closer to camera..."

        # HUD
        cv2.rectangle(frame, (0, 0), (w, 40), (30, 30, 30), -1)
        cv2.putText(frame, "VEGDETECTOR v8.0 | KUSHALZZ AI",
                    (20, 25), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (100, 215, 255), 1)
        return frame


engine = AdvancedVisionEngine()
