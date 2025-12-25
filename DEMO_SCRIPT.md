# GAIA Demo Script - Greenwashing Detection

## Demo Duration: 5-7 minutes

---

## Setup Checklist

Before the demo:
```bash
# Terminal 1: Start Backend
cd backend
python main.py
# Verify: http://localhost:8000/health

# Terminal 2: Start Frontend
cd frontend
npm run dev
# Verify: http://localhost:5173
```

---

## Demo Flow

### 1. Introduction (30 seconds)

**Script:**
> "GAIA is a revolutionary multi-agent AI system for sustainable finance intelligence. What makes it unique is our adversarial debate system - 7 specialized AI agents that analyze companies and actively challenge each other's findings to detect greenwashing."

**Action:** Show the landing page with the animated globe

---

### 2. Agent Overview (30 seconds)

**Script:**
> "We have 7 specialized agents:
> - **Sentinel** monitors environmental data
> - **Veritas** verifies supply chains
> - **Pulse** analyzes news sentiment
> - **Regulus** checks regulatory compliance
> - **Impact** quantifies SDG impact
> - **NEXUS** assesses financial inclusion
> - **Orchestrator** runs the adversarial debate"

**Action:** Point to the agent feature cards on the landing page

---

### 3. Live Analysis - Good Company (1.5 minutes)

**Script:**
> "Let's analyze Apple, a company with strong ESG practices."

**Actions:**
1. Type "AAPL" in the search bar
2. Click "Analyze"
3. Watch agents activate one by one
4. Point out the ESG Radar Chart
5. Show the SDG impact breakdown

**Talking Points:**
- "Notice how agents work in parallel"
- "Real-time WebSocket updates"
- "Each finding is backed by evidence from real APIs"

---

### 4. Greenwashing Detection Demo (2 minutes)

**Script:**
> "Now, let's analyze Exxon Mobil - an oil company. Watch how our adversarial debate system detects greenwashing."

**Actions:**
1. Type "XOM" in the search bar
2. Click "Analyze"
3. Watch for the **Debate Visualization** panel to appear
4. Point out the split-screen debate view

**Talking Points:**
> "Here's where GAIA shines. Watch the Orchestrator initiate the adversarial debate."
>
> "Sentinel detected Exxon's renewable energy investments..."
>
> "But Pulse found news about ongoing fossil fuel expansion..."
>
> "The agents DEBATE this contradiction in real-time!"

**Greenwashing Signals to Highlight:**
- Claims vs. Evidence gaps
- Cherry-picked environmental metrics
- Scope limitations in carbon reporting
- Token renewable investments vs. core business

---

### 5. Blockchain Audit Trail (30 seconds)

**Script:**
> "Every finding, every debate argument, is recorded on an immutable blockchain audit trail."

**Action:** Scroll to the Blockchain Audit Trail section

**Talking Points:**
- "Tamper-proof verification"
- "Smart contracts trigger alerts for ESG violations"
- "Third-party auditors can verify our findings"

---

### 6. SDG Impact Quantification (30 seconds)

**Script:**
> "We don't just score - we quantify real-world impact per dollar invested."

**Action:** Point to the SDG Impact section

**Talking Points:**
- "Lives improved per $1M"
- "CO2 avoided per $1M"
- "Maps directly to UN Sustainable Development Goals"

---

### 7. Compare: XOM vs AAPL (30 seconds)

**Script:**
> "The contrast is clear. Apple scores 75+ with minimal greenwashing signals. Exxon shows multiple inconsistencies detected through our adversarial debate."

**Action:** Show side-by-side if possible, or recall the scores

---

### 8. Technical Differentiators (30 seconds)

**Script:**
> "What makes GAIA different:
> 1. **Multi-LLM Architecture** - We use Gemini, GPT-4, and Claude with automatic fallback
> 2. **Adversarial Debate** - Agents actively challenge each other
> 3. **Real Data** - NewsAPI, Alpha Vantage, SEC EDGAR integration
> 4. **Blockchain Verification** - Immutable audit trail"

---

### 9. Call to Action (15 seconds)

**Script:**
> "GAIA transforms ESG analysis from a black box to a transparent, verifiable, AI-powered system that actively fights greenwashing. Thank you!"

---

## Backup Demo Companies

If API issues occur, use these pre-tested tickers:

| Ticker | Company | Expected Outcome |
|--------|---------|------------------|
| AAPL | Apple | High ESG, minimal greenwashing |
| MSFT | Microsoft | High ESG, good governance |
| TSLA | Tesla | High Environmental, some Social concerns |
| XOM | Exxon | Moderate ESG, **greenwashing detected** |
| NKE | Nike | Good overall, supply chain scrutiny |

---

## Common Q&A

**Q: How long does analysis take?**
> A: 30-60 seconds for a full analysis with 7 agents and 3 debate rounds.

**Q: Is this using real data?**
> A: Yes! We integrate NewsAPI for sentiment, Alpha Vantage for financials, and SEC EDGAR for regulatory filings.

**Q: How does the debate work?**
> A: The Orchestrator presents findings to all agents. Each agent can challenge findings with counter-evidence. The LLM synthesizes arguments and builds consensus.

**Q: What's next for GAIA?**
> A: Stage 2 includes satellite imagery from NASA Earthdata, real blockchain deployment, and analysis of 1000+ companies.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `.env` file has API keys |
| WebSocket not connecting | Fallback polling is automatic |
| API rate limits | Graceful degradation provides fallback data |
| Slow analysis | Check LLM API status |

---

## Demo Environment URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Blockchain Status**: http://localhost:8000/api/v1/blockchain/status
