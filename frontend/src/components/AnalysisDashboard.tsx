import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, AlertTriangle, Globe2 } from 'lucide-react';
import AgentVisualization from './AgentVisualization';
import SDGImpact from './SDGImpact';
import GreenwashingAlert from './GreenwashingAlert';
import ESGScoreCard from './ESGScoreCard';
import type { AnalysisResult, AgentStatus } from '../types';

const AnalysisDashboard = () => {
  const [companyName, setCompanyName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [agents, setAgents] = useState<AgentStatus[]>([]);

  const mockAgents: AgentStatus[] = [
    {
      id: 'scraper',
      name: 'Data Scraper',
      role: 'Information Gathering',
      status: 'idle',
      progress: 0,
      avatar: '🔍',
    },
    {
      id: 'esg',
      name: 'ESG Analyzer',
      role: 'Environmental, Social & Governance',
      status: 'idle',
      progress: 0,
      avatar: '🌍',
    },
    {
      id: 'sdg',
      name: 'SDG Mapper',
      role: 'Sustainable Development Goals',
      status: 'idle',
      progress: 0,
      avatar: '🎯',
    },
    {
      id: 'greenwashing',
      name: 'Greenwashing Detective',
      role: 'Authenticity Verification',
      status: 'idle',
      progress: 0,
      avatar: '🕵️',
    },
    {
      id: 'debater1',
      name: 'Critical Analyst',
      role: 'Challenge & Verify',
      status: 'idle',
      progress: 0,
      avatar: '⚖️',
    },
    {
      id: 'debater2',
      name: 'Consensus Builder',
      role: 'Synthesis & Integration',
      status: 'idle',
      progress: 0,
      avatar: '🤝',
    },
  ];

  const handleAnalyze = async () => {
    if (!companyName.trim()) return;

    setIsAnalyzing(true);
    setAgents(mockAgents);

    // Simulate agent workflow
    const workflow = [
      { agentId: 'scraper', duration: 2000, task: 'Collecting company data...' },
      { agentId: 'esg', duration: 3000, task: 'Analyzing ESG metrics...' },
      { agentId: 'sdg', duration: 2500, task: 'Mapping SDG impacts...' },
      { agentId: 'greenwashing', duration: 2800, task: 'Detecting greenwashing...' },
      { agentId: 'debater1', duration: 2000, task: 'Challenging findings...' },
      { agentId: 'debater2', duration: 1500, task: 'Building consensus...' },
    ];

    for (const step of workflow) {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === step.agentId
            ? { ...agent, status: 'working', currentTask: step.task }
            : agent
        )
      );

      // Simulate progress
      const progressInterval = setInterval(() => {
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === step.agentId && agent.progress < 100
              ? { ...agent, progress: Math.min(agent.progress + 10, 100) }
              : agent
          )
        );
      }, step.duration / 10);

      await new Promise((resolve) => setTimeout(resolve, step.duration));
      clearInterval(progressInterval);

      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === step.agentId
            ? { ...agent, status: 'completed', progress: 100 }
            : agent
        )
      );
    }

    // Generate mock results
    setAnalysisResult({
      company: { name: companyName },
      esgScores: {
        environmental: Math.random() * 40 + 60,
        social: Math.random() * 40 + 60,
        governance: Math.random() * 40 + 60,
        overall: Math.random() * 40 + 60,
      },
      sdgImpacts: [
        { goal: 7, title: 'Clean Energy', score: 85, impact: 'positive', evidence: ['Invested $2B in renewable energy', 'Reduced carbon emissions by 40%'] },
        { goal: 13, title: 'Climate Action', score: 78, impact: 'positive', evidence: ['Net-zero commitment by 2040', 'Science-based targets validated'] },
        { goal: 8, title: 'Decent Work', score: 72, impact: 'positive', evidence: ['Living wage policy', 'Strong labor standards'] },
        { goal: 12, title: 'Responsible Consumption', score: 65, impact: 'neutral', evidence: ['Circular economy initiatives', 'Some recycling programs'] },
      ],
      greenwashingAlerts: [
        {
          severity: 'medium',
          category: 'Vague Claims',
          description: 'Marketing materials use undefined "eco-friendly" claims without specific metrics',
          evidence: ['Website claims without data', 'No third-party verification'],
          confidence: 0.73,
        },
      ],
      agents: agents,
      debate: [],
      analysisDate: new Date(),
      confidence: 0.87,
    });

    setIsAnalyzing(false);
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
              <p className="text-slate-400">AI-Powered ESG Intelligence</p>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="glass rounded-xl p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Enter company name (e.g., Tesla, Apple, Microsoft)..."
                className="w-full pl-12 pr-4 py-4 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-gaia-500 focus:border-transparent transition-all"
                disabled={isAnalyzing}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !companyName.trim()}
              className="px-8 py-4 bg-gradient-to-r from-gaia-600 to-emerald-600 rounded-lg text-white font-semibold hover:shadow-lg hover:shadow-gaia-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-105 active:scale-95"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {isAnalyzing || analysisResult ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Agent Visualization */}
              <AgentVisualization agents={agents} isActive={isAnalyzing} />

              {/* Results Grid */}
              {analysisResult && (
                <>
                  {/* ESG Scores */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
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

                  {/* SDG Impact */}
                  <SDGImpact impacts={analysisResult.sdgImpacts} />

                  {/* Greenwashing Alerts */}
                  {analysisResult.greenwashingAlerts.length > 0 && (
                    <GreenwashingAlert alerts={analysisResult.greenwashingAlerts} />
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
                  Enter a company name above to start a comprehensive ESG analysis powered by 6 AI agents
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
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AnalysisDashboard;
