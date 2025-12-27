/**
 * Financial Inclusion Dashboard Component
 *
 * Comprehensive visualization of financial inclusion metrics
 * addressing DIC 2025 Finance Track Focus Area 3:
 * Inclusion-oriented payments/credit for underserved populations.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Globe,
  Heart,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  MapPin,
  Smartphone,
  Building,
  Target,
  Award,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Info,
  Loader2,
} from 'lucide-react';

// Types
interface InclusionScore {
  overall_score: number;
  access_score: number;
  credit_score: number;
  gender_score: number;
  geographic_score: number;
  vulnerable_population_score: number;
  affordability_score: number;
  grade: string;
  percentile_rank: number;
}

interface InclusionMetrics {
  access: {
    unbanked_reached: number;
    mobile_users: number;
    agents_deployed: number;
    access_score: number;
  };
  credit: {
    microloans: number;
    first_time_borrowers: number;
    approval_rate: number;
    credit_score: number;
  };
  gender: {
    women_accounts: number;
    women_entrepreneurs: number;
    parity_index: number;
    gender_score: number;
  };
  geographic: {
    rural_coverage: number;
    last_mile_communities: number;
    geographic_score: number;
  };
  vulnerable: {
    refugees_served: number;
    youth_accounts: number;
    vulnerable_score: number;
  };
  affordability: {
    zero_fee_accounts: boolean;
    effective_rate: number;
    affordability_score: number;
  };
}

interface WashingRisk {
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
  risk_score: number;
  indicators: string[];
  predatory_lending: boolean;
}

interface FinancialInclusionData {
  company_name: string;
  ticker: string;
  inclusion_score: InclusionScore;
  metrics: InclusionMetrics;
  washing_risk: WashingRisk;
  total_lives_impacted: number;
  segments_served: string[];
  sdg_alignment: { [key: number]: number };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

interface FinancialInclusionDashboardProps {
  ticker: string;
  companyName: string;
  data?: FinancialInclusionData;
  loading?: boolean;
}

// Mock data generator for demo
const generateMockData = (ticker: string, companyName: string): FinancialInclusionData => {
  const isHighInclusion = ticker.toLowerCase().includes('mfi') ||
                          companyName.toLowerCase().includes('micro');
  const baseScore = isHighInclusion ? 75 : 55;

  return {
    company_name: companyName,
    ticker: ticker,
    inclusion_score: {
      overall_score: baseScore + Math.random() * 15,
      access_score: baseScore + Math.random() * 20,
      credit_score: baseScore - 5 + Math.random() * 15,
      gender_score: baseScore - 10 + Math.random() * 20,
      geographic_score: baseScore - 5 + Math.random() * 15,
      vulnerable_population_score: baseScore - 15 + Math.random() * 20,
      affordability_score: baseScore + Math.random() * 10,
      grade: baseScore > 70 ? 'A-' : baseScore > 60 ? 'B+' : 'B',
      percentile_rank: baseScore + Math.random() * 15,
    },
    metrics: {
      access: {
        unbanked_reached: Math.floor(800 + Math.random() * 1200),
        mobile_users: Math.floor(500 + Math.random() * 1000),
        agents_deployed: Math.floor(50 + Math.random() * 150),
        access_score: baseScore + Math.random() * 15,
      },
      credit: {
        microloans: Math.floor(400 + Math.random() * 800),
        first_time_borrowers: Math.floor(200 + Math.random() * 500),
        approval_rate: 55 + Math.random() * 30,
        credit_score: baseScore + Math.random() * 10,
      },
      gender: {
        women_accounts: Math.floor(300 + Math.random() * 700),
        women_entrepreneurs: Math.floor(100 + Math.random() * 300),
        parity_index: 0.5 + Math.random() * 0.4,
        gender_score: baseScore - 5 + Math.random() * 20,
      },
      geographic: {
        rural_coverage: 30 + Math.random() * 40,
        last_mile_communities: Math.floor(20 + Math.random() * 60),
        geographic_score: baseScore + Math.random() * 15,
      },
      vulnerable: {
        refugees_served: Math.floor(50 + Math.random() * 150),
        youth_accounts: Math.floor(100 + Math.random() * 400),
        vulnerable_score: baseScore - 10 + Math.random() * 20,
      },
      affordability: {
        zero_fee_accounts: Math.random() > 0.3,
        effective_rate: 20 + Math.random() * 30,
        affordability_score: baseScore + Math.random() * 15,
      },
    },
    washing_risk: {
      risk_level: baseScore > 70 ? 'low' : baseScore > 55 ? 'moderate' : 'high',
      risk_score: 100 - baseScore + Math.random() * 20,
      indicators: baseScore < 60 ? ['Impact metrics may be overstated', 'Limited rural verification'] : [],
      predatory_lending: Math.random() < 0.1,
    },
    total_lives_impacted: Math.floor(1500 + Math.random() * 2000),
    segments_served: ['unbanked', 'women', 'rural', 'micro_entrepreneurs', 'youth'].slice(0, 3 + Math.floor(Math.random() * 3)),
    sdg_alignment: {
      1: baseScore + Math.random() * 15,
      5: baseScore - 10 + Math.random() * 20,
      8: baseScore + Math.random() * 10,
      10: baseScore - 5 + Math.random() * 15,
    },
    strengths: [
      'Strong mobile money reach',
      'Women-focused lending programs',
      'Affordable transaction fees',
    ].slice(0, 2 + Math.floor(Math.random() * 2)),
    weaknesses: [
      'Limited rural presence',
      'Gender parity gap',
      'High interest rates on some products',
    ].slice(0, 1 + Math.floor(Math.random() * 2)),
    recommendations: [
      'Expand agent network in rural areas',
      'Develop alternative credit scoring',
      'Introduce women-specific financial products',
    ],
  };
};

// Score indicator component
const ScoreIndicator: React.FC<{ score: number; label: string; icon: React.ReactNode }> = ({
  score,
  label,
  icon,
}) => {
  const getColor = (s: number) => {
    if (s >= 75) return 'text-green-500 bg-green-500/10';
    if (s >= 60) return 'text-blue-500 bg-blue-500/10';
    if (s >= 45) return 'text-yellow-500 bg-yellow-500/10';
    return 'text-red-500 bg-red-500/10';
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50">
      <div className={`p-2 rounded-lg ${getColor(score)}`}>{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="text-sm text-slate-400">{label}</div>
        <div className="text-lg font-semibold text-white">{score.toFixed(1)}</div>
      </div>
      <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden flex-shrink-0">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`h-full rounded-full ${
            score >= 75
              ? 'bg-green-500'
              : score >= 60
              ? 'bg-blue-500'
              : score >= 45
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
        />
      </div>
    </div>
  );
};

// Segment badge component
const SegmentBadge: React.FC<{ segment: string }> = ({ segment }) => {
  const segmentInfo: { [key: string]: { icon: React.ReactNode; color: string; label: string } } = {
    unbanked: { icon: <Users size={14} />, color: 'bg-purple-500/20 text-purple-400', label: 'Unbanked' },
    women: { icon: <Heart size={14} />, color: 'bg-pink-500/20 text-pink-400', label: 'Women' },
    rural: { icon: <MapPin size={14} />, color: 'bg-green-500/20 text-green-400', label: 'Rural' },
    youth: { icon: <TrendingUp size={14} />, color: 'bg-blue-500/20 text-blue-400', label: 'Youth' },
    micro_entrepreneurs: { icon: <Building size={14} />, color: 'bg-orange-500/20 text-orange-400', label: 'Micro-Entrepreneurs' },
    refugees: { icon: <Globe size={14} />, color: 'bg-cyan-500/20 text-cyan-400', label: 'Refugees' },
  };

  const info = segmentInfo[segment] || { icon: <Users size={14} />, color: 'bg-slate-500/20 text-slate-400', label: segment };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${info.color}`}>
      {info.icon}
      {info.label}
    </span>
  );
};

// SDG alignment component
const SDGAlignment: React.FC<{ alignment: { [key: number]: number } }> = ({ alignment }) => {
  const sdgNames: { [key: number]: string } = {
    1: 'No Poverty',
    5: 'Gender Equality',
    8: 'Decent Work',
    9: 'Innovation',
    10: 'Reduced Inequalities',
  };

  const sdgColors: { [key: number]: string } = {
    1: 'bg-red-500',
    5: 'bg-orange-500',
    8: 'bg-pink-600',
    9: 'bg-orange-400',
    10: 'bg-pink-500',
  };

  return (
    <div className="space-y-3">
      {Object.entries(alignment).map(([sdg, score]) => (
        <div key={sdg} className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg ${sdgColors[parseInt(sdg)]} flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}>
            {sdg}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-300">{sdgNames[parseInt(sdg)]}</span>
              <span className="text-white font-medium">{(score as number).toFixed(0)}%</span>
            </div>
            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${score}%` }}
                transition={{ duration: 1, delay: 0.2 }}
                className={`h-full rounded-full ${sdgColors[parseInt(sdg)]}`}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Washing risk indicator
const WashingRiskIndicator: React.FC<{ risk: WashingRisk }> = ({ risk }) => {
  const riskConfig = {
    low: { color: 'text-green-400 bg-green-500/10', icon: <CheckCircle size={20} />, label: 'Low Risk' },
    moderate: { color: 'text-yellow-400 bg-yellow-500/10', icon: <AlertTriangle size={20} />, label: 'Moderate Risk' },
    high: { color: 'text-orange-400 bg-orange-500/10', icon: <AlertTriangle size={20} />, label: 'High Risk' },
    critical: { color: 'text-red-400 bg-red-500/10', icon: <AlertTriangle size={20} />, label: 'Critical Risk' },
  };

  const config = riskConfig[risk.risk_level];

  return (
    <div className={`p-4 rounded-xl ${config.color}`}>
      <div className="flex items-center gap-3 mb-3">
        {config.icon}
        <div>
          <div className="font-semibold">{config.label}</div>
          <div className="text-sm opacity-80">Inclusion Washing Detection</div>
        </div>
      </div>
      {risk.indicators.length > 0 && (
        <ul className="space-y-1 text-sm opacity-80">
          {risk.indicators.map((indicator, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="mt-1">•</span>
              {indicator}
            </li>
          ))}
        </ul>
      )}
      {risk.predatory_lending && (
        <div className="mt-3 p-2 bg-red-500/20 rounded-lg text-red-300 text-sm">
          <AlertTriangle size={14} className="inline mr-1" />
          Predatory lending indicators detected
        </div>
      )}
    </div>
  );
};

// Main component
const FinancialInclusionDashboard: React.FC<FinancialInclusionDashboardProps> = ({
  ticker,
  companyName,
  data: propData,
  loading = false,
}) => {
  const [data, setData] = useState<FinancialInclusionData | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'impact'>('overview');

  useEffect(() => {
    if (propData) {
      setData(propData);
    } else {
      // Generate mock data for demo
      setData(generateMockData(ticker, companyName));
    }
  }, [ticker, companyName, propData]);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-gaia-500 mx-auto mb-4" />
          <p className="text-slate-400">Analyzing financial inclusion metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-2xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Financial Inclusion Analysis</h2>
              <p className="text-slate-400">{companyName} ({ticker})</p>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            {data.inclusion_score.overall_score.toFixed(1)}
          </div>
          <div className="flex items-center justify-end gap-2 mt-1">
            <span className="text-2xl font-semibold text-white">{data.inclusion_score.grade}</span>
            <span className="text-sm text-slate-400">
              Top {(100 - data.inclusion_score.percentile_rank).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-slate-700 pb-4 overflow-x-auto">
        {['overview', 'metrics', 'impact'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === tab
                ? 'bg-gaia-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Score Breakdown */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <BarChart3 size={20} className="text-blue-400" />
                Inclusion Score Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <ScoreIndicator
                  score={data.inclusion_score.access_score}
                  label="Financial Access"
                  icon={<Smartphone size={18} />}
                />
                <ScoreIndicator
                  score={data.inclusion_score.credit_score}
                  label="Credit Inclusion"
                  icon={<DollarSign size={18} />}
                />
                <ScoreIndicator
                  score={data.inclusion_score.gender_score}
                  label="Gender Inclusion"
                  icon={<Heart size={18} />}
                />
                <ScoreIndicator
                  score={data.inclusion_score.geographic_score}
                  label="Geographic Reach"
                  icon={<MapPin size={18} />}
                />
                <ScoreIndicator
                  score={data.inclusion_score.vulnerable_population_score}
                  label="Vulnerable Populations"
                  icon={<Users size={18} />}
                />
                <ScoreIndicator
                  score={data.inclusion_score.affordability_score}
                  label="Affordability"
                  icon={<Target size={18} />}
                />
              </div>
            </div>

            {/* Washing Risk */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <AlertTriangle size={20} className="text-yellow-400" />
                Inclusion Washing Risk
              </h3>
              <WashingRiskIndicator risk={data.washing_risk} />
            </div>

            {/* Segments Served */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Users size={20} className="text-purple-400" />
                Underserved Segments Served
              </h3>
              <div className="flex flex-wrap gap-2">
                {data.segments_served.map((segment) => (
                  <SegmentBadge key={segment} segment={segment} />
                ))}
              </div>
            </div>

            {/* SDG Alignment */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Globe size={20} className="text-green-400" />
                SDG Alignment
              </h3>
              <SDGAlignment alignment={data.sdg_alignment} />
            </div>
          </motion.div>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && (
          <motion.div
            key="metrics"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {/* Access Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <Smartphone size={18} className="text-blue-400" />
                Access Metrics
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Unbanked Reached (per $1M)</span>
                  <span className="text-white font-medium">{data.metrics.access.unbanked_reached.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Mobile Money Users</span>
                  <span className="text-white font-medium">{data.metrics.access.mobile_users.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Agents Deployed</span>
                  <span className="text-white font-medium">{data.metrics.access.agents_deployed}</span>
                </div>
              </div>
            </div>

            {/* Credit Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <DollarSign size={18} className="text-green-400" />
                Credit Metrics
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Microloans (per $1M)</span>
                  <span className="text-white font-medium">{data.metrics.credit.microloans.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">First-Time Borrowers</span>
                  <span className="text-white font-medium">{data.metrics.credit.first_time_borrowers.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Approval Rate</span>
                  <span className="text-white font-medium">{data.metrics.credit.approval_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Gender Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <Heart size={18} className="text-pink-400" />
                Gender Inclusion
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Women Account Holders</span>
                  <span className="text-white font-medium">{data.metrics.gender.women_accounts.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Women Entrepreneurs</span>
                  <span className="text-white font-medium">{data.metrics.gender.women_entrepreneurs.toLocaleString()}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Gender Parity Index</span>
                  <span className={`font-medium ${data.metrics.gender.parity_index >= 0.8 ? 'text-green-400' : data.metrics.gender.parity_index >= 0.6 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {data.metrics.gender.parity_index.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {/* Geographic Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <MapPin size={18} className="text-orange-400" />
                Geographic Reach
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Rural Coverage</span>
                  <span className="text-white font-medium">{data.metrics.geographic.rural_coverage.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Last-Mile Communities</span>
                  <span className="text-white font-medium">{data.metrics.geographic.last_mile_communities}</span>
                </div>
              </div>
            </div>

            {/* Vulnerable Population Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <Users size={18} className="text-purple-400" />
                Vulnerable Populations
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Refugees Served</span>
                  <span className="text-white font-medium">{data.metrics.vulnerable.refugees_served}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Youth Accounts</span>
                  <span className="text-white font-medium">{data.metrics.vulnerable.youth_accounts.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Affordability Metrics */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <Target size={18} className="text-cyan-400" />
                Affordability
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Zero-Fee Accounts</span>
                  <span className={`font-medium ${data.metrics.affordability.zero_fee_accounts ? 'text-green-400' : 'text-red-400'}`}>
                    {data.metrics.affordability.zero_fee_accounts ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-slate-400">Effective Rate</span>
                  <span className={`font-medium ${data.metrics.affordability.effective_rate < 30 ? 'text-green-400' : data.metrics.affordability.effective_rate < 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {data.metrics.affordability.effective_rate.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Impact Tab */}
        {activeTab === 'impact' && (
          <motion.div
            key="impact"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Total Impact */}
            <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-xl p-6 border border-purple-500/30">
              <div className="flex items-center gap-4 flex-wrap">
                <div className="p-4 bg-purple-500/20 rounded-xl flex-shrink-0">
                  <Award size={32} className="text-purple-400" />
                </div>
                <div>
                  <div className="text-4xl font-bold text-white">
                    {data.total_lives_impacted.toLocaleString()}
                  </div>
                  <div className="text-slate-400">Lives Impacted per $1M Invested</div>
                </div>
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
                <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                  <CheckCircle size={18} className="text-green-400" />
                  Key Strengths
                </h4>
                <ul className="space-y-2">
                  {data.strengths.map((strength, i) => (
                    <li key={i} className="flex items-start gap-2 text-slate-300">
                      <ArrowUpRight size={16} className="text-green-400 mt-1 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
                <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                  <AlertTriangle size={18} className="text-yellow-400" />
                  Areas for Improvement
                </h4>
                <ul className="space-y-2">
                  {data.weaknesses.map((weakness, i) => (
                    <li key={i} className="flex items-start gap-2 text-slate-300">
                      <ArrowDownRight size={16} className="text-yellow-400 mt-1 flex-shrink-0" />
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-slate-800/50 rounded-xl p-5 space-y-4">
              <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                <Info size={18} className="text-blue-400" />
                Recommendations
              </h4>
              <ul className="space-y-3">
                {data.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-3 p-3 bg-blue-500/10 rounded-lg text-slate-300">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                      {i + 1}
                    </span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FinancialInclusionDashboard;
