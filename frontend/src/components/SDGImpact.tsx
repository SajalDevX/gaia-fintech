import { motion } from 'framer-motion';
import { Target, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { SDGImpact as SDGImpactType } from '../types';
import { SDG_GOALS } from '../types';

interface SDGImpactProps {
  impacts: SDGImpactType[];
}

const SDGImpact = ({ impacts }: SDGImpactProps) => {
  const getImpactIcon = (impact: SDGImpactType['impact']) => {
    switch (impact) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-gaia-400" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <Minus className="w-4 h-4 text-slate-400" />;
    }
  };

  const getImpactColor = (impact: SDGImpactType['impact']) => {
    switch (impact) {
      case 'positive':
        return 'border-gaia-500/50 bg-gaia-500/10';
      case 'negative':
        return 'border-red-500/50 bg-red-500/10';
      default:
        return 'border-slate-600 bg-slate-700/30';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-gaia-400';
    if (score >= 60) return 'text-emerald-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <Target className="w-6 h-6 text-gaia-400" />
        <h2 className="text-xl font-semibold text-white">SDG Impact Analysis</h2>
        <span className="ml-auto text-sm text-slate-400">
          {impacts.length} Goals Assessed
        </span>
      </div>

      {/* Impact Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {impacts.map((impact, index) => {
          const sdgGoal = SDG_GOALS.find((g) => g.number === impact.goal);
          return (
            <motion.div
              key={impact.goal}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative rounded-lg p-4 border-2 ${getImpactColor(impact.impact)}`}
            >
              {/* SDG Header */}
              <div className="flex items-start gap-3 mb-3">
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  style={{ backgroundColor: sdgGoal?.color }}
                >
                  {impact.goal}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white text-sm mb-1">
                    {impact.title}
                  </h3>
                  <div className="flex items-center gap-2">
                    {getImpactIcon(impact.impact)}
                    <span className="text-xs text-slate-400 capitalize">
                      {impact.impact} Impact
                    </span>
                  </div>
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(impact.score)}`}>
                  {impact.score}
                </div>
              </div>

              {/* Score Bar */}
              <div className="mb-3">
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${impact.score}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className="h-full bg-gradient-to-r from-gaia-500 to-emerald-500"
                  />
                </div>
              </div>

              {/* Evidence */}
              <div className="space-y-1.5">
                {impact.evidence.slice(0, 2).map((evidence, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-gaia-400 rounded-full mt-1.5 flex-shrink-0" />
                    <p className="text-xs text-slate-300 line-clamp-2">{evidence}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* SDG Overview Grid */}
      <div className="pt-6 border-t border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">All 17 SDG Goals</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {SDG_GOALS.map((goal) => {
            const hasImpact = impacts.find((i) => i.goal === goal.number);
            return (
              <motion.div
                key={goal.number}
                whileHover={{ scale: 1.1 }}
                className={`w-9 h-9 rounded flex items-center justify-center text-white text-xs font-bold cursor-pointer transition-all ${
                  hasImpact ? 'opacity-100 shadow-lg' : 'opacity-40'
                }`}
                style={{ backgroundColor: goal.color }}
                title={`${goal.number}. ${goal.title}`}
              >
                {goal.number}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SDGImpact;
