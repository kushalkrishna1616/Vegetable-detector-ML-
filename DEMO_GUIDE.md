# 🥗 VegDetector AI - Presentation Guide

## 🛠️ Step 1: Launch Sequence
1. **Open VS Code** in the `/vegetable` folder.
2. **Terminal 1 (AI Brain)**: 
   - Run: `python streaming_server.py`
   - *Status: Should say "Running on http://127.0.0.1:5000"*
3. **Terminal 2 (Dashboard)**: 
   - Run: `cd dashboard`
   - Run: `npm run dev`
   - *Status: Should say "Local: http://localhost:5174"*
4. **Browser**: Open `http://localhost:5174`

---

## 💡 Key Features to Show & Explain

### 1. Universal Vision Engine
- **What to say**: "We are using YOLOv8-OIV7, which detects over 600 classes of objects. I have optimized it for high-sensitivity detection of fruits and vegetables."
- **Demo**: Show how it detects common items (Apple, Banana) with high confidence.

### 2. Custom Visual Memory (The 'vegetable' Folder)
- **What to say**: "I implemented a custom Similarity Engine. We can add any photo to the `/vegetable` folder, and the AI will extract a 'Visual Signature' (color/texture) to match those specific items in real-time."
- **Demo**: Show how the name of the file in the folder appears on the screen when that item is shown.

### 3. Kids Discovery Mode
- **What to say**: "The platform has a dedicated 'Explorer Mode' for children. It removes all billing info and replaces it with a 'Discovery Quest' to make learning about healthy food gamified and fun."
- **Demo**: Switch to Kids Mode and show the 'Seedling' to 'Nature Master' progression.

### 4. Smart Checkout & Payments
- **What to say**: "For retail use, the system calculates weight-based pricing and integrates a real-time payment gateway using Razorpay."
- **Demo**: Add items to the cart, adjust weights, and show the 'Pay' button.

---

## 🛡️ Troubleshooting
- **Black Video?**: Ensure `python streaming_server.py` is running and your webcam isn't being used by another app (like Zoom/Teams).
- **Refused to Connect?**: Make sure you did `cd dashboard` before running `npm run dev`.

---
**Created by Antigravity for Kushal** 🚀
