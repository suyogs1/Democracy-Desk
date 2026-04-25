/**
 * Democracy Desk - Frontend Intelligence
 * Coordinates Voice, Maps, and AI Agents.
 */

let map;
const STATE_COORDS = {
    "California": { lat: 36.7783, lng: -119.4179, offices: 58 },
    "Texas": { lat: 31.9686, lng: -99.9018, offices: 254 },
    "New York": { lat: 40.7128, lng: -74.0060, offices: 62 },
    "Florida": { lat: 27.6648, lng: -81.5158, offices: 67 },
    "Georgia": { lat: 32.1656, lng: -82.9001, offices: 159 },
    "Pennsylvania": { lat: 41.2033, lng: -77.1945, offices: 67 }
};

async function initMap() {
    const defaultState = document.getElementById('state-selector').value;
    const coords = STATE_COORDS[defaultState];
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: coords.lat, lng: coords.lng },
        zoom: 5,
        styles: DARK_MAP_STYLE,
        disableDefaultUI: true
    });
}

document.getElementById('state-selector').addEventListener('change', (e) => {
    const state = e.target.value;
    const coords = STATE_COORDS[state];
    document.getElementById('state-name-display').innerText = state;
    if (map && coords) {
        map.setCenter({ lat: coords.lat, lng: coords.lng });
        map.setZoom(5);
    }
});

// App Logic
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('user-input');
    const state = document.getElementById('state-selector').value;
    const mode = document.getElementById('mode-selector').value;
    const btn = document.getElementById('send-btn');
    
    if (!input.value.trim()) return;

    btn.disabled = true;
    btn.innerText = "Analyzing...";
    
    // Clear previous
    document.getElementById('reasoning-slot').innerHTML = '<div class="pulse-loader">Agentic Pipeline Active...</div>';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: input.value,
                state: state,
                mode: mode,
                enable_voice: true
            })
        });

        const data = await response.json();
        renderResponse(data);
    } catch (err) {
        console.error(err);
        document.getElementById('explanation-box').innerText = "An error occurred. Please try again.";
    } finally {
        btn.disabled = false;
        btn.innerText = "Process Request";
        input.value = "";
    }
});

function renderResponse(data) {
    const explBox = document.getElementById('explanation-box');
    const timeline = document.getElementById('timeline-stepper');
    const reasoning = document.getElementById('reasoning-slot');
    const intentBox = document.getElementById('intent-slot');
    
    // 1. Explanation
    explBox.innerHTML = `<h3>Plan Summary</h3><p>${data.final_explanation}</p>`;
    
    // 2. Timeline
    timeline.innerHTML = data.steps.map((step, i) => `
        <div class="step-item">
            <strong>Step ${i+1}: ${step.title}</strong>
            <p>${step.description}</p>
            ${step.cta ? `<button class="status-pill">${step.cta}</button>` : ''}
        </div>
    `).join('');
    
    // 3. Reasoning
    reasoning.innerHTML = data.reasoning_log.map(log => `
        <div style="margin-bottom: 8px;">
            <span style="color: var(--primary); font-weight: 600;">[${log.agent_name}]</span> ${log.summary}
        </div>
    `).join('');

    // 4. Intent
    document.getElementById('intent-panel').style.display = 'block';
    intentBox.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
            <span>Category: ${data.intent.category}</span>
            <span>Confidence: ${Math.round(data.intent.confidence * 100)}%</span>
        </div>
    `;

    // 5. Voice
    if (data.audio_content) {
        const audio = document.getElementById('ai-audio');
        audio.src = `data:audio/mp3;base64,${data.audio_content}`;
        audio.play().catch(e => console.warn("Autoplay blocked. User interaction required."));
    }
}

// Voice Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    const voiceBtn = document.getElementById('voice-btn');

    voiceBtn.onclick = () => {
        recognition.start();
        voiceBtn.classList.add('active');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user-input').value = transcript;
        voiceBtn.classList.add('pulse');
    };

    recognition.onend = () => {
        voiceBtn.classList.remove('active');
        voiceBtn.classList.remove('pulse');
    };
}

const DARK_MAP_STYLE = [
    { elementType: "geometry", stylers: [{ color: "#212121" }] },
    { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
    { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
    { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
    { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#757575" }] },
    { featureType: "water", elementType: "geometry", stylers: [{ color: "#000000" }] }
];
