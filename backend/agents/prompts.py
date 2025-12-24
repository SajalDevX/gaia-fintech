"""
Agent Prompts Module for GAIA
Contains system prompts and analysis templates for all agents.
"""

# System prompts define each agent's personality and expertise
AGENT_SYSTEM_PROMPTS = {
    "sentinel": """You are Sentinel, an environmental monitoring AI agent specializing in ESG analysis.

Your expertise includes:
- Satellite imagery interpretation and land use analysis
- Deforestation and vegetation change detection (NDVI analysis)
- Pollution monitoring (air quality, water contamination, soil degradation)
- Carbon emissions and climate impact assessment
- Biodiversity and ecosystem health evaluation
- Facility expansion and environmental footprint tracking

You analyze environmental data critically and provide evidence-based findings.
Always quantify impacts where possible and cite specific data sources.
Rate severity accurately: CRITICAL for immediate environmental harm, HIGH for significant ongoing issues,
MEDIUM for moderate concerns, LOW for minor issues, INFO for neutral observations.""",

    "veritas": """You are Veritas, a supply chain verification AI agent for ESG analysis.

Your expertise includes:
- Supply chain mapping and transparency assessment
- Supplier tier analysis (direct, indirect, sub-tier visibility)
- Certification verification (Fair Trade, ISO, B Corp, etc.)
- Conflict minerals and ethical sourcing evaluation
- Forced labor and human rights risk detection
- Shipping and logistics anomaly detection
- Blockchain and audit trail verification

You investigate supply chain claims skeptically and cross-reference multiple sources.
Flag discrepancies between stated practices and available evidence.
Focus on verifiable facts and highlight gaps in transparency.""",

    "pulse": """You are Pulse, a social sentiment and media monitoring AI agent.

Your expertise includes:
- News sentiment analysis and media coverage tracking
- Social media sentiment and trending topics
- Public perception and brand reputation assessment
- Labor practice controversies and allegations
- Community relations and stakeholder sentiment
- Consumer feedback and product safety concerns
- Activist campaigns and protest monitoring

You analyze media objectively, distinguishing between verified reports and allegations.
Identify sentiment trends over time and flag emerging reputational risks.
Consider source credibility when weighting information.""",

    "regulus": """You are Regulus, a regulatory compliance AI agent for ESG analysis.

Your expertise includes:
- Regulatory filing analysis (SEC, EPA, OSHA, etc.)
- Compliance status across multiple jurisdictions
- Enforcement actions and penalty history
- Pending investigations and legal proceedings
- Regulatory change impact assessment
- Industry-specific compliance requirements
- International regulatory frameworks (EU, UK, APAC)

You track regulatory history comprehensively and assess future compliance risks.
Quantify penalties and sanctions where known.
Highlight patterns of violations or improvement over time.""",

    "impact": """You are Impact, an SDG (Sustainable Development Goals) impact quantification agent.

Your expertise includes:
- Mapping business activities to all 17 UN SDGs
- Impact measurement and quantification
- Theory of change development
- Impact per dollar invested calculations
- Positive vs negative impact assessment
- Industry benchmarking for impact metrics
- IRIS+ and other impact measurement frameworks

You assess both positive contributions and negative externalities.
Quantify impact where possible (lives improved, CO2 avoided, jobs created, etc.).
Be balanced - recognize genuine impact while flagging impact washing.""",

    "nexus": """You are NEXUS, a financial inclusion intelligence agent.

Your expertise includes:
- Access to financial services for underserved populations
- Microfinance and inclusive lending assessment
- Gender-based financial inclusion metrics
- Rural and last-mile service delivery
- Vulnerable population service (refugees, disabled, elderly)
- Mobile money and fintech inclusion channels
- Inclusion washing detection (false claims about serving underserved)

You evaluate genuine financial inclusion impact critically.
Distinguish between marketing claims and actual service delivery.
Assess pricing fairness and predatory practice risks.""",

    "orchestrator": """You are the Orchestrator, a meta-agent coordinating ESG analysis across multiple specialized agents.

Your responsibilities include:
- Synthesizing findings from all specialist agents
- Identifying conflicts and contradictions between agent assessments
- Facilitating adversarial debate to stress-test findings
- Building consensus while preserving legitimate disagreements
- Detecting greenwashing and sustainability claim inconsistencies
- Producing balanced final assessments with confidence levels

You are objective and critical, challenging weak evidence and unsupported claims.
Weight findings by evidence quality and source reliability.
Acknowledge uncertainty and flag areas needing further investigation.""",
}


# Analysis prompt templates for specific tasks
ANALYSIS_PROMPT_TEMPLATES = {
    # Sentinel Agent Templates
    "environmental_analysis": """Analyze the environmental impact and practices of {company_name}.

Context and Available Data:
{data_context}

Provide a comprehensive environmental assessment covering:

1. **Carbon Footprint & Emissions**
   - Scope 1, 2, and 3 emissions if available
   - Emission reduction trends and commitments
   - Carbon neutrality or net-zero claims

2. **Environmental Compliance**
   - Regulatory violations or penalties
   - Environmental permits and their status
   - Remediation efforts for past issues

3. **Resource Management**
   - Water usage and efficiency
   - Waste management and recycling rates
   - Renewable energy adoption

4. **Ecosystem Impact**
   - Deforestation or land use changes
   - Biodiversity impacts
   - Pollution incidents (air, water, soil)

5. **Climate Risk Exposure**
   - Physical risks from climate change
   - Transition risks and opportunities
   - Climate adaptation measures

For each finding, provide:
- Severity rating (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Confidence score (0.0 to 1.0)
- Supporting evidence or data sources
- Specific metrics where available""",

    "deforestation_analysis": """Analyze deforestation and land use impacts for {company_name}.

Location/Region: {location}
Time Period: {time_period}

Available Information:
{data_context}

Assess:
1. Direct deforestation linked to operations or supply chain
2. Land use change patterns near facilities
3. Commitments to zero-deforestation and compliance
4. Certification status (FSC, RSPO, etc.)
5. Comparison to industry standards

Provide specific findings with severity ratings and confidence scores.""",

    "pollution_analysis": """Analyze pollution and environmental contamination for {company_name}.

Available Data:
{data_context}

Assess all pollution types:
1. Air pollution (emissions, particulates, toxic releases)
2. Water pollution (discharge, contamination, spills)
3. Soil contamination
4. Noise and light pollution where relevant

For each issue identified, provide severity, confidence, and evidence.""",

    # Veritas Agent Templates
    "supply_chain_analysis": """Analyze the supply chain transparency and ethics for {company_name}.

Available Information:
{data_context}

Assess:
1. **Supply Chain Visibility**
   - Tier 1, 2, and deeper supplier disclosure
   - Geographic distribution of suppliers
   - Supplier audit frequency and results

2. **Certifications & Standards**
   - Valid certifications (ISO 14001, SA8000, etc.)
   - Fair Trade or ethical sourcing certifications
   - Verification of certification claims

3. **Human Rights Risks**
   - Forced labor indicators
   - Child labor risks by geography
   - Living wage compliance

4. **Conflict Minerals & Sourcing**
   - 3TG (tin, tantalum, tungsten, gold) sourcing
   - Conflict-free declarations
   - DRC and other high-risk region exposure

5. **Transparency Gaps**
   - Missing information or disclosure gaps
   - Inconsistencies in reported data
   - Areas requiring further investigation

Provide findings with severity ratings and confidence scores.""",

    # Pulse Agent Templates
    "sentiment_analysis": """Analyze news and public sentiment for {company_name}.

Recent News Articles:
{articles_summary}

Additional Context:
{data_context}

Provide:
1. **Overall Sentiment Score** (-1.0 to 1.0, where -1 is very negative, 0 is neutral, 1 is very positive)

2. **Sentiment by Topic**
   - Environmental practices
   - Labor and workplace
   - Product quality and safety
   - Corporate governance
   - Community relations

3. **Key Positive Themes**
   - List main positive narratives with examples

4. **Key Negative Themes**
   - List main concerns or criticisms with examples

5. **Trending Concerns**
   - Emerging issues gaining media attention
   - Potential future reputational risks

6. **Source Credibility Assessment**
   - Quality of sources analyzed
   - Potential biases in coverage

Include confidence scores based on source quality and volume of coverage.""",

    "controversy_analysis": """Analyze ESG controversies and incidents for {company_name}.

Available Information:
{data_context}

Identify and assess:
1. Environmental incidents or violations
2. Labor disputes or workplace safety issues
3. Product recalls or safety concerns
4. Governance scandals or ethical breaches
5. Community conflicts or protests
6. Legal proceedings or regulatory actions

For each controversy:
- Describe the incident
- Assess severity (CRITICAL, HIGH, MEDIUM, LOW)
- Evaluate company response
- Estimate reputational impact
- Note resolution status""",

    # Regulus Agent Templates
    "regulatory_analysis": """Analyze regulatory compliance for {company_name}.

SEC Filings and Regulatory Data:
{filings_summary}

Additional Context:
{data_context}

Assess:
1. **Regulatory History**
   - Past violations and penalties
   - Enforcement actions
   - Consent decrees or settlements

2. **Current Compliance Status**
   - Active permits and their status
   - Pending investigations
   - Required disclosures and their completeness

3. **Multi-Jurisdictional Compliance**
   - US federal and state compliance
   - EU regulations (if applicable)
   - Other international requirements

4. **Regulatory Risk Outlook**
   - Upcoming regulatory changes
   - Exposure to new requirements
   - Compliance cost projections

Provide findings with severity ratings, specific regulations cited, and confidence scores.""",

    # Impact Agent Templates
    "sdg_impact_analysis": """Analyze SDG (Sustainable Development Goals) alignment for {company_name}.

Company Information:
- Industry: {industry}
- Description: {description}
- Key Products/Services: {products}

Financial Context:
{financial_data}

Map the company's activities to all 17 UN SDGs:

For each relevant SDG (1-17):
1. **Alignment Assessment**
   - Positive contributions
   - Negative externalities
   - Net impact score (-100 to +100)

2. **Impact Quantification** (where possible)
   - Specific metrics (lives improved, CO2 reduced, etc.)
   - Impact per $1M invested
   - Comparison to industry benchmarks

3. **Evidence Quality**
   - Data sources for impact claims
   - Third-party verification status
   - Confidence in impact estimates

Focus on SDGs most relevant to the company's industry and operations.
Flag any potential SDG-washing (exaggerated impact claims).""",

    # NEXUS Agent Templates
    "inclusion_analysis": """Analyze financial inclusion impact for {company_name}.

Available Information:
{data_context}

Assess across these dimensions:

1. **Access Metrics**
   - Unbanked/underbanked populations served
   - Geographic reach (urban vs rural)
   - Account penetration rates

2. **Credit Inclusion**
   - Microloan availability and terms
   - Interest rate fairness
   - Credit scoring for thin-file customers

3. **Gender Inclusion**
   - Women-focused products or services
   - Female customer base percentage
   - Women in leadership (provider perspective)

4. **Vulnerable Population Service**
   - Refugee/migrant services
   - Disability accessibility
   - Elderly-friendly services

5. **Affordability**
   - Fee structures for low-income users
   - Minimum balance requirements
   - Transaction cost accessibility

6. **Inclusion Washing Detection**
   - Marketing claims vs actual reach
   - Impact inflation indicators
   - Predatory pricing concerns

Provide specific metrics where available and flag unverified claims.""",

    # Orchestrator Templates
    "debate_support": """You are defending this finding in an adversarial debate.

Finding to Defend:
{finding_description}

Evidence Supporting This Finding:
{evidence}

Previous Arguments in This Debate:
{previous_arguments}

Current Round: {round_number} of {total_rounds}

Provide a compelling argument that:
1. Strengthens the case for this finding with logical reasoning
2. Addresses any counterarguments raised in previous rounds
3. References specific evidence to support your position
4. Acknowledges legitimate uncertainties while maintaining core conclusions

Be rigorous but fair - don't overstate the evidence.""",

    "debate_challenge": """You are challenging this finding in an adversarial debate.

Finding to Challenge:
{finding_description}

Evidence Presented:
{evidence}

Previous Arguments in This Debate:
{previous_arguments}

Current Round: {round_number} of {total_rounds}

Provide a critical challenge that:
1. Identifies weaknesses in the evidence or reasoning
2. Proposes alternative interpretations of the data
3. Highlights missing information or potential biases
4. Questions the confidence level if it seems too high or low

Be constructive - aim to stress-test the finding, not dismiss it unfairly.""",

    "debate_resolution": """Evaluate this adversarial debate and determine the outcome.

Topic: {topic}

Original Finding:
{finding_description}

Complete Debate Transcript:
{debate_transcript}

Determine:
1. **Prevailing Position**: Which side presented stronger evidence and reasoning?
2. **Final Confidence Score**: Based on debate quality (0.0 to 1.0)
3. **Consensus Reached**: Was a clear conclusion established? (true/false)
4. **Resolution Summary**: What should the final finding state?
5. **Remaining Uncertainties**: What questions remain unresolved?

Be objective and base your judgment on evidence quality, not argument style.""",

    "greenwashing_detection": """Analyze these ESG findings for potential greenwashing indicators.

Company: {company_name}

Findings from All Agents:
{findings_summary}

Check for these greenwashing patterns:

1. **Vague or Unsubstantiated Claims**
   - Generic environmental language without specifics
   - Claims without supporting data

2. **Lack of Evidence**
   - Positive claims with minimal evidence
   - Self-reported data without verification

3. **Contradictory Data**
   - Inconsistencies between different sources
   - Claims that conflict with observable data

4. **Cherry-Picking**
   - Highlighting minor positives while ignoring major negatives
   - Selective time periods or metrics

5. **Hidden Tradeoffs**
   - Green claims in one area masking problems in another
   - Offsetting rather than reducing impacts

6. **Misleading Imagery or Language**
   - "Natural" or "eco-friendly" without certification
   - Irrelevant claims (e.g., "CFC-free" when CFCs are banned)

For each detected signal:
- Signal type
- Severity (low, medium, high, critical)
- Specific description
- Evidence
- Confidence score""",

    "final_synthesis": """Synthesize the complete ESG analysis for {company_name}.

Agent Findings:
{all_findings}

Debate Outcomes:
{debate_summaries}

Greenwashing Signals:
{greenwashing_signals}

Produce a final synthesis that includes:

1. **Overall ESG Assessment**
   - Environmental score and key factors
   - Social score and key factors
   - Governance score and key factors
   - Combined ESG rating (AAA to D scale)

2. **Key Strengths**
   - Top 3-5 positive findings with high confidence

3. **Key Risks**
   - Top 3-5 concerns with severity ratings

4. **Consensus Areas**
   - Findings where all agents agree

5. **Uncertainty Areas**
   - Findings with low confidence or agent disagreement

6. **Investment Recommendation**
   - Risk level: CRITICAL, HIGH, MODERATE, LOW, MINIMAL
   - Suggested action: AVOID, CAUTION, MONITOR, ACCEPTABLE, RECOMMENDED

7. **Data Quality Assessment**
   - Overall confidence in the analysis
   - Key data gaps or limitations""",
}


def get_system_prompt(agent_name: str) -> str:
    """Get the system prompt for a specific agent."""
    return AGENT_SYSTEM_PROMPTS.get(agent_name.lower(), AGENT_SYSTEM_PROMPTS["orchestrator"])


def get_analysis_template(template_name: str) -> str:
    """Get an analysis prompt template."""
    return ANALYSIS_PROMPT_TEMPLATES.get(template_name, "")


def format_template(template_name: str, **kwargs) -> str:
    """Format an analysis template with provided variables."""
    template = get_analysis_template(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")

    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")
