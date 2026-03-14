#!/usr/bin/env python3
"""
Flask server for real-time Gemini-powered driver safety warnings
"""

from flask import Flask, request, jsonify
import os
import json
import math
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

# BC crash zones with center coordinates
CRASH_ZONES = {
    'LOWER MAINLAND': {'lat': 49.28, 'lon': -122.78, 'crashes': 888374, 'percentage': 64.4},
    'SOUTHERN INTERIOR': {'lat': 49.25, 'lon': -120.30, 'crashes': 199102, 'percentage': 14.4},
    'VANCOUVER ISLAND': {'lat': 49.15, 'lon': -123.95, 'crashes': 192693, 'percentage': 14.0},
    'NORTH CENTRAL': {'lat': 53.90, 'lon': -122.30, 'crashes': 79774, 'percentage': 5.8},
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def find_nearby_zones(latitude, longitude, radius_km=50):
    """Find crash zones near the driver's location"""
    nearby = []
    
    for zone_name, zone_data in CRASH_ZONES.items():
        distance = haversine_distance(latitude, longitude, zone_data['lat'], zone_data['lon'])
        
        if distance <= radius_km:
            nearby.append({
                'zone': zone_name,
                'distance': round(distance, 2),
                'crashes': zone_data['crashes'],
                'percentage': zone_data['percentage'],
                'risk_level': 'critical' if zone_data['percentage'] > 50 else 'high' if zone_data['percentage'] > 10 else 'medium'
            })
    
    return sorted(nearby, key=lambda x: x['distance'])

@app.route('/api/check-location', methods=['POST'])
def check_location():
    """
    Check driver location and return Gemini-powered warning
    """
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Missing latitude or longitude'}), 400
        
        if not GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        # Find nearby high-crash zones
        nearby_zones = find_nearby_zones(latitude, longitude)
        
        if not nearby_zones:
            return jsonify({
                'warning': 'No high-risk crash zones nearby. Safe driving area.',
                'risk_level': 'low',
                'zones': []
            })
        
        # Build context for Gemini from nearby zones
        zones_info = '\n'.join([
            f"- {z['zone']}: {z['distance']}km away, {z['crashes']:,} crashes ({z['percentage']}% of total, Risk: {z['risk_level'].upper()})"
            for z in nearby_zones
        ])
        
        # Call Gemini API for context-aware warning
        gemini_prompt = f"""You are a road safety AI advisor. A driver is located at coordinates ({latitude}, {longitude}) in BC, Canada.

Nearby high-crash zones:
{zones_info}

Based on this data, provide a brief (2-3 sentences) safety warning about:
1. The crash risk in their current area
2. Specific driving precautions they should take
3. One actionable safety tip

Keep the warning urgent but not alarming. Focus on practical advice."""
        
        gemini_response = requests.post(
            f'{GEMINI_API_URL}?key={GEMINI_API_KEY}',
            json={
                'contents': [{
                    'parts': [{
                        'text': gemini_prompt
                    }]
                }]
            },
            timeout=10
        )
        
        if gemini_response.status_code != 200:
            warning_text = f"⚠️ HIGH CRASH RISK AREA: You are near zones with significant crash history. Drive carefully and stay alert."
        else:
            response_data = gemini_response.json()
            warning_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Determine overall risk level
        max_percentage = max([z['percentage'] for z in nearby_zones])
        if max_percentage > 50:
            risk_level = 'critical'
        elif max_percentage > 20:
            risk_level = 'high'
        else:
            risk_level = 'medium'
        
        return jsonify({
            'warning': warning_text,
            'risk_level': risk_level,
            'zones': nearby_zones,
            'location': {'latitude': latitude, 'longitude': longitude}
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Check if Gemini API is configured"""
    return jsonify({
        'configured': bool(GEMINI_API_KEY),
        'message': 'Gemini warning system ready' if GEMINI_API_KEY else 'Please set GEMINI_API_KEY environment variable'
    })

if __name__ == '__main__':
    print("🚗 Starting Gemini Driver Safety Warning Server...")
    print(f"✓ API Configured: {bool(GEMINI_API_KEY)}")
    app.run(debug=False, host='localhost', port=5000)
