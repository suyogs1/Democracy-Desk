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

    // UI Reset & Accessibility
    sendBtn.disabled = true;
    form.setAttribute('aria-busy', 'true');
    const originalBtnText = sendBtn.textContent;
    sendBtn.textContent = 'Analyzing...';
    
    explanationBox.innerHTML = '<div class="loading-state" aria-live="polite">Processing your request with multi-agent intelligence...</div>';
    timelineStepper.innerHTML = '';
    todayActionSlot.innerHTML = '';

    try {
        // Detect environment and set base URL
        const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://localhost:8000' 
            : ''; // Cloud Run uses same origin or relative or configured URL

        const response = await fetch(`${API_BASE}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                state: stateSelector.value,
                mode: modeSelector.value,
                recaptcha_token: "demo_token" // Placeholder for reCAPTCHA integration
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'API Error');
        }

        const data = await response.json();
        renderResponse(data);
        
        // Accessibility: Move focus to the explanation for screen readers
        explanationBox.setAttribute('tabindex', '-1');
        explanationBox.focus();
        
    } catch (error) {
        explanationBox.innerHTML = `<div class="error-msg" role="alert" style="color: var(--danger)">
            <strong>Error:</strong> ${error.message}. Please try again later.
        </div>`;
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = originalBtnText;
        form.setAttribute('aria-busy', 'false');
    }
});

function renderResponse(data) {
    // 1. Final Explanation
    explanationBox.innerHTML = `<h3>Your Guide</h3><p>${data.final_explanation}</p>`;

    // 2. Today Action Widget
    todayActionSlot.innerHTML = `
        <div class="today-widget" role="complementary" aria-label="Immediate Action Recommendation">
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
        item.setAttribute('role', 'button');
        item.setAttribute('tabindex', '0');
        item.setAttribute('aria-expanded', 'false');
        item.setAttribute('aria-label', `Step ${index + 1}: ${step.title}. Click to expand details.`);
        
        item.innerHTML = `
            <div class="timeline-marker"></div>
            <div class="timeline-content">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight: 700;">${step.title}</div>
                    <span style="font-size: 0.7rem; color: var(--accent)">${step.timeline_hint || ''}</span>
                </div>
                <div class="details">
                    ${step.description}
                    <a href="#" class="action-cta" onclick="event.stopPropagation()">View More Region Info</a>
                </div>
            </div>
        `;

        const toggleExpand = () => {
            const isExpanded = item.classList.toggle('expanded');
            item.setAttribute('aria-expanded', isExpanded);
        };

        item.addEventListener('click', toggleExpand);
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleExpand();
            }
        });
        
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
                <span>Confidence: ${Math.round(log.confidence * 100)}%</span>
            </div>
            <div class="confidence-bar" role="progressbar" aria-valuenow="${Math.round(log.confidence * 100)}" aria-valuemin="0" aria-valuemax="100">
                <div class="confidence-fill" style="width: ${log.confidence * 100}%"></div>
            </div>
        `;
        reasoningSlot.appendChild(div);
    });
}
