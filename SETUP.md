# BC Heat Map - Running the Application

## Prerequisites
- Python 3.9+
- Your Gemini API key in `.env` file

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

You need to run **2 servers** simultaneously:

### 1. API Server (Port 5000)
This handles Gemini API calls securely using your API key from `.env`:

```bash
python3 src/api_server.py
```

The server will start on `http://localhost:5000` and show:
```
🚀 API Server starting on http://localhost:5000
📌 Gemini API Key configured: True
```

### 2. Web Server (Port 8000)
In a separate terminal, serve the frontend files:

```bash
cd /Users/jana/Documents/HackTheGalaxy_CitySafe/output
python3 -m http.server 8000
```

The website will be available at `http://localhost:8000`

## Architecture

- **Frontend (Port 8000):** HTML, CSS, JavaScript with Leaflet maps
- **Backend (Port 5000):** Flask API that securely calls Gemini API using your server-side API key
- **Data:** ICBC crash CSV with 1,087,337 data points

## Features

1. **Interactive Heatmaps**
   - Main BC heatmap showing all crashes
   - Clickable cities for city-specific heatmaps
   - Clickable streets for street-specific heatmaps

2. **AI Analysis**
   - Click "Generate Analysis" to get Gemini AI insights
   - Powered by your API key (never exposed to browser)

3. **Driver Warning Systems**
   - **Driver Safety Warning:** GPS-based real-time alerts
   - **Interactive Cursor Warning:** Hover-based street detection

## Security Notes

✅ Your API key is **never exposed** to the browser
✅ All API calls go through your local backend server
✅ API key is loaded from `.env` file on the server

## Troubleshooting

**"Connection refused on port 5000?"**
- Make sure `python3 src/api_server.py` is running in a separate terminal

**"Cannot analyze crash data?"**
- Verify you have `google-generativeai` installed: `pip install google-generativeai`
- Check that your GEMINI_API_KEY is set in `.env`
- Check the API server logs for errors

**"Maps not loading?"**
- Ensure you're running the web server on port 8000
- Maps are large (~27MB for main heatmap), may take time to load
