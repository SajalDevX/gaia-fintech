# GAIA Backend - Quick Start Guide

Get the GAIA backend running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation Steps

### 1. Navigate to Backend Directory

```bash
cd /home/sajal/Desktop/Hackathons/gaia-project/backend
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI
- Uvicorn
- Pydantic
- WebSockets
- And more...

### 4. Configure Environment

```bash
cp .env.example .env
```

**Minimum Required Configuration:**

Edit `.env` and add at least one AI API key:

```bash
# Option 1: OpenAI
OPENAI_API_KEY="sk-your-key-here"

# OR Option 2: Anthropic
ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

For basic testing, you can leave other values as defaults.

### 5. Start the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Installation

Open your browser and visit:

**API Documentation:**
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

**Health Check:**
- http://localhost:8000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "GAIA - Global AI-powered Impact Assessment",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": 1234567890.123
}
```

## Test the API

### 1. Start an Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "include_satellite": true,
    "include_sentiment": true,
    "include_supply_chain": true,
    "debate_rounds": 3
  }'
```

**Response:**
```json
{
  "analysis_id": "uuid-here",
  "status": "started",
  "ticker": "AAPL",
  "message": "Analysis started for AAPL",
  "websocket_url": "/ws/analyze/uuid-here",
  "estimated_duration": 60,
  "created_at": "2025-12-23T..."
}
```

### 2. Check Analysis Status

```bash
curl "http://localhost:8000/api/v1/analyze/{analysis_id}"
```

Replace `{analysis_id}` with the ID from step 1.

### 3. Get SDG Goals

```bash
curl "http://localhost:8000/api/v1/sdg/goals"
```

Returns all 17 Sustainable Development Goals.

### 4. Search Companies

```bash
curl -X POST "http://localhost:8000/api/v1/companies/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Apple",
    "limit": 10
  }'
```

## WebSocket Test (JavaScript)

Create a simple HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>GAIA WebSocket Test</title>
</head>
<body>
    <h1>GAIA Real-time Analysis</h1>
    <div id="status">Not connected</div>
    <div id="messages"></div>

    <script>
        // Replace with your analysis ID
        const analysisId = 'your-analysis-id-here';
        const ws = new WebSocket(`ws://localhost:8000/ws/analyze/${analysisId}`);

        ws.onopen = () => {
            document.getElementById('status').textContent = 'Connected!';
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML += `<p><strong>${data.type}:</strong> ${JSON.stringify(data, null, 2)}</p>`;

            if (data.type === 'completed') {
                console.log('Analysis completed!', data.results);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            document.getElementById('status').textContent = 'Disconnected';
        };

        // Keep connection alive
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);
    </script>
</body>
</html>
```

## Project Structure Overview

```
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── routes/                    # API endpoints
│   ├── __init__.py
│   ├── analysis.py           # Analysis endpoints
│   ├── companies.py          # Company endpoints
│   └── sdg.py               # SDG endpoints
├── services/
│   └── analysis_service.py   # Core analysis logic
├── agents/                   # AI agents (to be implemented)
├── models/                   # Database models
├── utils/                    # Utility functions
└── data/                     # Data storage
```

## Common Issues & Solutions

### Issue: Port 8000 already in use
```bash
# Use a different port
uvicorn main:app --port 8001
```

### Issue: Import errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key errors
```bash
# Check your .env file has the correct API keys
cat .env | grep API_KEY

# Make sure .env is in the same directory as main.py
```

### Issue: WebSocket connection refused
```bash
# Make sure CORS is configured correctly in .env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Documentation**: See README.md for detailed information
3. **Configure Advanced Features**: Edit .env for satellite data, blockchain, etc.
4. **Integrate with Frontend**: Connect your React/Vue/Angular app
5. **Implement Real Agents**: Replace placeholder agents with actual AI logic

## API Endpoint Summary

### Analysis
- `POST /api/v1/analyze` - Start analysis
- `GET /api/v1/analyze/{id}` - Get status
- `GET /api/v1/analyze/{id}/results` - Get results
- `DELETE /api/v1/analyze/{id}` - Cancel
- `WS /ws/analyze/{id}` - Real-time updates

### Companies
- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{ticker}` - Get details
- `POST /api/v1/companies/search` - Search
- `GET /api/v1/companies/{ticker}/timeline` - Timeline
- `GET /api/v1/companies/{ticker}/compare` - Compare

### SDG
- `GET /api/v1/sdg/goals` - List SDG goals
- `GET /api/v1/sdg/impact/{ticker}` - Get impact
- `POST /api/v1/sdg/portfolio` - Portfolio analysis
- `GET /api/v1/sdg/impact/{ticker}/timeline` - Timeline

## Development Mode

For development with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will automatically restart the server when you modify code.

## Production Deployment

For production, see README.md for:
- Docker containerization
- Database setup (PostgreSQL)
- Redis configuration
- Reverse proxy (Nginx)
- HTTPS setup
- Monitoring and logging

## Support

- **Documentation**: See README.md
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check IMPLEMENTATION_SUMMARY.md for known limitations

## Success Indicators

You'll know everything is working when:

✅ Health check returns status "healthy"
✅ API documentation loads at /docs
✅ You can POST to /analyze and get an analysis_id
✅ WebSocket connection accepts and responds to messages
✅ No errors in terminal logs

Happy coding! 🚀
