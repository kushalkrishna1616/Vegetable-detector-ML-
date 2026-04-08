# 🥦 Kushalzz AI Vision Platform
### *Premium Vegetable Detection & Analytics Suite*

Welcome to the **Kushalzz AI Vision Assistant**, a luxury-themed object detection and smart-checkout platform powered by **YOLOv8** and **React**. This project transforms standard vision-based detection into a high-end retail and nutritional monitoring dashboard.

---

## 🌟 Key Features

- **Luxury AI HUD**: Enhanced real-time overlay with a Gold & Slate aesthetic, featuring glassmorphism-inspired UI and smooth L-cut bounding boxes.
- **Advanced Object Mapping**: Intelligent remapping of common AI misclassifications (e.g., "Goldfish" to "Carrot") for a reliable retail experience.
- **Real-time Analytics Dashboard**: A modern React-based interface to track revenue, object frequency, and AI confidence scores.
- **Live Stream Integration**: Effortlessly view the AI processing feed through a high-performance Flask MJPEG streamer.
- **Nutritional Intelligence**: Rotating insights and fiber/vitamin details for detected products.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** (with `ultralytics`, `opencv-python`, and `flask`)
- **Node.js 18+** (for the Dashboard)

### 2. Automatic Launch (Windows)
Run the master start script to initialize both the Backend and Frontend with one click:
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
| `vegdetector.py` | Core vision engine with premium HUD and detection logic. |
| `streaming_server.py`| Flask bridge that serves the MJPEG live feed to the web. |
| `dashboard/` | Premium React-based frontend analytics application. |
| `oiv7_classes.txt` | Dataset classes for the Open Images V7 model. |
| `START_PLATFORM.bat` | One-click system orchestrator. |

---

## 🎨 Theme & Design
The project adheres to a strict **Luxury Gold & deep Slate** design system, ensuring a premium feel comparable to high-end boutiques and smart retail environments.

---
Developed with ❤️ for the future of AI Retail.
