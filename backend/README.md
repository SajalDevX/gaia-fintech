# GAIA Backend - FastAPI Service

Global AI-powered Impact Assessment System - Backend API Service

## Overview

The GAIA backend is a comprehensive FastAPI-based service that orchestrates a multi-agent AI system for ESG (Environmental, Social, Governance) and SDG (Sustainable Development Goals) analysis of companies.

### Key Features

- **Multi-Agent Analysis System**: 6 specialized AI agents working in parallel
- **Adversarial Debate**: AI agents challenge each other's findings for robust analysis
- **Real-time Updates**: WebSocket support for live analysis progress
- **Comprehensive ESG/SDG Scoring**: Detailed impact assessment across all 17 SDGs
- **Satellite Imagery Analysis**: Environmental impact detection via satellite data
- **Supply Chain Analysis**: Deep dive into supply chain sustainability
- **Sentiment Analysis**: Real-time sentiment from news and social media

## Architecture

### Agent System

1. **Financial Agent**: Analyzes financial data, SEC filings, ESG reports
2. **Environmental Agent**: Satellite imagery, carbon emissions, resource usage
3. **Social Agent**: Labor practices, human rights, community impact
4. **Governance Agent**: Board structure, ethics, transparency
5. **Sentiment Agent**: News, social media, public perception
6. **Supply Chain Agent**: Supplier analysis, tier-n visibility, risk assessment

### Analysis Flow

```
1. Parallel Agent Execution
   ↓
2. Adversarial Debate (3 rounds default)
   ↓
3. Consensus Building
   ↓
4. Final Assessment Generation
   ↓
5. Results Storage & Delivery
```

## Installation

### Prerequisites

- Python 3.10+
- Redis (optional, for WebSocket scaling)
- PostgreSQL (optional, SQLite used by default)

### Setup

1. Clone the repository:
```bash
cd /home/sajal/Desktop/Hackathons/gaia-project/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run the server:
```bash
python main.py
# Or with uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

#### Analysis

- `POST /api/v1/analyze` - Start company analysis
- `GET /api/v1/analyze/{id}` - Get analysis status
- `GET /api/v1/analyze/{id}/results` - Get complete results
- `DELETE /api/v1/analyze/{id}` - Cancel ongoing analysis
- `WS /ws/analyze/{id}` - WebSocket for real-time updates

#### Companies

- `GET /api/v1/companies` - List analyzed companies
- `GET /api/v1/companies/{ticker}` - Get company details
- `POST /api/v1/companies/search` - Search companies
- `GET /api/v1/companies/{ticker}/timeline` - Score evolution
- `GET /api/v1/companies/{ticker}/compare` - Compare companies
- `GET /api/v1/companies/{ticker}/peers` - Get peer companies

#### SDG Analysis

- `GET /api/v1/sdg/goals` - List all 17 SDG goals
- `GET /api/v1/sdg/impact/{ticker}` - Get SDG impact analysis
- `POST /api/v1/sdg/portfolio` - Analyze portfolio SDG impact
- `GET /api/v1/sdg/impact/{ticker}/goal/{sdg_number}` - Specific SDG detail
- `GET /api/v1/sdg/impact/{ticker}/timeline` - SDG impact over time

### WebSocket Protocol

Connect to `/ws/analyze/{analysis_id}` for real-time updates.

**Message Types:**

```json
{
  "type": "status|progress|agent_complete|debate_round|completed|error",
  "progress": 0-100,
  "message": "Description",
  "timestamp": "ISO-8601"
}
```

**Client Messages:**

```json
{
  "type": "ping"
}
```

Server responds with `pong`.

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

**Required:**
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For AI agent processing
- `DATABASE_URL` - Database connection (default: SQLite)

**Optional:**
- `NASA_EARTHDATA_API_KEY` - For satellite imagery
- `ESA_COPERNICUS_API_KEY` - For Copernicus satellite data
- `REDIS_URL` - For WebSocket scaling
- `BLOCKCHAIN_ENABLED` - Enable blockchain attestation

### Agent Configuration

Adjust agent behavior in `config.py`:

```python
AGENT_TIMEOUT_SECONDS = 60
MAX_CONCURRENT_AGENTS = 10
ADVERSARIAL_DEBATE_ROUNDS = 3
```

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── routes/
│   ├── __init__.py       # Router configuration
│   ├── analysis.py       # Analysis endpoints
│   ├── companies.py      # Company endpoints
│   └── sdg.py           # SDG endpoints
├── services/
│   └── analysis_service.py  # Core analysis orchestration
├── agents/               # AI agent implementations
├── models/              # Database models
├── utils/               # Utility functions
└── data/                # Data storage
```

### Adding New Agents

1. Implement agent in `agents/` directory
2. Register in `AnalysisService._initialize_agents()`
3. Add execution method in `AnalysisService`
4. Update debate logic to include new agent findings

### Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=. tests/
```

## API Examples

### Start Analysis

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

### Get Analysis Status

```bash
curl "http://localhost:8000/api/v1/analyze/{analysis_id}"
```

### Search Companies

```bash
curl -X POST "http://localhost:8000/api/v1/companies/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Apple",
    "limit": 10,
    "include_analysis": true
  }'
```

### Analyze Portfolio SDG Impact

```bash
curl -X POST "http://localhost:8000/api/v1/sdg/portfolio" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "weights": {
      "AAPL": 0.4,
      "MSFT": 0.35,
      "GOOGL": 0.25
    }
  }'
```

## WebSocket Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analyze/YOUR_ANALYSIS_ID');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);

  if (data.type === 'completed') {
    console.log('Analysis completed!', data.results);
  }
};

// Keep connection alive
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "timestamp": 1234567890.123
}
```

**Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `500` - Internal Server Error

## Performance

- Parallel agent execution for speed
- WebSocket for efficient real-time updates
- Redis caching for frequently accessed data
- Database query optimization
- Rate limiting to prevent abuse

## Security

- CORS middleware configured
- Input validation with Pydantic
- API key authentication (TODO)
- Rate limiting
- SQL injection prevention via SQLAlchemy
- XSS prevention in responses

## Monitoring

- Structured logging with `structlog`
- Prometheus metrics endpoint at `/metrics`
- Health check at `/health`
- Request timing in response headers

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Repository URL]
- Email: support@gaia-project.com
- Documentation: [Docs URL]

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Roadmap

- [ ] Implement actual AI agent logic
- [ ] Add database models and persistence
- [ ] Integrate real satellite imagery APIs
- [ ] Add authentication and authorization
- [ ] Implement caching layer
- [ ] Add comprehensive test suite
- [ ] Deploy on cloud infrastructure
- [ ] Add blockchain attestation
- [ ] Implement PDF/Excel export
- [ ] Add GraphQL support
