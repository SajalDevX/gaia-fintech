# GAIA - Functionality Documentation

## Overview

**GAIA (Global AI-powered Impact Assessment)** is a sustainable finance intelligence platform that uses multiple AI agents to analyze companies for ESG (Environmental, Social, Governance) compliance, SDG (Sustainable Development Goals) impact, and greenwashing detection.

---

## Core Features

### 1. Multi-Agent AI Analysis System

GAIA deploys **7 specialized AI agents** that work together to provide comprehensive sustainability assessments:

| Agent | Purpose | Data Sources |
|-------|---------|--------------|
| **Sentinel** | Environmental monitoring & impact analysis | LLM reasoning, environmental databases |
| **Veritas** | Supply chain verification & transparency | Blockchain records, certifications, SEC filings |
| **Pulse** | News sentiment & media analysis | NewsAPI, social media signals |
| **Regulus** | Regulatory compliance monitoring | SEC EDGAR, 190+ jurisdiction regulations |
| **Impact** | SDG impact quantification | Investment-to-outcome mapping |
| **NEXUS** | Financial inclusion assessment | Microfinance data, demographic reach |
| **Orchestrator** | Meta-agent coordination & adversarial debate | Synthesizes all agent outputs |

### 2. Adversarial Debate System

A unique differentiator - agents **debate each other's findings** using LLM-powered argumentation:

- Agents present findings with evidence
- Opposing viewpoints are generated
- LLM acts as debate moderator
- Conflicts are resolved through consensus
- Greenwashing signals are detected through inconsistencies

### 3. ESG Scoring

Comprehensive scoring across three pillars:

- **Environmental (E)**: Carbon footprint, emissions, resource usage, biodiversity impact
- **Social (S)**: Labor practices, community impact, diversity, human rights
- **Governance (G)**: Board structure, transparency, ethics, risk management

Each component scored 0-100, with overall weighted score.

### 4. SDG Impact Quantification

Maps company activities to all **17 UN Sustainable Development Goals**:

- SDG 1: No Poverty
- SDG 2: Zero Hunger
- SDG 3: Good Health
- SDG 4: Quality Education
- SDG 5: Gender Equality
- SDG 6: Clean Water
- SDG 7: Affordable Energy
- SDG 8: Decent Work
- SDG 9: Industry & Innovation
- SDG 10: Reduced Inequalities
- SDG 11: Sustainable Cities
- SDG 12: Responsible Consumption
- SDG 13: Climate Action
- SDG 14: Life Below Water
- SDG 15: Life on Land
- SDG 16: Peace & Justice
- SDG 17: Partnerships

**Quantified metrics per $1M invested:**
- Lives improved
- CO2 emissions avoided (tons)
- Jobs created
- Clean water provided (liters)

### 5. Greenwashing Detection

Identifies sustainability claim inconsistencies:

- **Claim vs. Evidence gaps**: Stated goals vs. actual performance
- **Impact inflation**: Overstated environmental benefits
- **Cherry-picked metrics**: Selective data presentation
- **Token gestures**: Minimal efforts marketed as major initiatives
- **Scope manipulation**: Narrow boundaries to exclude negative impacts

### 6. Financial Inclusion Assessment

Measures impact on underserved populations:

| Segment | Metrics |
|---------|---------|
| **Unbanked** | Accounts opened per $1M invested |
| **Women** | Female entrepreneurs funded, gender parity index |
| **Rural** | Last-mile communities reached |
| **Youth** | Financial literacy program participants |
| **Refugees** | Displaced persons served |
| **Micro-entrepreneurs** | First-time borrowers supported |

### 7. Blockchain Audit Trail

Immutable verification of all findings:

- Every agent finding recorded on-chain
- Debate arguments preserved
- Evidence hashes stored
- Tamper-proof assessment history
- Third-party verification enabled

### 8. Real-Time Analysis Updates

WebSocket-based live progress tracking:

- Agent activation status
- Current analysis phase
- Debate round notifications
- Progressive result delivery

---

## Technical Architecture

### No LangChain - Custom Multi-Agent Framework

This project does **NOT use LangChain**. Instead, it implements a custom agent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Custom Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BaseAgent (Abstract Class)                                  │
│  ├── analyze() - Core analysis method                        │
│  ├── collect_data() - Evidence gathering                     │
│  ├── calculate_confidence() - Confidence scoring             │
│  ├── execute_with_timeout() - Timeout protection             │
│  ├── fetch_with_retry() - Retry logic with tenacity          │
│  └── challenge_finding() - Adversarial debate support        │
│                                                              │
│  MultiProviderLLMClient                                      │
│  ├── Gemini (google-generativeai SDK)                        │
│  ├── OpenAI (direct API via httpx)                           │
│  ├── Claude (direct API via httpx)                           │
│  ├── Load balancing (round-robin, random, weighted)          │
│  ├── Automatic fallback on failure                           │
│  └── Response caching with TTL                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Why Not LangChain?

1. **Lightweight**: Direct API calls reduce dependencies and overhead
2. **Control**: Full control over retry logic, caching, and error handling
3. **Multi-provider**: Custom load balancing across Gemini, OpenAI, Claude
4. **Specialized**: Domain-specific agent behaviors for ESG/SDG analysis
5. **Performance**: Optimized for this specific use case

### Agent Communication Flow

```
User Request (Company Ticker)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    Analysis Service                        │
│  1. Initialize all 6 specialized agents                    │
│  2. Execute agents in parallel (asyncio)                   │
│  3. Collect findings with evidence trails                  │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                       │
│  1. Synthesize findings from all agents                    │
│  2. Run adversarial debate rounds                          │
│  3. Detect greenwashing signals                            │
│  4. Build consensus on final scores                        │
│  5. Record to blockchain audit trail                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
   Final Assessment
   (ESG Scores, SDG Impact, Recommendations)
```

---

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
| GET | `/api/v1/companies/compare` | Compare multiple companies |

### SDG

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sdg/goals` | List all 17 SDG goals |
| GET | `/api/v1/sdg/impact/{ticker}` | Get SDG impact for company |

### Financial Inclusion

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/inclusion/analyze` | Analyze financial inclusion |
| GET | `/api/v1/inclusion/{ticker}` | Get inclusion metrics |

### Blockchain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/blockchain/status` | Blockchain network status |
| GET | `/api/v1/blockchain/audit/{id}` | Get audit trail |

---

## Data Models

### Analysis Request
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "options": {
    "include_sdg": true,
    "include_inclusion": true,
    "run_debate": true
  }
}
```

### Analysis Response
```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "esg_scores": {
    "environmental": 75,
    "social": 82,
    "governance": 88,
    "overall": 81
  },
  "risk_level": "LOW",
  "recommendation": "BUY",
  "sdg_impact": [...],
  "greenwashing_signals": [...],
  "debate_summary": {...},
  "blockchain_hash": "0x..."
}
```

---

## External Data Integrations

| Service | Purpose | Authentication |
|---------|---------|----------------|
| **NewsAPI** | News sentiment analysis | API Key |
| **Alpha Vantage** | Financial data | API Key |
| **SEC EDGAR** | Regulatory filings | None (public) |
| **NASA Earthdata** | Satellite imagery (Stage 2) | API Key |
| **ESA Copernicus** | Environmental data (Stage 2) | API Key |

---

## Risk Assessment Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| MINIMAL | 0-20 | Excellent sustainability practices |
| LOW | 21-40 | Good practices with minor concerns |
| MODERATE | 41-60 | Some areas need improvement |
| HIGH | 61-80 | Significant sustainability risks |
| CRITICAL | 81-100 | Severe risks, avoid investment |

---

## Investment Recommendations

| Rating | Meaning |
|--------|---------|
| STRONG_BUY | Excellent ESG profile, high SDG impact |
| BUY | Good sustainability practices |
| HOLD | Mixed signals, monitor closely |
| SELL | Concerning sustainability issues |
| STRONG_SELL | Critical ESG failures, divest |

---

## Target Users

1. **Institutional Investors**: ESG-focused portfolio management
2. **Asset Managers**: Sustainable fund construction
3. **Financial Advisors**: Client sustainability screening
4. **Corporate Sustainability Teams**: Benchmarking and improvement
5. **Regulators**: Compliance verification
6. **NGOs**: Impact assessment and reporting

---

## Technology Stack Summary

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI (Python) |
| Frontend Framework | React + TypeScript |
| LLM Providers | Gemini, OpenAI, Claude |
| Real-time | WebSockets |
| Database | SQLite/PostgreSQL |
| Cache | Redis |
| Containerization | Docker Compose |

---

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and add API keys
3. Run `docker-compose up` or start services individually
4. Access frontend at `http://localhost:5173`
5. API available at `http://localhost:8000`

---

*GAIA - Transparent, Verified Sustainability Intelligence*
