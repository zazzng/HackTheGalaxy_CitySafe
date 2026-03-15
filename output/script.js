let cachedCities = [];
let cachedStreets = [];
let cachedHotspots = [];

function normalizeName(value) {
    return String(value || '').trim().toLowerCase();
}

function toTitleCase(value) {
    return String(value || '')
        .toLowerCase()
        .split(' ')
        .filter(Boolean)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function slugify(value) {
    return String(value || '').toLowerCase().trim().replace(/\s+/g, '-');
}

function setAiNavigatorResult(text, isError = false) {
    const box = document.getElementById('aiNavigatorResult');
    if (!box) return;
    box.textContent = text;
    box.style.background = isError ? '#fff2f2' : '#f7f9ff';
    box.style.borderColor = isError ? '#f3b1b1' : '#d8def5';
    box.style.color = isError ? '#9b1c1c' : '#2f3d67';
}

async function loadTopZones() {
    const zonesContent = document.getElementById('topZonesContent');

    try {
        const response = await fetch('./top_cities.json');
        if (!response.ok) {
            throw new Error('Failed to load cities data');
        }

        const citiesData = await response.json();
        cachedCities = citiesData;

        const maxCrashes = Math.max(...citiesData.map(c => c.crashes));

        const citiesHTML = citiesData.map(city => {
            const barWidth = (city.crashes / maxCrashes) * 100;
            const rankClass = city.rank === 1 ? 'rank-1' : '';
            const citySlug = slugify(city.city);
            const cityLabel = toTitleCase(city.city);

            return `
                <div class="zone-card ${rankClass}" onclick="zoomToZone('${citySlug}', '${cityLabel}')" style="cursor: pointer;">
                    <div class="zone-rank">Rank #${city.rank}</div>
                    <div class="zone-name">${cityLabel}</div>
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

function zoomToZone(citySlug, cityName) {
    const mapIframe = document.querySelector('.map-iframe');
    const mapContainer = document.querySelector('.map-container');

    mapIframe.src = `heatmap-city-${citySlug}.html`;
    mapContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    console.log(`Zooming to city: ${cityName}`);
}

async function loadTopStreets() {
    const streetsContent = document.getElementById('topStreetsContent');

    try {
        const response = await fetch('./top_streets.json');
        if (!response.ok) {
            throw new Error('Failed to load streets data');
        }

        const streetsData = await response.json();
        const filteredStreets = streetsData.filter(s => normalizeName(s.street) !== 'unknown');
        cachedStreets = filteredStreets;

        const maxCrashes = Math.max(...filteredStreets.map(s => s.crashes));

        const streetsHTML = filteredStreets.map(street => {
            const barWidth = (street.crashes / maxCrashes) * 100;
            const rankClass = street.rank === 1 ? 'rank-1' : '';
            const streetSlug = slugify(street.street);
            const streetLabel = toTitleCase(street.street);

            return `
                <div class="street-item ${rankClass}" onclick="zoomToStreet('${streetSlug}', '${streetLabel}')" style="cursor: pointer;">
                    <div class="street-rank">#${street.rank}</div>
                    <div class="street-info">
                        <div class="street-name">${streetLabel}</div>
                        <div class="street-stats">
                            <div class="street-crashes">
                                <i class="fas fa-car-crash"></i>
                                <strong>${street.crashes.toLocaleString()}</strong> crashes
                            </div>
                            <div class="street-percentage">
                                <i class="fas fa-percent"></i>
                                <strong>${street.percentage}%</strong> of total
                            </div>
                        </div>
                    </div>
                    <div class="street-bar-container">
                        <div class="street-bar">
                            <div class="street-bar-fill" style="width: ${barWidth}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        streetsContent.innerHTML = streetsHTML;
    } catch (error) {
        streetsContent.innerHTML = `<div style="color: #c33; padding: 1rem;">Error loading streets data: ${error.message}</div>`;
    }
}

function zoomToStreet(streetSlug, streetName) {
    const mapIframe = document.querySelector('.map-iframe');
    const mapContainer = document.querySelector('.map-container');

    mapIframe.src = `heatmap-street-${streetSlug}.html`;
    mapContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    console.log(`Zooming to street: ${streetName}`);
}

async function loadHotspots() {
    try {
        const response = await fetch('./hotspots.json');
        if (!response.ok) {
            throw new Error('Failed to load hotspots data');
        }
        cachedHotspots = await response.json();
    } catch (error) {
        console.error('Hotspots load error:', error.message);
        cachedHotspots = [];
    }
}

function extractJsonObject(text) {
    const match = String(text || '').match(/\{[\s\S]*\}/);
    if (!match) return null;
    try {
        return JSON.parse(match[0]);
    } catch (err) {
        return null;
    }
}

async function requestAiAnalysis(prompt, citiesData = null) {
    const endpoints = [
        'http://localhost:5000/api/analyze',
        'http://127.0.0.1:5000/api/analyze'
    ];

    let lastError = null;

    for (const url of endpoints) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        try {
            const payload = { prompt: prompt };
            if (citiesData) {
                payload.citiesData = citiesData;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error('AI endpoint error: ' + response.status + ' at ' + url);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            lastError = error;
        }
    }

    throw new Error('Cannot reach AI server on port 5000. Start it with: python3 src/api_server.py');
}

function findCityByName(name) {
    const target = normalizeName(name);
    return cachedCities.find(c => normalizeName(c.city) === target)
        || cachedCities.find(c => normalizeName(c.city).includes(target));
}

function findStreetByName(name) {
    const target = normalizeName(name);
    return cachedStreets.find(s => normalizeName(s.street) === target)
        || cachedStreets.find(s => normalizeName(s.street).includes(target));
}

function findHotspotByName(name) {
    const target = normalizeName(name);
    return cachedHotspots.find(h => normalizeName(h.name || h.city) === target)
        || cachedHotspots.find(h => normalizeName(h.name || h.city).includes(target));
}

function chooseFallbackTargetFromQuery(query) {
    const q = normalizeName(query);

    if (q.includes('street') || q.includes('highway') || q.includes('hwy') || q.includes('road')) {
        const street = cachedStreets[0];
        if (street) {
            return {
                targetType: 'street',
                targetName: street.street,
                reason: 'Fallback: using highest crash street.'
            };
        }
    }

    if (q.includes('hotspot') || q.includes('intersection') || q.includes('danger')) {
        const hotspot = cachedHotspots[0];
        if (hotspot) {
            return {
                targetType: 'hotspot',
                targetName: hotspot.name || hotspot.city,
                reason: 'Fallback: using top hotspot.'
            };
        }
    }

    const city = cachedCities[0];
    if (city) {
        return {
            targetType: 'city',
            targetName: city.city,
            reason: 'Fallback: using highest crash city.'
        };
    }

    return null;
}

async function runAiNavigator() {
    const input = document.getElementById('aiNavigatorInput');
    if (!input) return;

    const userQuery = input.value.trim();
    if (!userQuery) {
        setAiNavigatorResult('Enter a short question first.', true);
        return;
    }

    if (cachedCities.length === 0 || cachedStreets.length === 0) {
        setAiNavigatorResult('Data still loading. Try again in a second.', true);
        return;
    }

    setAiNavigatorResult('AI is analyzing your question...');

    const aiPrompt = [
        'You are a BC traffic safety map navigator.',
        'If the user asks for navigation, return ONLY valid JSON object with keys: targetType, targetName, reason.',
        'targetType must be one of: city, street, hotspot.',
        'If the user asks a safety question (worst time/day/month/risk), return a plain text answer with numeric evidence from dataset context.',
        'User query: ' + userQuery,
        'Cities: ' + cachedCities.map(c => c.city).join(', '),
        'Streets: ' + cachedStreets.map(s => s.street).join(', '),
        'Hotspots: ' + cachedHotspots.map(h => (h.name || h.city || '')).join(', ')
    ].join('\n');

    try {
        const data = await requestAiAnalysis(aiPrompt);
        const analysisText = String(data.analysis || '').trim();
        let parsed = extractJsonObject(data.analysis);
        
        // If AI returned a direct safety answer (non-JSON), show it directly.
        if ((!parsed || !parsed.targetType || !parsed.targetName) && analysisText) {
            setAiNavigatorResult(analysisText);
            return;
        }

        if (!parsed || !parsed.targetType || !parsed.targetName) {
            parsed = chooseFallbackTargetFromQuery(userQuery);
            if (!parsed) {
                throw new Error('AI response was not valid and no fallback target available.');
            }
        }

        const targetType = normalizeName(parsed.targetType);
        const targetName = parsed.targetName;
        const reason = parsed.reason || 'AI-selected based on your query.';

        if (targetType === 'city') {
            const city = findCityByName(targetName);
            if (!city) throw new Error('AI picked a city not in the dataset.');
            zoomToZone(slugify(city.city), toTitleCase(city.city));
            setAiNavigatorResult('AI Jumped to city: ' + toTitleCase(city.city) + ' | ' + reason);
            return;
        }

        if (targetType === 'street') {
            const street = findStreetByName(targetName);
            if (!street) throw new Error('AI picked a street not in the dataset.');
            zoomToStreet(slugify(street.street), toTitleCase(street.street));
            setAiNavigatorResult('AI Jumped to street: ' + toTitleCase(street.street) + ' | ' + reason);
            return;
        }

        if (targetType === 'hotspot') {
            const hotspot = findHotspotByName(targetName);
            if (!hotspot) throw new Error('AI picked a hotspot not in the dataset.');
            const mapIframe = document.querySelector('.map-iframe');
            mapIframe.src = 'heatmap-markers.html';
            document.querySelector('.map-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
            setAiNavigatorResult('AI Jumped to hotspot map: ' + toTitleCase(hotspot.name || hotspot.city) + ' | ' + reason);
            return;
        }

        throw new Error('AI returned unsupported targetType.');
    } catch (error) {
        setAiNavigatorResult('AI Navigator failed: ' + error.message, true);
    }
}

async function analyzeWithGemini() {
    const resultDiv = document.getElementById('geminiResult');

    resultDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing crash data with Gemini...';
    resultDiv.className = 'gemini-result loading';

    try {
        const citiesResponse = await fetch('./top_cities.json');
        if (!citiesResponse.ok) {
            throw new Error('Failed to load cities data');
        }
        const citiesData = await citiesResponse.json();

        const data = await requestAiAnalysis(
            `Based on the following ICBC crash data for the top cities in British Columbia, provide insights and recommendations:\n\n${JSON.stringify(citiesData, null, 2)}\n\nPlease provide:\n1. Key findings about crash patterns across the top cities\n2. Why Vancouver and Surrey have the highest crash counts\n3. Specific road safety improvement recommendations for each city\n4. Priority cities for intervention and prevention programs\n5. Actionable strategies for local governments\n\nKeep the analysis concise but actionable.`,
            citiesData
        );
        const analysisResult = data.analysis || 'No analysis available';

        resultDiv.innerHTML = `<div class="gemini-analysis">${analysisResult.replace(/\n/g, '<br>')}</div>`;
        resultDiv.className = 'gemini-result success';
    } catch (error) {
        resultDiv.innerHTML = '<strong>Error:</strong> ' + error.message;
        resultDiv.className = 'gemini-result error';
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('BC Heat Map loaded successfully');

    await Promise.all([loadTopZones(), loadTopStreets(), loadHotspots()]);

    const aiBtn = document.getElementById('aiNavigatorBtn');
    const aiInput = document.getElementById('aiNavigatorInput');

    if (aiBtn) {
        aiBtn.addEventListener('click', runAiNavigator);
    }

    if (aiInput) {
        aiInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                runAiNavigator();
            }
        });
    }
});
