# 🥦 VegDetector AI Vision Platform
### *Premium Vegetable Detection & Dual-Mode Analytics Suite*

Welcome to **VegDetector AI**, a luxury-themed object detection platform designed for both high-end retail and interactive education. Powered by **YOLOv8** and **React**, this project solves the bottleneck of manual checkout while providing a fun, nutritional learning experience for children.

---

## 🎯 Problem Statement
"Manual vegetable identification during checkout is slow, error-prone, and misses an opportunity for nutritional education. Children, in particular, lack engaging ways to learn about healthy eating while accompanying parents. **VegDetector AI** provides a dual-purpose solution: a high-speed automated checkout system for retailers and an interactive, real-time nutritional guide for children, all protected by secure Google Authentication."

---

## 🌟 Key Features

- **Dual-Experience Modes**: 
  - 🎒 **Kids Explorer**: A vibrant UI for children that shows fun facts, colors, and calories for every detected item.
  - 🛒 **Quick Checkout**: A sleek, high-speed automated billing flow for smart shopping.
- **20+ AI Detection Classes**: Optimized to detect at least 10 fruits and 10 vegetables with high precision.
- **Google Authentication**: Secure login system for personalized user profiles and history.
- **Luxury AI HUD**: Enhanced real-time overlay with a Gold & Slate aesthetic, featuring glassmorphism-inspired UI.
- **Nutritional Intelligence**: Real-time insights, calories, and vitamin details for all detected items.
- **Razorpay Integration**: Seamless payment gateway support for the checkout experience.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** (with `ultralytics`, `opencv-python`, and `flask`)
- **Node.js 18+** (for the Dashboard)

### 2. Automatic Launch (Windows)
Run the master start script to initialize the system:
```powershell
.\START_PLATFORM.bat
```

### 3. Manual Startup
**Start Python AI Streamer:**
```bash
py streaming_server.py
```

**Launch Dashboard:**
```bash
cd dashboard
npm install
npm run dev
```

---

## 📁 Project Structure

| File/Folder | Purpose |
| :--- | :--- |
| `vision_engine.py` | Core YOLOv8 vision logic with expanded nutritional data. |
| `streaming_server.py`| Flask bridge serving MJPEG feed and real-time item status. |
| `dashboard/` | Premium React frontend with Kids and Checkout modules. |
| `oiv7_classes.txt` | Dataset classes for the Open Images V7 model. |
| `START_PLATFORM.bat` | One-click system orchestrator. |

---

## 🎨 Design Philosophy
The platform utilizes a **Dynamic Aesthetic System**—shifting from a "Luxury Gold" theme for Checkout to a "Sky Blue & Vibrant" theme for Kids Mode, ensuring the UI feels alive and tailored to the user.

---
Developed with ❤️ by Kushal G.
