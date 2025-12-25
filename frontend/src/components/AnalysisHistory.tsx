import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  History,
  AlertTriangle,
  Clock,
  Building2,
  ChevronRight,
  RefreshCw,
  Filter,
  Search,
} from 'lucide-react';

interface AnalysisSummary {
  analysis_id: string;
  ticker: string;
  company_name: string;
  overall_score: number | null;
  risk_level: string | null;
  recommendation: string | null;
  greenwashing_signals_count: number;
  created_at: string | null;
  status: string;
}

interface HistoryStats {
  total_analyses: number;
  unique_companies: number;
  analyses_last_7_days: number;
  average_scores: {
    overall: number;
    environmental: number;
    social: number;
    governance: number;
  };
  risk_distribution: Record<string, number>;
}

interface AnalysisHistoryProps {
  onSelectAnalysis?: (analysisId: string) => void;
  onAnalyzeCompany?: (ticker: string) => void;
}

const API_BASE = 'http://localhost:8000/api/v1';

const AnalysisHistory = ({ onSelectAnalysis, onAnalyzeCompany }: AnalysisHistoryProps) => {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [stats, setStats] = useState<HistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTicker, setSearchTicker] = useState('');
  const [filterRisk, setFilterRisk] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/history/recent?limit=20`),
        fetch(`${API_BASE}/history/stats`),
      ]);

      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setAnalyses(historyData);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (err) {
      setError('Failed to load analysis history');
      console.error('History fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredAnalyses = analyses.filter((a) => {
    if (searchTicker && !a.ticker.toLowerCase().includes(searchTicker.toLowerCase())) {
      return false;
    }
    if (filterRisk && a.risk_level !== filterRisk) {
      return false;
    }
    return true;
  });

  const getRiskColor = (risk: string | null) => {
    switch (risk?.toUpperCase()) {
      case 'LOW':
      case 'MINIMAL':
        return 'text-emerald-400 bg-emerald-400/10';
      case 'MODERATE':
        return 'text-amber-400 bg-amber-400/10';
      case 'HIGH':
      case 'ELEVATED':
        return 'text-orange-400 bg-orange-400/10';
      case 'CRITICAL':
        return 'text-red-400 bg-red-400/10';
      default:
        return 'text-slate-400 bg-slate-400/10';
    }
  };

  const getScoreColor = (score: number | null) => {
    if (!score) return 'text-slate-400';
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-gaia-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-center h-40">
          <RefreshCw className="w-8 h-8 text-gaia-400 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <History className="w-6 h-6 text-gaia-400" />
          <h2 className="text-xl font-semibold text-white">Analysis History</h2>
        </div>
        <button
          onClick={fetchHistory}
          className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{stats.total_analyses}</div>
            <div className="text-sm text-slate-400">Total Analyses</div>
          </div>
          <div className="glass rounded-lg p-4">
            <div className="text-2xl font-bold text-gaia-400">{stats.unique_companies}</div>
            <div className="text-sm text-slate-400">Companies</div>
          </div>
          <div className="glass rounded-lg p-4">
            <div className="text-2xl font-bold text-emerald-400">{stats.average_scores.overall.toFixed(1)}</div>
            <div className="text-sm text-slate-400">Avg ESG Score</div>
          </div>
          <div className="glass rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-400">{stats.analyses_last_7_days}</div>
            <div className="text-sm text-slate-400">Last 7 Days</div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by ticker..."
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-gaia-500"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterRisk || ''}
            onChange={(e) => setFilterRisk(e.target.value || null)}
            className="px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-gaia-500"
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MODERATE">Moderate Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {/* Analysis List */}
      {error ? (
        <div className="glass rounded-xl p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
          <p className="text-slate-400">{error}</p>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="glass rounded-xl p-8 text-center">
          <History className="w-12 h-12 text-slate-500 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-white mb-2">No Analysis History</h3>
          <p className="text-slate-400 mb-4">
            {searchTicker || filterRisk
              ? 'No analyses match your filters'
              : 'Start analyzing companies to build your history'}
          </p>
          {!searchTicker && !filterRisk && (
            <button
              onClick={() => onAnalyzeCompany?.('AAPL')}
              className="px-4 py-2 bg-gaia-600 hover:bg-gaia-500 text-white rounded-lg transition-colors"
            >
              Analyze Apple (AAPL)
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {filteredAnalyses.map((analysis, index) => (
              <motion.div
                key={analysis.analysis_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => onSelectAnalysis?.(analysis.analysis_id)}
                className="glass rounded-lg p-4 cursor-pointer hover:bg-slate-700/30 transition-colors group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-lg bg-slate-700/50 flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-gaia-400" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-white">{analysis.ticker}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${getRiskColor(analysis.risk_level)}`}>
                          {analysis.risk_level || 'N/A'}
                        </span>
                        {analysis.greenwashing_signals_count > 0 && (
                          <span className="px-2 py-0.5 rounded text-xs text-amber-400 bg-amber-400/10 flex items-center">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            {analysis.greenwashing_signals_count}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-slate-400">{analysis.company_name}</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <div className={`text-lg font-bold ${getScoreColor(analysis.overall_score)}`}>
                        {analysis.overall_score?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-xs text-slate-500">ESG Score</div>
                    </div>

                    <div className="flex items-center space-x-2 text-slate-400">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">{formatDate(analysis.created_at)}</span>
                    </div>

                    <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-gaia-400 transition-colors" />
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Risk Distribution Chart */}
      {stats && Object.keys(stats.risk_distribution).length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          <div className="flex items-end space-x-2 h-32">
            {Object.entries(stats.risk_distribution).map(([level, count]) => {
              const maxCount = Math.max(...Object.values(stats.risk_distribution));
              const height = (count / maxCount) * 100;
              return (
                <div key={level} className="flex-1 flex flex-col items-center">
                  <div
                    className={`w-full rounded-t transition-all ${getRiskColor(level).split(' ')[1]}`}
                    style={{ height: `${height}%` }}
                  />
                  <div className="mt-2 text-xs text-slate-400 text-center">{level}</div>
                  <div className="text-sm font-medium text-white">{count}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default AnalysisHistory;
