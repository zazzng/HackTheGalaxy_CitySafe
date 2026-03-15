# BC Heat Map - Complete Setup Guide

## Project Overview

This is a comprehensive crash data analysis system for British Columbia that combines:
- Interactive heatmaps showing crash locations
- AI-powered driver safety warnings
- Real-time cursor-based danger zone detection

## Before You Start

### Required Files
✅ All files are ready in `/Users/jana/Documents/HackTheGalaxy_CitySafe/output/`

### 1. Start the API Server (Port 5000)

```bash
cd /Users/jana/Documents/HackTheGalaxy_CitySafe
python3 src/api_server.py
```

**You should see:**
```
🚀 API Server starting on http://localhost:5000
📌 Gemini API Key configured: True
```

### 2. Start the Web Server (Port 8000)

**In a SEPARATE terminal:**

```bash
cd /Users/jana/Documents/HackTheGalaxy_CitySafe/output
python3 -m http.server 8000
```

**You should see:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### 3. Open Your Browser

Visit: **http://localhost:8000**

---

## Features

### Main Page (http://localhost:8000)
- **BC Heat Map**: Full interactive heatmap showing 1,087,337 crash points
- **Top 10 Cities**: Click any city to zoom to that city's heatmap
- **Top 10 Streets**: Click any street to zoom to that street's heatmap
- **Gemini AI Analysis**: Click "Generate Analysis" for AI insights
- **Two Driver Warning Systems**: See buttons below the map

### Driver Safety Warning (driver-warning.html)
- **GPS-Based Location Tracking**: Click "Start Location Tracking"
- **Real-Time Risk Assessment**: AI analyzes nearby high-crash zones
- **Nearby Zones Display**: See which zones are dangerous near you
- **Back Button**: Return to main page

### Interactive Cursor Warning (interactive-warning.html)
- **Heatmap Display**: Shows all crashes on the left side
- **Cursor Tracking**: Move cursor to detect danger zones
- **Tight Detection Zone**: Only warns about streets within 500m-800m
- **Street Details**: See specific streets with crash counts
- **Gemini AI Actions**: Get one-sentence safety actions
- **Back Button**: Return to main page

---

## File Structure

```
output/
├── index.html                     # Main page
├── style.css                      # Styling
├── script.js                      # Main functionality
├── heatmap.html                   # Full BC heatmap (27MB)
├── heatmap-city-*.html           # 10 city-specific heatmaps
├── heatmap-street-*.html         # 10 street-specific heatmaps
├── driver-warning.html           # GPS-based warnings
├── interactive-warning.html      # Cursor-based warnings
├── top_cities.json               # Top 10 cities data
└── top_streets.json              # Top 10 streets data

src/
├── api_server.py                 # Flask backend (Port 5000)
└── heatmap.py                    # Heatmap generation script

data/
└── raw/
    └── icbc_crash_data_cleaned.csv  # 1,087,337 crash records
```

---

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (No frameworks)
- **Backend**: Python 3 + Flask (Handles Gemini API securely)
- **APIs**: Google Gemini Pro (AI warnings)
- **Maps**: Leaflet.js + Folium (Interactive heatmaps)
- **Data**: ICBC crash dataset (1,380,474 records → 1,087,337 valid)
- **Libraries**: Bootstrap CDN, Font Awesome 6.4.0

---

## Troubleshooting

### "API server not responding?"
- Make sure `python3 src/api_server.py` is running in a terminal
- Check port 5000: `lsof -i :5000`
- Restart: `pkill -f "python3 src/api_server.py"`

### "Heatmap not loading?"
- Ensure web server is running on port 8000
- Heatmaps are large (27MB) - may take 10-30 seconds to load
- Check browser console (F12) for errors
- Try a different zoom level on the map

### "AI warnings not working?"
- Verify GEMINI_API_KEY is set in `.env` file
- Check API server is running: `curl http://localhost:5000/health`
- Look for error messages in the right panel

### "Cursor detection not working?"
- Click "Enable Warning Mode" first
- Move cursor SLOWLY over the map
- Only detects streets very close (500m-800m radius)
- Try hovering near Vancouver area where more crashes are concentrated

---

## Security Notes

✅ **Your API key is NEVER exposed to the browser**
✅ **All Gemini API calls go through your local backend server**
✅ **API key is loaded from `.env` file on the server only**

---

## Next Steps

1. ✅ Start API server on port 5000
2. ✅ Start web server on port 8000
3. ✅ Open http://localhost:8000
4. ✅ Explore the heatmaps
5. ✅ Try both warning systems
6. ✅ Move cursor on interactive map to see tight-zone detection

---

**Happy exploring! Stay safe! 🚗💨**
