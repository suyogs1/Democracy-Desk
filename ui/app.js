const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const stateSelector = document.getElementById('state-selector');
const modeSelector = document.getElementById('mode-selector');
const explanationBox = document.getElementById('explanation-box');
const timelineStepper = document.getElementById('timeline-stepper');
const todayActionSlot = document.getElementById('today-action-slot');
const reasoningSlot = document.getElementById('reasoning-slot');
const sendBtn = document.getElementById('send-btn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    // UI Reset
    sendBtn.disabled = true;
    sendBtn.textContent = 'Analyzing...';
    explanationBox.textContent = 'Processing your request with multi-agent intelligence...';
    timelineStepper.innerHTML = '';
    todayActionSlot.innerHTML = '';

    try {
        const response = await fetch('http://localhost:8000/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                state: stateSelector.value,
                mode: modeSelector.value
            })
        });

        if (!response.ok) throw new Error('API Error');

        const data = await response.json();
        renderResponse(data);
    } catch (error) {
        explanationBox.innerHTML = `<span style="color: var(--danger)">Unable to reach the assistant. Please try again later.</span>`;
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Get Plan';
    }
});

function renderResponse(data) {
    // 1. Final Explanation
    explanationBox.innerHTML = `<h3>Your Guide</h3><p>${data.final_explanation}</p>`;

    // 2. Today Action Widget
    todayActionSlot.innerHTML = `
        <div class="today-widget">
            <span class="urgency-badge urgency-${data.today_action.urgency}">${data.today_action.urgency} Urgency</span>
            <div style="font-size: 0.9rem; color: var(--text-muted)">Recommended for Today:</div>
            <div style="font-size: 1.1rem; font-weight: 600;">${data.today_action.action}</div>
            <div style="font-size: 0.8rem; opacity: 0.7">⏱️ Time Estimate: ${data.today_action.time_estimate}</div>
        </div>
    `;

    // 3. Timeline Stepper
    data.steps.forEach((step, index) => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="timeline-marker"></div>
            <div class="timeline-content">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight: 700;">${step.title}</div>
                    <span style="font-size: 0.7rem; color: var(--accent)">${step.timeline_hint || ''}</span>
                </div>
                <div class="details">
                    ${step.description}
                    <a href="#" class="action-cta">${step.cta}</a>
                </div>
            </div>
        `;
        item.addEventListener('click', () => item.classList.toggle('expanded'));
        timelineStepper.appendChild(item);
    });

    // 4. Reasoning Panel
    reasoningSlot.innerHTML = '';
    data.reasoning_log.forEach(log => {
        const div = document.createElement('div');
        div.className = 'reasoning-item';
        div.innerHTML = `
            <div style="font-weight: 600; font-size: 0.85rem;">${log.agent_name}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.3;">${log.summary}</div>
            <div class="reasoning-meta">
                <span>Confidence: ${intConfidence(log.confidence)}%</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${log.confidence * 100}%"></div>
            </div>
        `;
        reasoningSlot.appendChild(div);
    });
}

function intConfidence(val) {
    return Math.round(val * 100);
}
