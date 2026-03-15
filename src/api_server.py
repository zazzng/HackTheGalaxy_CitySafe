#!/usr/bin/env python3
"""
API Server for BC Heat Map
Handles Gemini API calls securely using server-side API key
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import math
import pandas as pd

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-1.5-flash')
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in .env file")
else:
    genai.configure(api_key=GEMINI_API_KEY)

DATASET_PATH = 'data/raw/icbc_crash_data_cleaned.csv'
DATASET_INSIGHTS = {}


def detect_city_in_query(query_text, city_labels):
    """Return the best-matching city label mentioned in query, else None."""
    q = str(query_text or '').lower()
    sorted_labels = sorted(city_labels, key=lambda s: len(str(s)), reverse=True)
    for city in sorted_labels:
        city_l = str(city).lower()
        if city_l and city_l in q:
            return city
    return None


def extract_user_query_text(prompt_text):
    """Extract user question from composite prompts; fallback to full prompt."""
    text = str(prompt_text or '')
    marker = 'User query:'
    marker_alt = 'USER REQUEST:'

    if marker in text:
        extracted = text.split(marker, 1)[1].strip()
        stop_tokens = [
            '\nCities:', '\nStreets:', '\nHotspots:',
            ' Cities:', ' Streets:', ' Hotspots:',
            '\nDATASET CONTEXT:'
        ]
        cut_at = len(extracted)
        for token in stop_tokens:
            idx = extracted.find(token)
            if idx != -1 and idx < cut_at:
                cut_at = idx
        return extracted[:cut_at].strip()

    if marker_alt in text:
        extracted = text.split(marker_alt, 1)[1].strip()
        stop_tokens = ['\nDATASET CONTEXT:', '\nCities:', '\nStreets:', '\nHotspots:']
        cut_at = len(extracted)
        for token in stop_tokens:
            idx = extracted.find(token)
            if idx != -1 and idx < cut_at:
                cut_at = idx
        return extracted[:cut_at].strip()

    return text


def load_dataset_insights():
    """Load one-time crash dataset insights for AI context and fallback answers."""
    global DATASET_INSIGHTS
    try:
        df = pd.read_csv(DATASET_PATH)

        # Keep robust numeric crash counts.
        df['Total Crashes'] = pd.to_numeric(df['Total Crashes'], errors='coerce').fillna(0)

        # Filter empty/unknown labels where useful.
        time_df = df.dropna(subset=['Time Category'])
        day_df = df.dropna(subset=['Day Of Week'])
        month_df = df.dropna(subset=['Month Of Year'])

        city_df = df.dropna(subset=['Municipality Name (ifnull)']).copy()
        city_df['Municipality Name (ifnull)'] = city_df['Municipality Name (ifnull)'].astype(str).str.strip()
        city_df = city_df[
            city_df['Municipality Name (ifnull)'].ne('')
            & ~city_df['Municipality Name (ifnull)'].str.lower().isin({'unknown', 'unk', 'nan', 'none', 'null'})
        ]

        street_df = df.dropna(subset=['Street Full Name (ifnull)']).copy()
        street_df['Street Full Name (ifnull)'] = street_df['Street Full Name (ifnull)'].astype(str).str.strip()
        street_df = street_df[
            street_df['Street Full Name (ifnull)'].ne('')
            & ~street_df['Street Full Name (ifnull)'].str.lower().isin({'unknown', 'unk', 'nan', 'none', 'null'})
        ]

        by_time = (
            time_df.groupby('Time Category')['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )
        by_day = (
            day_df.groupby('Day Of Week')['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )
        by_month = (
            month_df.groupby('Month Of Year')['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )
        by_city = (
            city_df.groupby('Municipality Name (ifnull)')['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )
        by_street = (
            street_df.groupby('Street Full Name (ifnull)')['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )

        by_city_time = (
            city_df.groupby(['Municipality Name (ifnull)', 'Time Category'])['Total Crashes']
            .sum()
            .sort_values(ascending=False)
        )

        city_worst_time = {}
        for (city, time_cat), crash_count in by_city_time.items():
            if city not in city_worst_time:
                city_worst_time[city] = {
                    'time': str(time_cat),
                    'crashes': int(crash_count)
                }

        DATASET_INSIGHTS = {
            'rows': int(len(df)),
            'total_crashes': int(df['Total Crashes'].sum()),
            'top_time': {
                'label': str(by_time.index[0]) if len(by_time) else 'N/A',
                'crashes': int(by_time.iloc[0]) if len(by_time) else 0,
            },
            'top_day': {
                'label': str(by_day.index[0]) if len(by_day) else 'N/A',
                'crashes': int(by_day.iloc[0]) if len(by_day) else 0,
            },
            'top_month': {
                'label': str(by_month.index[0]) if len(by_month) else 'N/A',
                'crashes': int(by_month.iloc[0]) if len(by_month) else 0,
            },
            'top_city': {
                'label': str(by_city.index[0]) if len(by_city) else 'N/A',
                'crashes': int(by_city.iloc[0]) if len(by_city) else 0,
            },
            'top_street': {
                'label': str(by_street.index[0]) if len(by_street) else 'N/A',
                'crashes': int(by_street.iloc[0]) if len(by_street) else 0,
            },
            'time_top5': [
                {'label': str(idx), 'crashes': int(val)}
                for idx, val in by_time.head(5).items()
            ],
            'day_top5': [
                {'label': str(idx), 'crashes': int(val)}
                for idx, val in by_day.head(5).items()
            ],
            'month_top5': [
                {'label': str(idx), 'crashes': int(val)}
                for idx, val in by_month.head(5).items()
            ],
            'city_top5': [
                {'label': str(idx), 'crashes': int(val)}
                for idx, val in by_city.head(5).items()
            ],
            'street_top5': [
                {'label': str(idx), 'crashes': int(val)}
                for idx, val in by_street.head(5).items()
            ],
            'city_worst_time': city_worst_time,
        }
        print('Loaded dataset insights for AI context.')
    except Exception as e:
        print(f'WARNING: failed to load dataset insights: {str(e)}')
        DATASET_INSIGHTS = {}


def build_dataset_context_text():
    """Construct compact context text for AI prompts from precomputed insights."""
    if not DATASET_INSIGHTS:
        return 'Dataset insights unavailable.'

    def fmt_top(items):
        return ', '.join([f"{i['label']} ({i['crashes']:,})" for i in items])

    return (
        f"Dataset rows: {DATASET_INSIGHTS['rows']:,}. "
        f"Total crashes: {DATASET_INSIGHTS['total_crashes']:,}. "
        f"Worst time category: {DATASET_INSIGHTS['top_time']['label']} ({DATASET_INSIGHTS['top_time']['crashes']:,}). "
        f"Worst day: {DATASET_INSIGHTS['top_day']['label']} ({DATASET_INSIGHTS['top_day']['crashes']:,}). "
        f"Worst month: {DATASET_INSIGHTS['top_month']['label']} ({DATASET_INSIGHTS['top_month']['crashes']:,}). "
        f"Top city: {DATASET_INSIGHTS['top_city']['label']} ({DATASET_INSIGHTS['top_city']['crashes']:,}). "
        f"Top street: {DATASET_INSIGHTS['top_street']['label']} ({DATASET_INSIGHTS['top_street']['crashes']:,}). "
        f"Top 5 time categories: {fmt_top(DATASET_INSIGHTS['time_top5'])}. "
        f"Top 5 days: {fmt_top(DATASET_INSIGHTS['day_top5'])}."
    )


def fallback_dataset_answer(user_prompt):
    """Deterministic dataset-grounded fallback answer when model is unavailable."""
    if not DATASET_INSIGHTS:
        return (
            'AI model and dataset insights are unavailable right now. '
            'Please restart the API server and ensure the CSV file exists.'
        )

    q = extract_user_query_text(user_prompt).lower()
    top_time = DATASET_INSIGHTS['top_time']
    top_day = DATASET_INSIGHTS['top_day']
    top_month = DATASET_INSIGHTS['top_month']
    top_city = DATASET_INSIGHTS['top_city']
    top_street = DATASET_INSIGHTS['top_street']

    if any(k in q for k in ['worst time', 'best time', 'time to go', 'when to go', 'what time']):
        city_match = detect_city_in_query(q, DATASET_INSIGHTS.get('city_worst_time', {}).keys())
        if city_match:
            city_time = DATASET_INSIGHTS['city_worst_time'][city_match]
            return (
                f"For {city_match.title()}, the worst time category is {city_time['time']} "
                f"with {city_time['crashes']:,} crashes. Province-wide, the highest-risk day is {top_day['label']} "
                f"with {top_day['crashes']:,} crashes. To reduce crash risk, avoid {city_time['time']} in {city_match.title()} when possible."
            )

        return (
            f"Based on ICBC crash totals, the worst time category is {top_time['label']} "
            f"with {top_time['crashes']:,} crashes. The highest-risk day is {top_day['label']} "
            f"with {top_day['crashes']:,} crashes. To reduce risk, avoid {top_time['label']} on {top_day['label']} "
            f"when possible, and prefer lower-volume off-peak windows."
        )

    return (
        f"Dataset-based safety snapshot: highest-risk time is {top_time['label']} ({top_time['crashes']:,}), "
        f"highest-risk day is {top_day['label']} ({top_day['crashes']:,}), highest-risk month is {top_month['label']} "
        f"({top_month['crashes']:,}), top city is {top_city['label']} ({top_city['crashes']:,}), and top street is "
        f"{top_street['label']} ({top_street['crashes']:,})."
    )

# High-risk zones in BC
HIGH_RISK_ZONES = [
    {
        'zone': 'Vancouver Downtown',
        'latitude': 49.28,
        'longitude': -123.12,
        'crashes': 45000,
        'percentage': 4.1
    },
    {
        'zone': 'Surrey Central',
        'latitude': 49.19,
        'longitude': -122.30,
        'crashes': 38000,
        'percentage': 3.5
    },
    {
        'zone': 'Burnaby Highway 1',
        'latitude': 49.22,
        'longitude': -122.90,
        'crashes': 32000,
        'percentage': 2.9
    },
    {
        'zone': 'Richmond Airport Area',
        'latitude': 49.19,
        'longitude': -123.18,
        'crashes': 28000,
        'percentage': 2.6
    },
    {
        'zone': 'Langley Bypass',
        'latitude': 49.10,
        'longitude': -122.39,
        'crashes': 22000,
        'percentage': 2.0
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def determine_risk_level(nearby_zones):
    """Determine risk level based on nearby zones"""
    if not nearby_zones:
        return 'low'
    
    # If any zone is very close (< 5km), it's high risk
    for zone in nearby_zones:
        if zone['distance'] < 5:
            return 'high'
    
    # If zones are moderately close (5-20km), it's medium
    for zone in nearby_zones:
        if zone['distance'] < 20:
            return 'medium'
    
    return 'low'

@app.route('/api/analyze', methods=['POST'])
def analyze_crash_data():
    """
    Endpoint to analyze crash data with Gemini API
    Uses server-side API key from .env
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt in request'}), 400
        
        prompt = data.get('prompt')
        enriched_prompt = (
            'You are a BC crash-data safety analyst. Use only the provided dataset facts. '\
            'If asked for worst/best times, answer with direct numeric evidence. '\
            'Be concise and actionable.\n\n'
            + 'DATASET CONTEXT:\n'
            + build_dataset_context_text()
            + '\n\nUSER REQUEST:\n'
            + str(prompt)
        )
        
        # Call Gemini API with graceful fallback so frontend never gets a hard failure.
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            response = model.generate_content(enriched_prompt)
            analysis = response.text if response.text else "No analysis generated"
        except Exception as ai_error:
            analysis = fallback_dataset_answer(prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/check-location', methods=['POST'])
def check_location():
    """
    Endpoint to check location and provide risk warnings
    Finds nearby high-risk zones and generates AI warning
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Missing latitude or longitude'}), 400
        
        user_lat = float(data['latitude'])
        user_lon = float(data['longitude'])
        
        # Find nearby high-risk zones (within 50km)
        nearby_zones = []
        for zone in HIGH_RISK_ZONES:
            distance = calculate_distance(user_lat, user_lon, zone['latitude'], zone['longitude'])
            if distance <= 50:
                nearby_zones.append({
                    'zone': zone['zone'],
                    'distance': round(distance, 1),
                    'crashes': zone['crashes'],
                    'percentage': zone['percentage']
                })
        
        # Sort by distance
        nearby_zones.sort(key=lambda z: z['distance'])
        
        # Determine risk level
        risk_level = determine_risk_level(nearby_zones)
        
        # Generate warning using Gemini
        zone_info = ', '.join([f"{z['zone']} ({z['distance']}km away)" for z in nearby_zones[:3]])
        warning_prompt = f"""You are a road safety advisor. A driver is in a location near these high-risk crash zones: {zone_info or 'no known high-risk zones'}.

Provide a brief (2-3 sentences) warning about the crash risks in this area and ONE specific safety recommendation. Be direct and actionable."""
        
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            ai_response = model.generate_content(warning_prompt)
            warning_text = ai_response.text if ai_response.text else "Drive carefully in this area."
        except Exception as e:
            warning_text = f"Drive carefully in this area. Contact support if you need help."
        
        return jsonify({
            'success': True,
            'risk_level': risk_level,
            'warning': warning_text,
            'zones': nearby_zones
        })
    
    except Exception as e:
        print(f"Error in check-location endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(GEMINI_API_KEY),
        'dataset_insights_loaded': bool(DATASET_INSIGHTS)
    })


@app.route('/api/dataset-insights', methods=['GET'])
def dataset_insights():
    """Expose key aggregated insights for debugging and UI use."""
    return jsonify({
        'success': True,
        'insights': DATASET_INSIGHTS
    })

if __name__ == '__main__':
    load_dataset_insights()
    print("🚀 API Server starting on http://localhost:5000")
    print(f"📌 Gemini API Key configured: {bool(GEMINI_API_KEY)}")
    app.run(debug=True, host='localhost', port=5000)
