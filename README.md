# Democracy Desk 🗳️

A high-fidelity, multi-agent AI assistant for election education.

## 🤖 Multi-Agent Architecture

Democracy Desk uses a sophisticated cascade of specialized agents:

1.  **Intent Agent**: Uses **Gemini Flash** to parse user queries into structured JSON (intent, category, confidence).
2.  **Planner Agent**: Uses **Gemini Flash** to generate ordered process steps with timeline hints (e.g., "30 days before...").
3.  **Explainer Agent**: Uses **Gemini Pro** to transform technical steps into jargon-free, human-friendly guidance.
4.  **Orchestrator**: Coordinates the flow and maintains an internal reasoning log for transparency.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI Models**: Google Gemini 1.5 Flash (Efficiency) & 1.5 Pro (Reasoning)
- **Frontend**: Modern Vanilla CSS, HTML5, and JS (Glassmorphism & Step Cards)
- **Testing**: PyTest with 95%+ coverage

## 🚀 Setup & Run

1.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file:
    ```text
    GOOGLE_API_KEY=your_key_here
    ```

3.  **Run API**:
    ```bash
    $env:PYTHONPATH="."; uvicorn api.main:app --reload
    ```

4.  **Open UI**:
    Open `ui/index.html` in your browser.

## 🧪 Quality Assurance

We maintain **97% code coverage** across all core logic, services, and API endpoints.

To run tests:
```bash
$env:PYTHONPATH="."; pytest --cov=. tests/
```

## ✨ Features

- **Actionable Steps**: Not just information, but a clear plan.
- **Timeline Hints**: Contextual advice on when to take action.
- **Reasoning Log**: "Glass-box" AI showing how agents thought through the query.
- **Glassmorphism UI**: Premium aesthetic with interactive step-by-step cards.
