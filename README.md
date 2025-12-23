# GAIA - Global AI-powered Impact Assessment

A revolutionary multi-agent AI system for sustainable finance intelligence, featuring adversarial debate for greenwashing detection and SDG impact quantification.

## Overview

GAIA (Global AI-powered Impact Assessment) is a comprehensive ESG (Environmental, Social, Governance) and SDG (Sustainable Development Goals) analysis platform that uses multiple specialized AI agents working in concert with adversarial debate methodology to provide accurate, verified sustainability assessments for investors and financial institutions.

### Key Features

- **6 Specialized AI Agents**: Sentinel, Veritas, Pulse, Regulus, Impact, and Orchestrator
- **Adversarial Debate System**: Agents challenge each other's findings for robust analysis
- **SDG Impact Quantification**: Measurable impact per dollar invested across all 17 SDGs
- **Real-time Analysis**: WebSocket-powered live updates during analysis
- **Blockchain Audit Trail**: Immutable verification of all findings
- **Satellite Imagery Analysis**: Environmental impact detection via satellite data
- **Supply Chain Transparency**: Deep visibility into supplier sustainability

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GAIA Platform                                │
├─────────────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                                       │
│  ├── Analysis Dashboard                                              │
│  ├── Agent Visualization                                             │
│  ├── SDG Impact Display                                              │
│  └── Real-time WebSocket Updates                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + Python)                                          │
│  ├── REST API Endpoints                                              │
│  ├── WebSocket Server                                                │
│  └── Analysis Service                                                │
├─────────────────────────────────────────────────────────────────────┤
│  Agent System                                                        │
│  ├── Sentinel - Environmental Monitoring (Satellite/Sensors)        │
│  ├── Veritas - Supply Chain Verification                            │
│  ├── Pulse - Sentiment & News Analysis                              │
│  ├── Regulus - Regulatory Compliance Intelligence                   │
│  ├── Impact - SDG Impact Quantification                             │
│  └── Orchestrator - Meta-Agent & Adversarial Debate                 │
├─────────────────────────────────────────────────────────────────────┤
│  Data Layer                                                          │
│  ├── PostgreSQL / SQLite Database                                   │
│  ├── Redis Cache                                                     │
│  └── Blockchain Audit Trail                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent System

### Sentinel Agent - Environmental Monitoring
- Satellite imagery analysis for deforestation, pollution detection
- Environmental sensor data processing
- Facility expansion monitoring
- Biodiversity impact assessment

### Veritas Agent - Supply Chain Verification
- Supply chain mapping and transparency analysis
- Blockchain record verification
- Supplier certification validation
- Conflict minerals and forced labor detection

### Pulse Agent - Sentiment Analysis
- News and media sentiment tracking
- Social media analysis
- Public perception monitoring
- Controversy detection

### Regulus Agent - Regulatory Compliance
- Monitor regulations across 190+ jurisdictions
- Predict regulatory actions
- Track enforcement patterns
- Calculate compliance scores

### Impact Agent - SDG Quantification
- Map investments to UN SDG outcomes
- Quantify impact per dollar invested:
  - Lives improved per $1M
  - CO2 avoided per $1M
  - Jobs created per $1M
  - Clean water provided per $1M

### Orchestrator Agent - Meta-Coordination
- Coordinate all specialized agents
- Implement adversarial debate system
- Resolve conflicts between agent findings
- Build consensus and final scoring

### NEXUS Agent - Financial Inclusion Intelligence
- Analyze access to financial services for underserved populations
- Track credit inclusion metrics (microloans, first-time borrowers)
- Measure gender-based financial inclusion (SDG 5)
- Assess geographic reach (rural, last-mile communities)
- Monitor services for vulnerable populations (refugees, youth, elderly)
- Evaluate affordability of financial products
- Detect "inclusion washing" - false claims about serving underserved

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (optional)
- Redis (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
cd gaia-project

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python main.py
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Start company analysis |
| GET | `/api/v1/analyze/{id}` | Get analysis status |
| GET | `/api/v1/analyze/{id}/results` | Get complete results |
| DELETE | `/api/v1/analyze/{id}` | Cancel analysis |
| WS | `/ws/analyze/{id}` | Real-time updates |

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies` | List analyzed companies |
| GET | `/api/v1/companies/{ticker}` | Get company details |
| POST | `/api/v1/companies/search` | Search companies |
| GET | `/api/v1/companies/{ticker}/compare` | Compare companies |

### SDG Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sdg/goals` | List all 17 SDG goals |
| GET | `/api/v1/sdg/impact/{ticker}` | Get SDG impact analysis |
| POST | `/api/v1/sdg/portfolio` | Analyze portfolio SDG impact |

### Financial Inclusion

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/inclusion/analyze` | Start inclusion analysis |
| GET | `/api/v1/inclusion/analyze/{id}` | Get inclusion results |
| GET | `/api/v1/inclusion/segments` | List underserved segments |
| GET | `/api/v1/inclusion/channels` | List delivery channels |
| POST | `/api/v1/inclusion/portfolio` | Portfolio inclusion analysis |
| POST | `/api/v1/inclusion/compare` | Compare companies |
| GET | `/api/v1/inclusion/benchmarks/{industry}` | Industry benchmarks |
| GET | `/api/v1/inclusion/impact-calculator` | Calculate projected impact |

## Usage Example

### Starting an Analysis

```javascript
// Start analysis
const response = await fetch('/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    company_name: 'Apple Inc.',
    include_satellite: true,
    include_sentiment: true,
    include_supply_chain: true,
    debate_rounds: 3
  })
});

const { analysis_id, websocket_url } = await response.json();

// Connect to WebSocket for real-time updates
const ws = new WebSocket(`ws://localhost:8000${websocket_url}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data.type, data.progress + '%');

  if (data.type === 'completed') {
    console.log('Final score:', data.results.overall_score);
  }
};
```

### Response Structure

```json
{
  "analysis_id": "uuid-here",
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "status": "completed",
  "overall_score": 78.5,
  "risk_level": "LOW",
  "recommendation": "Consider investing with minor due diligence",
  "esg_scores": {
    "environmental": 72.3,
    "social": 85.2,
    "governance": 88.5,
    "overall": 78.5
  },
  "sdg_impact": {
    "7": 85.0,
    "8": 72.5,
    "13": 68.0
  },
  "top_sdgs": [
    {"sdg": 7, "name": "Affordable and Clean Energy", "impact": 85.0},
    {"sdg": 8, "name": "Decent Work and Economic Growth", "impact": 72.5}
  ],
  "strengths": ["Strong governance", "Renewable energy commitment"],
  "weaknesses": ["Supply chain transparency gaps"],
  "debate_summary": {
    "total_rounds": 3,
    "consensus_reached": true
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI agents | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `DATABASE_URL` | Database connection | sqlite:///./gaia.db |
| `REDIS_URL` | Redis connection | redis://localhost:6379 |
| `NASA_EARTHDATA_API_KEY` | NASA satellite data | Optional |
| `ESA_COPERNICUS_API_KEY` | ESA Copernicus data | Optional |
| `BLOCKCHAIN_ENABLED` | Enable blockchain audit | true |
| `ADVERSARIAL_DEBATE_ROUNDS` | Debate rounds | 3 |

## Financial Inclusion Metrics

GAIA measures financial inclusion impact across underserved populations:

| Segment | Metrics | SDG Alignment |
|---------|---------|---------------|
| Unbanked | Accounts opened per $1M, Mobile users enabled | SDG 1, 8, 10 |
| Women | Women entrepreneurs funded, Gender parity index | SDG 5, 8 |
| Rural | Rural coverage %, Last-mile communities reached | SDG 9, 11 |
| Youth | Youth accounts, Financial literacy programs | SDG 4, 8 |
| Refugees | Refugees served, ID-less product availability | SDG 10, 16 |
| Micro-Entrepreneurs | Microloans per $1M, First-time borrowers | SDG 1, 8 |

### Inclusion Washing Detection

Similar to greenwashing detection, GAIA identifies "inclusion washing":
- Impact inflation (overstated reach claims)
- Cherry-picked geographic metrics
- Token women's products without real impact
- Predatory pricing disguised as inclusion
- Phantom financial literacy programs

## SDG Impact Metrics

GAIA quantifies impact across all 17 UN Sustainable Development Goals:

| SDG | Name | Key Metrics |
|-----|------|-------------|
| 1 | No Poverty | Lives improved per $1M |
| 2 | Zero Hunger | People fed per $1M |
| 3 | Good Health | Healthcare access per $1M |
| 4 | Quality Education | Students educated per $1M |
| 5 | Gender Equality | Women empowered per $1M |
| 6 | Clean Water | Liters clean water per $1M |
| 7 | Clean Energy | MWh clean energy per $1M |
| 8 | Decent Work | Jobs created per $1M |
| 9 | Industry/Innovation | R&D impact per $1M |
| 10 | Reduced Inequalities | Inequality reduction score |
| 11 | Sustainable Cities | Housing units per $1M |
| 12 | Responsible Consumption | Waste reduced per $1M |
| 13 | Climate Action | Tons CO2 avoided per $1M |
| 14 | Life Below Water | Marine area protected per $1M |
| 15 | Life on Land | Hectares restored per $1M |
| 16 | Peace & Justice | Institutions strengthened |
| 17 | Partnerships | Partnerships formed |

## Technology Stack

### Backend
- **FastAPI**: High-performance async Python framework
- **Pydantic v2**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **Redis**: Caching and WebSocket support
- **Structlog**: Structured logging

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **Framer Motion**: Animations
- **Recharts**: Data visualization

### AI/ML
- **OpenAI GPT-4**: Agent reasoning
- **Anthropic Claude**: Alternative AI backend
- **Transformers**: NLP processing
- **NumPy/Pandas**: Data analysis

### Infrastructure
- **Docker**: Containerization
- **PostgreSQL**: Production database
- **Redis**: Caching layer
- **Prometheus**: Metrics collection

## Project Structure

```
gaia-project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   ├── agents/              # AI agent implementations
│   │   ├── base_agent.py    # Base agent class
│   │   ├── sentinel_agent.py
│   │   ├── veritas_agent.py
│   │   ├── regulus_agent.py
│   │   ├── impact_agent.py
│   │   └── orchestrator_agent.py
│   ├── models/              # Pydantic data models
│   │   ├── company.py
│   │   ├── assessment.py
│   │   ├── agent_models.py
│   │   ├── evidence.py
│   │   └── sdg.py
│   ├── routes/              # API endpoints
│   │   ├── analysis.py
│   │   ├── companies.py
│   │   └── sdg.py
│   ├── services/            # Business logic
│   │   └── analysis_service.py
│   ├── utils/               # Utilities
│   │   ├── blockchain.py
│   │   ├── scoring.py
│   │   └── helpers.py
│   └── data/                # Sample data
│       └── sample_companies.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── AnalysisDashboard.tsx
│   │   │   ├── AgentVisualization.tsx
│   │   │   ├── SDGImpact.tsx
│   │   │   ├── GreenwashingAlert.tsx
│   │   │   └── ESGScoreCard.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- UN Sustainable Development Goals framework
- NASA Earthdata for satellite imagery
- ESA Copernicus for environmental data
- Global Reporting Initiative (GRI) standards
- Sustainability Accounting Standards Board (SASB)

## Contact

For questions and support:
- GitHub Issues: Open an issue in this repository
- Email: support@gaia-project.com

---

**GAIA** - Revolutionizing sustainable finance through AI-powered transparency
