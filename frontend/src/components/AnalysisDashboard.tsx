import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, AlertTriangle, Globe2, Link2, CheckCircle2, History } from 'lucide-react';
import AgentVisualization from './AgentVisualization';
import SDGImpact from './SDGImpact';
import GreenwashingAlert from './GreenwashingAlert';
import ESGScoreCard from './ESGScoreCard';
import ESGRadarChart from './ESGRadarChart';
import DebateVisualization from './DebateVisualization';
import AnalysisHistory from './AnalysisHistory';
import { AnalysisAPI, GAIA_AGENTS } from '../services/api';
import type { AnalysisResult, AgentStatus, SDGImpact as SDGImpactType, GreenwashingAlert as GreenwashingAlertType } from '../types';

// Common ticker mappings
const TICKER_MAP: Record<string, string> = {
  'apple': 'AAPL',
  'microsoft': 'MSFT',
  'tesla': 'TSLA',
  'google': 'GOOGL',
  'amazon': 'AMZN',
  'meta': 'META',
  'nvidia': 'NVDA',
  'exxon': 'XOM',
  'exxon mobil': 'XOM',
  'nike': 'NKE',
  'walmart': 'WMT',
  'coca-cola': 'KO',
  'pepsi': 'PEP',
  'chevron': 'CVX',
  'shell': 'SHEL',
  'bp': 'BP',
};

const AnalysisDashboard = () => {
  const [companyInput, setCompanyInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [blockchainStatus, setBlockchainStatus] = useState<any>(null);
  const [debateSessions, setDebateSessions] = useState<any[]>([]);
  const [greenwashingSignals, setGreenwashingSignals] = useState<any[]>([]);
  const [isDebating, setIsDebating] = useState(false);
  const [currentDebateRound, setCurrentDebateRound] = useState(0);
  const [showHistory, setShowHistory] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Handle selecting an analysis from history
  const handleSelectHistoryAnalysis = async (historyAnalysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/history/${historyAnalysisId}/full`);
      if (response.ok) {
        const data = await response.json();
        // Set the result and close history view
        if (data) {
          setAnalysisResult({
            company: { name: data.company_name || data.ticker, ticker: data.ticker },
            esgScores: data.esg_scores || {
              environmental: data.environmental_score || 0,
              social: data.social_score || 0,
              governance: data.governance_score || 0,
              overall: data.overall_score || 0,
            },
            sdgImpacts: data.sdg_impact || data.top_sdgs || [],
            greenwashingAlerts: data.greenwashing_signals || [],
            blockchainHash: data.blockchain_hash,
          });
          setDebateSessions(data.debate_summary?.debate_sessions || []);
          setGreenwashingSignals(data.greenwashing_signals || []);
          setShowHistory(false);
        }
      }
    } catch (err) {
      console.error('Failed to load historical analysis:', err);
    }
  };

  // Handle analyze from history (re-analyze a company)
  const handleAnalyzeFromHistory = (ticker: string) => {
    setCompanyInput(ticker);
    setShowHistory(false);
    // Trigger analysis after state update
    setTimeout(() => {
      const form = document.querySelector('form');
      if (form) form.dispatchEvent(new Event('submit', { bubbles: true }));
    }, 100);
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Convert company name to ticker if needed
  const getTickerFromInput = (input: string): string => {
    const normalized = input.toLowerCase().trim();
    if (TICKER_MAP[normalized]) {
      return TICKER_MAP[normalized];
    }
    // If it looks like a ticker (1-5 uppercase letters), use as-is
    if (/^[A-Za-z]{1,5}$/.test(input.trim())) {
      return input.toUpperCase().trim();
    }
    // Otherwise, use the input directly (backend will try to resolve)
    return input.toUpperCase().trim();
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: any) => {
    console.log('WebSocket message:', message);

    switch (message.type) {
      case 'connected':
        console.log('Connected to analysis WebSocket');
        break;

      case 'status':
        if (message.status === 'completed') {
          // Analysis complete - fetch final results
          if (analysisId) {
            fetchFinalResults(analysisId);
          }
        } else if (message.status === 'failed') {
          setError(message.message || 'Analysis failed');
          setIsAnalyzing(false);
        }
        break;

      case 'progress':
        // Update overall progress
        console.log('Progress:', message.progress);
        break;

      case 'agent_start':
        setAgents(prev => prev.map(agent =>
          agent.id === message.agent_id
            ? { ...agent, status: 'working', currentTask: message.task || 'Analyzing...', progress: 0 }
            : agent
        ));
        break;

      case 'agent_complete':
        setAgents(prev => prev.map(agent =>
          agent.id === message.agent_id
            ? {
                ...agent,
                status: 'completed',
                progress: 100,
                findings: message.findings || []
              }
            : agent
        ));
        break;

      case 'debate_update':
        // Update orchestrator to debating status
        setIsDebating(true);
        setCurrentDebateRound(message.round || 0);
        setAgents(prev => prev.map(agent =>
          agent.id === 'orchestrator'
            ? { ...agent, status: 'debating', currentTask: `Debate Round ${message.round}` }
            : agent
        ));
        break;

      case 'debate_complete':
        setIsDebating(false);
        break;

      case 'result':
        // Final results received
        processResults(message.data);
        setIsAnalyzing(false);
        break;

      case 'error':
        setError(message.message || 'An error occurred');
        setIsAnalyzing(false);
        break;
    }
  }, [analysisId]);

  // Fetch final results
  const fetchFinalResults = async (id: string) => {
    try {
      const results = await AnalysisAPI.getAnalysisResults(id);
      processResults(results);
      setIsAnalyzing(false);
    } catch (err: any) {
      console.error('Error fetching results:', err);
      // Try to get status instead
      try {
        const status = await AnalysisAPI.getAnalysisStatus(id);
        if (status.results) {
          processResults(status.results);
        }
      } catch {
        setError('Failed to fetch analysis results');
      }
      setIsAnalyzing(false);
    }
  };

  // Process and map backend results to frontend format
  const processResults = (data: any) => {
    console.log('Processing results:', data);

    // Map ESG scores
    const esgScores = {
      environmental: data.environmental_score || data.esg_scores?.environmental || 0,
      social: data.social_score || data.esg_scores?.social || 0,
      governance: data.governance_score || data.esg_scores?.governance || 0,
      overall: data.overall_score || data.esg_scores?.overall || 0,
    };

    // Map SDG impacts
    const sdgImpacts: SDGImpactType[] = [];
    if (data.sdg_impact || data.top_sdgs) {
      const sdgData = data.top_sdgs || Object.entries(data.sdg_impact || {}).map(([goal, score]) => ({
        goal: parseInt(goal),
        score: score as number,
        impact_type: (score as number) > 50 ? 'positive' : 'neutral'
      }));

      sdgData.forEach((sdg: any) => {
        sdgImpacts.push({
          goal: sdg.goal || sdg.sdg_number,
          title: getSDGTitle(sdg.goal || sdg.sdg_number),
          score: Math.round(sdg.score || sdg.impact_score || 0),
          impact: sdg.impact_type || (sdg.score > 50 ? 'positive' : 'neutral'),
          evidence: sdg.evidence || sdg.initiatives || [],
        });
      });
    }

    // Map greenwashing alerts
    const greenwashingAlerts: GreenwashingAlertType[] = [];
    if (data.debate_summary?.greenwashing_signals || data.greenwashing_alerts) {
      const signals = data.debate_summary?.greenwashing_signals || data.greenwashing_alerts || [];
      signals.forEach((signal: any) => {
        greenwashingAlerts.push({
          severity: mapSeverity(signal.severity || signal.risk_level || 'medium'),
          category: signal.category || signal.type || 'General',
          description: signal.description || signal.signal || '',
          evidence: signal.evidence || signal.indicators || [],
          confidence: signal.confidence || signal.confidence_score || 0.5,
        });
      });
    }

    // Build final result
    const result: AnalysisResult = {
      company: {
        name: data.company_name || data.ticker || 'Unknown',
        ticker: data.ticker,
      },
      esgScores,
      sdgImpacts,
      greenwashingAlerts,
      agents: agents,
      debate: data.debate_summary?.arguments || [],
      analysisDate: new Date(data.completed_at || data.created_at || Date.now()),
      confidence: data.debate_summary?.resolution?.final_confidence || data.confidence || 0.85,
    };

    setAnalysisResult(result);

    // Update blockchain status if available
    if (data.blockchain) {
      setBlockchainStatus(data.blockchain);
    }

    // Extract debate sessions from orchestrator summary
    if (data.orchestrator_summary?.debate_sessions || data.debate_sessions) {
      setDebateSessions(data.orchestrator_summary?.debate_sessions || data.debate_sessions || []);
    }

    // Extract greenwashing signals
    if (data.orchestrator_summary?.greenwashing_signals || data.greenwashing_signals) {
      const signals = data.orchestrator_summary?.greenwashing_signals || data.greenwashing_signals || [];
      setGreenwashingSignals(signals);
    }
  };

  // Get SDG title from goal number
  const getSDGTitle = (goal: number): string => {
    const titles: Record<number, string> = {
      1: 'No Poverty',
      2: 'Zero Hunger',
      3: 'Good Health',
      4: 'Quality Education',
      5: 'Gender Equality',
      6: 'Clean Water',
      7: 'Clean Energy',
      8: 'Decent Work',
      9: 'Innovation',
      10: 'Reduced Inequality',
      11: 'Sustainable Cities',
      12: 'Responsible Consumption',
      13: 'Climate Action',
      14: 'Life Below Water',
      15: 'Life on Land',
      16: 'Peace & Justice',
      17: 'Partnerships',
    };
    return titles[goal] || `SDG ${goal}`;
  };

  // Map severity string to type
  const mapSeverity = (severity: string): 'low' | 'medium' | 'high' | 'critical' => {
    const lower = severity.toLowerCase();
    if (lower.includes('critical') || lower.includes('severe')) return 'critical';
    if (lower.includes('high')) return 'high';
    if (lower.includes('low') || lower.includes('minor')) return 'low';
    return 'medium';
  };

  // Start analysis
  const handleAnalyze = async () => {
    const input = companyInput.trim();
    if (!input) return;

    setError(null);
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setDebateSessions([]);
    setGreenwashingSignals([]);
    setIsDebating(false);
    setCurrentDebateRound(0);
    setBlockchainStatus(null);

    // Initialize agents
    const initialAgents = GAIA_AGENTS.map(agent => ({
      ...agent,
      status: 'idle' as const,
      progress: 0,
      currentTask: undefined,
      findings: undefined,
    }));
    setAgents(initialAgents);

    try {
      // Get ticker from input
      const ticker = getTickerFromInput(input);
      console.log(`Starting analysis for ticker: ${ticker}`);

      // Start analysis via API
      const response = await AnalysisAPI.startAnalysis(ticker, input);
      console.log('Analysis started:', response);

      setAnalysisId(response.analysis_id);

      // Connect to WebSocket for real-time updates
      if (wsRef.current) {
        wsRef.current.close();
      }

      wsRef.current = AnalysisAPI.connectWebSocket(
        response.analysis_id,
        handleWebSocketMessage,
        (error) => {
          console.error('WebSocket error:', error);
          // Don't set error - try polling instead
        },
        (event) => {
          console.log('WebSocket closed:', event);
        }
      );

      // Also poll for status as backup (WebSocket might not work in all environments)
      pollAnalysisStatus(response.analysis_id);

    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to start analysis');
      setIsAnalyzing(false);
    }
  };

  // Poll for analysis status (backup for WebSocket)
  const pollAnalysisStatus = async (id: string) => {
    const maxAttempts = 120; // 2 minutes max
    let attempts = 0;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setError('Analysis timed out');
        setIsAnalyzing(false);
        return;
      }

      try {
        const status = await AnalysisAPI.getAnalysisStatus(id);
        console.log('Poll status:', status);

        // Update agent progress from status
        if (status.completed_agents) {
          setAgents(prev => prev.map(agent => ({
            ...agent,
            status: status.completed_agents.includes(agent.id)
              ? 'completed'
              : status.pending_agents?.includes(agent.id)
                ? 'working'
                : agent.status,
            progress: status.completed_agents.includes(agent.id) ? 100 : agent.progress,
          })));
        }

        if (status.status === 'completed') {
          if (status.results) {
            processResults(status.results);
          } else {
            await fetchFinalResults(id);
          }
          setIsAnalyzing(false);
          return;
        }

        if (status.status === 'failed') {
          setError(status.error || 'Analysis failed');
          setIsAnalyzing(false);
          return;
        }

        // Continue polling
        attempts++;
        setTimeout(poll, 1000);

      } catch (err) {
        attempts++;
        setTimeout(poll, 2000);
      }
    };

    // Start polling after a short delay
    setTimeout(poll, 2000);
  };

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Globe2 className="w-10 h-10 text-gaia-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">GAIA Dashboard</h1>
              <p className="text-slate-400">AI-Powered ESG Intelligence with 7 Specialized Agents</p>
            </div>
          </div>
          {blockchainStatus && (
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-900/30 border border-emerald-700/50 rounded-lg">
              <Link2 className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-300 text-sm">
                Blockchain: {blockchainStatus.total_transactions || 0} transactions
              </span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
          )}
        </div>

        {/* Search Bar */}
        <div className="glass rounded-xl p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={companyInput}
                onChange={(e) => setCompanyInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Enter company name or ticker (e.g., Tesla, AAPL, Microsoft)..."
                className="w-full pl-12 pr-4 py-4 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-gaia-500 focus:border-transparent transition-all"
                disabled={isAnalyzing}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !companyInput.trim()}
              className="px-8 py-4 bg-gradient-to-r from-gaia-600 to-emerald-600 rounded-lg text-white font-semibold hover:shadow-lg hover:shadow-gaia-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-105 active:scale-95"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className={`px-6 py-4 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 ${
                showHistory
                  ? 'bg-gaia-600 text-white'
                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50'
              }`}
            >
              <History className="w-5 h-5" />
              History
            </button>
          </div>

          {/* Quick ticker suggestions */}
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="text-slate-500 text-sm">Try:</span>
            {['AAPL', 'TSLA', 'MSFT', 'XOM', 'NKE'].map(ticker => (
              <button
                key={ticker}
                onClick={() => setCompanyInput(ticker)}
                disabled={isAnalyzing}
                className="px-3 py-1 bg-slate-700/50 hover:bg-slate-600/50 rounded-full text-sm text-slate-300 transition-colors disabled:opacity-50"
              >
                {ticker}
              </button>
            ))}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-900/30 border border-red-700/50 rounded-lg">
              <div className="flex items-center gap-2 text-red-300">
                <AlertTriangle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analysis History */}
      {showHistory && (
        <div className="max-w-7xl mx-auto mb-6">
          <AnalysisHistory
            onSelectAnalysis={handleSelectHistoryAnalysis}
            onAnalyzeCompany={handleAnalyzeFromHistory}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {!showHistory && (isAnalyzing || analysisResult) ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Agent Visualization */}
              <AgentVisualization agents={agents} isActive={isAnalyzing} />

              {/* Debate Visualization - Show during debate or when debates exist */}
              {(isDebating || debateSessions.length > 0 || greenwashingSignals.length > 0) && (
                <DebateVisualization
                  debates={debateSessions}
                  greenwashingSignals={greenwashingSignals}
                  isDebating={isDebating}
                  currentRound={currentDebateRound}
                />
              )}

              {/* Results Grid */}
              {analysisResult && (
                <>
                  {/* ESG Scores - Cards and Radar Chart */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Score Cards Column */}
                    <div className="lg:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
                      <ESGScoreCard
                        title="Environmental"
                        score={analysisResult.esgScores.environmental}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="emerald"
                      />
                      <ESGScoreCard
                        title="Social"
                        score={analysisResult.esgScores.social}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="blue"
                      />
                      <ESGScoreCard
                        title="Governance"
                        score={analysisResult.esgScores.governance}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="purple"
                      />
                      <ESGScoreCard
                        title="Overall ESG"
                        score={analysisResult.esgScores.overall}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="gaia"
                        highlight
                      />
                    </div>
                    {/* Radar Chart Column */}
                    <div className="lg:col-span-1">
                      <ESGRadarChart
                        environmental={analysisResult.esgScores.environmental}
                        social={analysisResult.esgScores.social}
                        governance={analysisResult.esgScores.governance}
                        companyName={analysisResult.company.name}
                      />
                    </div>
                  </div>

                  {/* SDG Impact */}
                  {analysisResult.sdgImpacts.length > 0 && (
                    <SDGImpact impacts={analysisResult.sdgImpacts} />
                  )}

                  {/* Greenwashing Alerts */}
                  {analysisResult.greenwashingAlerts.length > 0 && (
                    <GreenwashingAlert alerts={analysisResult.greenwashingAlerts} />
                  )}

                  {/* Blockchain Audit Trail */}
                  {blockchainStatus && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="glass rounded-xl p-6"
                    >
                      <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <Link2 className="w-5 h-5 text-gaia-400" />
                        Blockchain Audit Trail
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-slate-800/50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-white">
                            {blockchainStatus.total_transactions || 0}
                          </div>
                          <div className="text-sm text-slate-400">Transactions</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-white">
                            {blockchainStatus.chain_length || 1}
                          </div>
                          <div className="text-sm text-slate-400">Blocks</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-white">
                            {blockchainStatus.smart_contracts || 3}
                          </div>
                          <div className="text-sm text-slate-400">Smart Contracts</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-4">
                          <div className="text-2xl font-bold text-emerald-400">
                            {blockchainStatus.is_valid !== false ? 'Valid' : 'Invalid'}
                          </div>
                          <div className="text-sm text-slate-400">Chain Status</div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </>
              )}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass rounded-xl p-12 text-center"
            >
              <div className="max-w-2xl mx-auto">
                <div className="w-20 h-20 bg-gaia-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="w-10 h-10 text-gaia-400" />
                </div>
                <h2 className="text-2xl font-semibold text-white mb-3">
                  Ready to Analyze
                </h2>
                <p className="text-slate-400 mb-6">
                  Enter a company name or ticker above to start a comprehensive ESG analysis powered by 7 AI agents with adversarial debate
                </p>
                <div className="flex items-center justify-center gap-8 text-sm text-slate-500">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gaia-500 rounded-full animate-pulse" />
                    ESG Scoring
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    SDG Mapping
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    Greenwashing Detection
                  </div>
                </div>

                {/* Features list */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <div className="text-gaia-400 font-semibold mb-1">7 AI Agents</div>
                    <div className="text-sm text-slate-400">
                      Sentinel, Veritas, Pulse, Regulus, Impact, NEXUS, Orchestrator
                    </div>
                  </div>
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <div className="text-emerald-400 font-semibold mb-1">Adversarial Debate</div>
                    <div className="text-sm text-slate-400">
                      Agents challenge each other to detect bias and greenwashing
                    </div>
                  </div>
                  <div className="bg-slate-800/30 rounded-lg p-4">
                    <div className="text-blue-400 font-semibold mb-1">Blockchain Audit</div>
                    <div className="text-sm text-slate-400">
                      Immutable record of all analysis activities and findings
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AnalysisDashboard;
