import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime

# --- PREMIUM CONFIGURATION (INDIAN RUPEE EDITION) ---
THEME_GOLD = (100, 215, 255)  
THEME_SLATE = (45, 45, 45)    
THEME_TEXT = (255, 255, 255)  
THEME_NEON = (57, 255, 20)    

# Strict Filtering: Only show these fruit & vegetable classes
VALID_CLASSES = [
    "apple", "artichoke", "banana", "bell pepper", "broccoli", 
    "cabbage", "cantaloupe", "carrot", "cucumber", "garden asparagus",
    "grape", "grapefruit", "lemon", "mango", "mushroom", "orange",
    "peach", "pear", "pineapple", "pomegranate", "potato", "pumpkin",
    "radish", "squash", "strawberry", "tomato", "vegetable", "watermelon",
    "winter melon", "zucchini"
]

# Enriched nutrition data & pricing in INDIAN RUPEES (INR)
OBJECT_DATA = {
    "apple": {"info": "Fresh Gala | Vitamin C", "price": "₹150/kg", "insight": "Apples are high in fiber and vitamin C, supporting heart health."},
    "banana": {"info": "Robusta | Potassium", "price": "₹60/doz", "insight": "Bananas are a great source of potassium, helping maintain blood pressure."},
    "orange": {"info": "Nagpur | Citrus", "price": "₹80/kg", "insight": "Oranges are packed with Vitamin C, boosting the immune system."},
    "carrot": {"info": "Desi | Vitamin A", "price": "₹40/kg", "insight": "Carrots are rich in beta-carotene, essential for good eye health."},
    "broccoli": {"info": "Green Florets", "price": "₹120/kg", "insight": "Broccoli is a superfood rich in Vitamin K and calcium for bones."},
    "tomato": {"info": "Hybrid | Lycopene", "price": "₹30/kg", "insight": "Tomatoes contain lycopene, which helps protect cells from damage."},
    "potato": {"info": "Jyoti | Carbs", "price": "₹25/kg", "insight": "Potatoes provide complex carbohydrates for sustained energy."},
    "onion": {"info": "Nasik Red", "price": "₹35/kg", "insight": "Onions have antioxidants that help reduce inflammation."},
    "mango": {"info": "Alphonso | Vitamin A", "price": "₹600/box", "insight": "Mangoes are rich in Vitamin A and C, promoting skin health."},
    "strawberry": {"info": "Mahabaleshwar", "price": "₹100/pkt", "insight": "Strawberries are low in calories and high in antioxidants."},
    "cucumber": {"info": "English | Hydrating", "price": "₹40/kg", "insight": "Cucumbers are 95% water, keeping you hydrated and refreshed."},
    "bell pepper": {"info": "Capsicum | Vitamin C", "price": "₹60/kg", "insight": "Bell peppers have more Vitamin C than oranges by weight."},
    "pomegranate": {"info": "Kandhari", "price": "₹180/kg", "insight": "Pomegranates are great for blood flow and heart health."},
    "zucchini": {"info": "Green | Low Cal", "price": "₹90/kg", "insight": "Zucchini is very low calorie and supports healthy digestion."},
    "watermelon": {"info": "Kiran | Lycopene", "price": "₹30/kg", "insight": "Watermelon is highly hydrating and contains heart-healthy lycopene."},
    "lemon": {"info": "Yellow | Vitamin C", "price": "₹5/pc", "insight": "Lemons help aid digestion and provide a huge Vitamin C boost."},
    "cauliflower": {"info": "White Florets", "price": "₹40/kg", "insight": "Cauliflower is a versatile veggie high in fiber and B-vitamins."},
    "mushroom": {"info": "Button | B-Vitamins", "price": "₹50/pkt", "insight": "Mushrooms are one of the few food sources of Vitamin D."},
    "spinach": {"info": "Palak | Iron", "price": "₹20/bunch", "insight": "Spinach is iron-rich, helping maintain healthy blood oxygen levels."},
    "pineapple": {"info": "Queen | Bromelain", "price": "₹80/pc", "insight": "Pineapple contains bromelain, which aids in protein digestion."},
    "pear": {"info": "Naspati | Fiber", "price": "₹120/kg", "insight": "Pears are excellent for gut health due to their high fiber content."},
    "pomegranate": {"info": "Anaar", "price": "₹150/kg", "insight": "Pomegranate seeds are anti-inflammatory and heart-healthy."}
}

CLASS_REMAP = {
    "goldfish": "carrot",
    "gold fish": "carrot",
    "garden asparagus": "vegetable"
}

class PremiumDetector:
    def __init__(self, model_path="yolov8n-oiv7.pt"):
        # Switched to Nano model for speed!
        print(f"[SYSTEM] Initializing Optimized AI Engine...")
        self.model = YOLO(model_path)
        self.history = []
        self.fps = 0
        self.start_time = time.time()
        self.frame_count = 0
        self.last_item = "None"
        self.last_insight = "Scan a fruit or vegetable to see insights."

    def draw_hud(self, frame, status_text="SCANNING READY"):
        h, w, _ = frame.shape
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), THEME_SLATE, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "KUSHALZZ AI VISION - FRUIT & VEG", (20, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.7, THEME_GOLD, 2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"FPS: {self.fps:.1f} | {timestamp}", (w - 220, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, THEME_GOLD, 1)
        cv2.rectangle(frame, (10, h - 40), (250, h - 10), THEME_SLATE, -1)
        cv2.putText(frame, f"STATUS: {status_text}", (20, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, THEME_NEON, 1)

    def draw_glass_box(self, frame, x1, y1, x2, y2, name, conf, data):
        color = THEME_GOLD
        thickness = 2
        l = 25 
        cv2.line(frame, (x1, y1), (x1 + l, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + l), color, thickness)
        cv2.line(frame, (x2, y1), (x2 - l, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + l), color, thickness)
        cv2.line(frame, (x1, y2), (x1 + l, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - l), color, thickness)
        cv2.line(frame, (x2, y2), (x2 - l, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - l), color, thickness)
        lbl_h = 60
        sub_overlay = frame.copy()
        cv2.rectangle(sub_overlay, (x1, y1 - lbl_h), (x1 + 220, y1), THEME_SLATE, -1)
        cv2.addWeighted(sub_overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, f"{name.upper()} {conf:.0%}", (x1 + 10, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, THEME_GOLD, 2)
        cv2.putText(frame, data.get("info", "Fresh Item"), (x1 + 10, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(frame, f"PRICE: {data.get('price', 'TBD')}", (x1 + 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, THEME_NEON, 1)

    def run(self):
        cap = cv2.VideoCapture(0)
        # Optimized Resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            self.frame_count += 1
            if self.frame_count % 10 == 0:
                curr_time = time.time()
                self.fps = 10 / (curr_time - self.start_time)
                self.start_time = curr_time

            # Perform detection on a smaller size to boost speed
            results = self.model(frame, stream=True, conf=0.25, imgsz=320, verbose=False)
            
            detected_any = False
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    raw_name = self.model.names[cls_id].lower()
                    cls_name = CLASS_REMAP.get(raw_name, raw_name)
                    
                    # STRICT FILTERING: Only process if it's in our valid fruit/veg list
                    if cls_name not in VALID_CLASSES:
                        continue

                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    data = OBJECT_DATA.get(cls_name, {"info": f"Fresh {cls_name.capitalize()}", "price": "₹40/kg", "insight": f"{cls_name.capitalize()} is a nutritious addition to your diet."})
                    self.draw_glass_box(frame, x1, y1, x2, y2, cls_name, conf, data)
                    
                    # Update global state for Dashboard
                    self.last_item = cls_name.capitalize()
                    self.last_insight = data.get("insight")
                    detected_any = True

            self.draw_hud(frame, "TRACKING" if detected_any else "SCANNING")
            cv2.imshow("KUSHALZZ AI - FRUIT & VEG ONLY", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Ensure Nano model is used
    detector = PremiumDetector("yolov8n-oiv7.pt")
    detector.run()
