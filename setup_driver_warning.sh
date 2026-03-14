#!/bin/bash
# Quick setup script for Driver Safety Warning System

echo "🚗 Setting up Driver Safety Warning System..."
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Gemini API Configuration
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "✓ .env file created"
    echo "   👉 Edit .env and add your Gemini API key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Start Flask server: python3 src/gemini_warning_server.py"
echo "3. Start HTTP server: cd output && python3 -m http.server 8000"
echo "4. Visit http://localhost:8000 and click 'Use Driver Safety Warning'"
echo ""
