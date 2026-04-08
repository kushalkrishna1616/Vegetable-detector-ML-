@echo off
title Kushalzz AI Platform
echo [1] Starting Vision AI Engine (Backend)...
start cmd /k "py streaming_server.py"

echo [2] Installing Dashboard dependencies...
cd dashboard
npm install && npm run dev

echo.
echo Platform is initializing...
echo View Feed at http://localhost:5000/video_feed
echo View Dashboard at http://localhost:5173
echo.
pause
