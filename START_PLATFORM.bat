@echo off
title Kushalzz AI Platform
echo [1] Starting Vision AI Engine (Backend)...
start cmd /k "py streaming_server.py"

echo [2] Launching Dashboard...
cd dashboard
npm run dev -- --port 5174

echo.
echo View Dashboard at http://localhost:5174
echo View MJPEG Stream at http://localhost:5000/video_feed
echo.
pause
