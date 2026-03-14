// Sample data
const sampleData = [
    { latitude: 49.46318, longitude: -122.60460, severity: "high" },
    { latitude: 49.45, longitude: -122.61, severity: "medium" },
    { latitude: 49.47, longitude: -122.59, severity: "high" },
    { latitude: 49.44, longitude: -122.62, severity: "low" },
    { latitude: 49.48, longitude: -122.58, severity: "medium" }
];

// Load sample data into textarea
function loadSampleData() {
    document.getElementById('jsonData').value = JSON.stringify(sampleData, null, 2);
}

// Clear textarea
function clearData() {
    document.getElementById('jsonData').value = '';
}

// Download JSON data
function downloadData() {
    const jsonData = document.getElementById('jsonData').value;
    if (!jsonData.trim()) {
        alert('Nothing to download. Add or load data first.');
        return;
    }
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(jsonData));
    element.setAttribute('download', 'crash_data.json');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

console.log('BC Heat Map loaded successfully');

// Load and display top cities
async function loadTopZones() {
    const zonesContent = document.getElementById('topZonesContent');
    
    try {
        const response = await fetch('./top_cities.json');
        if (!response.ok) {
            throw new Error('Failed to load cities data');
        }
        
        const citiesData = await response.json();
        
        // Find max crashes for percentage bar
        const maxCrashes = Math.max(...citiesData.map(c => c.crashes));
        
        // Generate HTML for each city
        const citiesHTML = citiesData.map(city => {
            const barWidth = (city.crashes / maxCrashes) * 100;
            const rankClass = city.rank === 1 ? 'rank-1' : '';
            const citySlug = city.city.toLowerCase().replace(/ /g, '-');
            
            return `
                <div class="zone-card ${rankClass}" onclick="zoomToZone('${citySlug}', '${city.city}')" style="cursor: pointer;">
                    <div class="zone-rank">Rank #${city.rank}</div>
                    <div class="zone-name">${city.city}</div>
                    <div class="zone-stats">
                        <div class="stat">
                            <span class="stat-label">Crashes:</span>
                            <span class="stat-value">${city.crashes.toLocaleString()}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Percentage of Total:</span>
                            <span class="stat-value">${city.percentage}%</span>
                        </div>
                    </div>
                    <div class="zone-bar">
                        <div class="zone-bar-fill" style="width: ${barWidth}%"></div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.9rem;">
                        <i class="fas fa-search-plus"></i> Click to zoom
                    </div>
                </div>
            `;
        }).join('');
        
        zonesContent.innerHTML = citiesHTML;
    } catch (error) {
        zonesContent.innerHTML = `<div style="color: #c33; padding: 1rem; grid-column: 1 / -1;">Error loading cities data: ${error.message}</div>`;
    }
}

// Zoom to a specific city's heatmap
function zoomToZone(citySlug, cityName) {
    const mapIframe = document.querySelector('.map-iframe');
    const mapContainer = document.querySelector('.map-container');
    
    // Update iframe to load the city-specific heatmap
    mapIframe.src = `heatmap-city-${citySlug}.html`;
    
    // Scroll to the map section
    mapContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Show a brief indicator
    console.log(`Zooming to: ${cityName}`);
}

// Load cities when page loads
document.addEventListener('DOMContentLoaded', loadTopZones);

// Analyze with Gemini API
async function analyzeWithGemini() {
    const apiKey = document.getElementById('geminiApiKey').value;
    const resultDiv = document.getElementById('geminiResult');

    // Validation
    if (!apiKey.trim()) {
        resultDiv.innerHTML = '<span>Please enter your Gemini API key</span>';
        resultDiv.className = 'gemini-result error';
        return;
    }

    // Show loading state
    resultDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing crash data with Gemini...';
    resultDiv.className = 'gemini-result loading';

    try {
        // Load cities data for analysis
        const citiesResponse = await fetch('./top_cities.json');
        if (!citiesResponse.ok) {
            throw new Error('Failed to load cities data');
        }
        const citiesData = await citiesResponse.json();

        // Call Gemini API with cities data
        const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + apiKey, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: `Based on the following ICBC crash data for the top cities in British Columbia, provide insights and recommendations:

${JSON.stringify(citiesData, null, 2)}

Please provide:
1. Key findings about crash patterns across the top cities
2. Why Vancouver and Surrey have the highest crash counts
3. Specific road safety improvement recommendations for each city
4. Priority cities for intervention and prevention programs
5. Actionable strategies for local governments

Keep the analysis concise but actionable.`
                    }]
                }]
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.message || 'API Error: ' + response.statusText);
        }

        const data = await response.json();
        const analysisResult = data.candidates?.[0]?.content?.parts?.[0]?.text || 'No analysis available';

        // Display result with formatting
        resultDiv.innerHTML = `<div class="gemini-analysis">${analysisResult.replace(/\n/g, '<br>')}</div>`;
        resultDiv.className = 'gemini-result success';
    } catch (error) {
        resultDiv.innerHTML = '<strong>Error:</strong> ' + error.message;
        resultDiv.className = 'gemini-result error';
    }
}