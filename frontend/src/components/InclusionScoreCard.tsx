/**
 * Inclusion Score Card Component
 *
 * Compact visualization of financial inclusion metrics
 * for integration in the main analysis dashboard.
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Heart,
  MapPin,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

interface InclusionScoreCardProps {
  overallScore: number;
  grade: string;
  accessScore: number;
  genderScore: number;
  geographicScore: number;
  livesImpacted: number;
  washingRisk: 'low' | 'moderate' | 'high' | 'critical';
  topSegments: string[];
  onViewDetails?: () => void;
}

const InclusionScoreCard: React.FC<InclusionScoreCardProps> = ({
  overallScore,
  grade,
  accessScore,
  genderScore,
  geographicScore,
  livesImpacted,
  washingRisk,
  topSegments,
  onViewDetails,
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 45) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getGradeColor = (g: string) => {
    if (g.startsWith('A')) return 'from-green-500 to-emerald-500';
    if (g.startsWith('B')) return 'from-blue-500 to-cyan-500';
    if (g.startsWith('C')) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  };

  const getRiskConfig = (risk: string) => {
    const configs = {
      low: { color: 'text-green-400', bg: 'bg-green-500/10', icon: <CheckCircle size={14} /> },
      moderate: { color: 'text-yellow-400', bg: 'bg-yellow-500/10', icon: <AlertTriangle size={14} /> },
      high: { color: 'text-orange-400', bg: 'bg-orange-500/10', icon: <AlertTriangle size={14} /> },
      critical: { color: 'text-red-400', bg: 'bg-red-500/10', icon: <AlertTriangle size={14} /> },
    };
    return configs[risk as keyof typeof configs] || configs.moderate;
  };

  const segmentLabels: { [key: string]: string } = {
    unbanked: 'Unbanked',
    women: 'Women',
    rural: 'Rural',
    youth: 'Youth',
    micro_entrepreneurs: 'Micro-Ent.',
    refugees: 'Refugees',
  };

  const riskConfig = getRiskConfig(washingRisk);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-5 border border-slate-700/50 hover:border-purple-500/50 transition-colors"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Users size={18} className="text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">Financial Inclusion</h3>
        </div>
        <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${getGradeColor(grade)} text-white text-sm font-bold`}>
          {grade}
        </div>
      </div>

      {/* Main Score */}
      <div className="flex items-center gap-4 mb-4">
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="40"
              cy="40"
              r="36"
              fill="none"
              stroke="currentColor"
              strokeWidth="6"
              className="text-slate-700"
            />
            <motion.circle
              cx="40"
              cy="40"
              r="36"
              fill="none"
              stroke="url(#inclusionGradient)"
              strokeWidth="6"
              strokeLinecap="round"
              initial={{ strokeDasharray: '0 226' }}
              animate={{ strokeDasharray: `${(overallScore / 100) * 226} 226` }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
            />
            <defs>
              <linearGradient id="inclusionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-xl font-bold ${getScoreColor(overallScore)}`}>
              {overallScore.toFixed(0)}
            </span>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-3xl font-bold text-white mb-1">
            {livesImpacted.toLocaleString()}
          </div>
          <div className="text-sm text-slate-400">Lives impacted per $1M</div>
        </div>
      </div>

      {/* Mini Metrics */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="text-center p-2 bg-slate-800/50 rounded-lg">
          <Users size={14} className="mx-auto mb-1 text-blue-400" />
          <div className={`text-sm font-semibold ${getScoreColor(accessScore)}`}>
            {accessScore.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500">Access</div>
        </div>
        <div className="text-center p-2 bg-slate-800/50 rounded-lg">
          <Heart size={14} className="mx-auto mb-1 text-pink-400" />
          <div className={`text-sm font-semibold ${getScoreColor(genderScore)}`}>
            {genderScore.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500">Gender</div>
        </div>
        <div className="text-center p-2 bg-slate-800/50 rounded-lg">
          <MapPin size={14} className="mx-auto mb-1 text-green-400" />
          <div className={`text-sm font-semibold ${getScoreColor(geographicScore)}`}>
            {geographicScore.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500">Geographic</div>
        </div>
      </div>

      {/* Segments */}
      <div className="flex flex-wrap gap-1 mb-4">
        {topSegments.slice(0, 4).map((segment) => (
          <span
            key={segment}
            className="px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded-full"
          >
            {segmentLabels[segment] || segment}
          </span>
        ))}
      </div>

      {/* Washing Risk & Action */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-700/50 flex-wrap gap-2">
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${riskConfig.bg} ${riskConfig.color} text-xs`}>
          {riskConfig.icon}
          <span className="capitalize">{washingRisk} Risk</span>
        </div>
        {onViewDetails && (
          <button
            onClick={onViewDetails}
            className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          >
            View Details →
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default InclusionScoreCard;
