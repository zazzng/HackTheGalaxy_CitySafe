# 🚗 Driver Safety Warning System - Setup Guide

This feature uses **Gemini AI** to provide real-time crash risk warnings based on the driver's location.

## How It Works

1. **Driver clicks "Start Location Tracking"** on `driver-warning.html`
2. **Browser requests location** (latitude/longitude) from GPS
3. **Backend server** checks nearby crash zones around that location
4. **Gemini API** generates a contextual safety warning
5. **Warning is displayed** with specific zone information

## Setup Instructions

### 1. Install Dependencies

```bash
cd /Users/jana/Documents/HackTheGalaxy_CitySafe
pip install -r requirements.txt
```

### 2. Configure Gemini API Key

Edit the `.env` file in the project root:

```bash
# .env file
GEMINI_API_KEY=your_api_key_here
```

**Getting your API key:**
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
- Click "Get API Key"
- Create a new API key
- Copy and paste it into `.env`

### 3. Start the Flask Backend Server

```bash
python3 src/gemini_warning_server.py
```

You should see:
```
🚗 Starting Gemini Driver Safety Warning Server...
✓ API Configured: True
 * Running on http://localhost:5000
```

### 4. Keep HTTP Server Running on Port 8000

In a different terminal:
```bash
cd /Users/jana/Documents/HackTheGalaxy_CitySafe/output
python3 -m http.server 8000
```

### 5. Access the Driver Warning Feature

1. Go to `http://localhost:8000`
2. Click the **"Use Driver Safety Warning"** link in the footer
3. Click **"Start Location Tracking"**
4. **Grant location permission** when prompted
5. Receive real-time Gemini-powered safety warnings!

## Features

✅ **Real-time location tracking** - Uses browser geolocation API
✅ **Gemini AI warnings** - Context-aware safety messages
✅ **Nearby zone detection** - Shows High-crash areas within 50km
✅ **Risk levels** - Critical, High, Medium, Low
✅ **Specific recommendations** - Actionable driving advice

## What Gemini Analyzes

For each location, Gemini receives:
- **Nearby crash zones** with coordinates
- **Crash count** in each zone
- **Percentage of total crashes**
- **Risk level** assessment
- Generates **practical safety tips**

## Example Output

```
⚠️ HIGH RISK
You are 18km from the LOWER MAINLAND zone, which accounts for 64.4% of all BC crashes. 
Expect heavy traffic, reduce speed, and maintain extra following distance. 
Avoid distracted driving and stay alert for sudden stops.
```

## Architecture

```
Browser (driver-warning.html)
    ↓ (GET location)
    ↓ (POST location to backend)
Flask Server (gemini_warning_server.py)
    ↓ (Check nearby zones)
    ↓ (Call Gemini API)
Gemini API
    ↓ (Generate warning)
Flask Server (return warning + zones)
    ↓ (Display warning)
Browser (show alert to driver)
```

## Troubleshooting

**Q: "Connection error: Failed to fetch"**
- Make sure Flask server is running on port 5000
- Check that backend-frontend communication is configured correctly

**Q: "Gemini API key not configured"**
- Update the `.env` file with your actual API key
- Restart the Flask server

**Q: Browser won't share location**
- Click "Allow" when permission prompt appears
- Check browser privacy settings
- Try in an incognito window

**Q: Getting unexpected warnings**
- Check if your location is within 50km of a known high-crash zone
- Verify the backend is using latest crash zone data

## Files Created

- `src/gemini_warning_server.py` - Flask backend with Gemini integration
- `output/driver-warning.html` - Driver warning UI
- `.env` - Configuration file for API keys
- `requirements.txt` - Python dependencies

## Security Notes

⚠️ **Never commit `.env` with real API keys to version control**

The `.env` file should be added to `.gitignore`:
```bash
echo ".env" >> .gitignore
```
