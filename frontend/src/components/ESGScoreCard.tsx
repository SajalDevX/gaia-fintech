import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface ESGScoreCardProps {
  title: string;
  score: number;
  icon: ReactNode;
  color?: 'emerald' | 'blue' | 'purple' | 'gaia';
  highlight?: boolean;
}

const ESGScoreCard = ({ title, score, icon, color = 'gaia', highlight = false }: ESGScoreCardProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-gaia-400';
    if (score >= 60) return 'text-emerald-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const colorMap = {
    emerald: {
      gradient: 'from-emerald-500 to-emerald-600',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/50',
      text: 'text-emerald-400',
    },
    blue: {
      gradient: 'from-blue-500 to-blue-600',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/50',
      text: 'text-blue-400',
    },
    purple: {
      gradient: 'from-purple-500 to-purple-600',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/50',
      text: 'text-purple-400',
    },
    gaia: {
      gradient: 'from-gaia-500 to-emerald-500',
      bg: 'bg-gaia-500/10',
      border: 'border-gaia-500/50',
      text: 'text-gaia-400',
    },
  };

  const colors = colorMap[color];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className={`glass rounded-xl p-6 border-2 ${
        highlight ? colors.border : 'border-slate-700'
      } transition-all duration-300`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colors.bg}`}>
          <div className={colors.text}>{icon}</div>
        </div>
        <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
          {Math.round(score)}
        </div>
      </div>

      <h3 className="text-slate-300 text-sm font-medium mb-2">{title}</h3>

      <div className="mb-3">
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className={`h-full bg-gradient-to-r ${colors.gradient}`}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">Rating</span>
        <span className={`text-xs font-semibold ${getScoreColor(score)}`}>
          {getScoreLabel(score)}
        </span>
      </div>

      {highlight && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className={`w-2 h-2 ${colors.bg} rounded-full`} />
            Comprehensive ESG Score
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ESGScoreCard;
