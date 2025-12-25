import { motion } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface ESGRadarChartProps {
  environmental: number;
  social: number;
  governance: number;
  companyName?: string;
}

const ESGRadarChart = ({ environmental, social, governance, companyName }: ESGRadarChartProps) => {
  // Ensure scores are valid numbers (default to 0 if null/undefined/NaN)
  const envScore = Number(environmental) || 0;
  const socScore = Number(social) || 0;
  const govScore = Number(governance) || 0;

  const data = [
    {
      category: 'Environmental',
      score: envScore,
      fullMark: 100,
      description: 'Carbon footprint, emissions, resource usage',
    },
    {
      category: 'Social',
      score: socScore,
      fullMark: 100,
      description: 'Labor practices, community impact, diversity',
    },
    {
      category: 'Governance',
      score: govScore,
      fullMark: 100,
      description: 'Board structure, transparency, ethics',
    },
  ];

  const getOverallRating = () => {
    const avg = (envScore + socScore + govScore) / 3;
    if (avg >= 80) return { label: 'Excellent', color: 'text-emerald-400' };
    if (avg >= 60) return { label: 'Good', color: 'text-gaia-400' };
    if (avg >= 40) return { label: 'Fair', color: 'text-amber-400' };
    return { label: 'Poor', color: 'text-red-400' };
  };

  const rating = getOverallRating();

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-white font-semibold">{data.category}</p>
          <p className="text-gaia-400 text-lg font-bold">{data.score}/100</p>
          <p className="text-slate-400 text-xs mt-1">{data.description}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold text-white">ESG Performance Radar</h3>
          {companyName && (
            <p className="text-slate-400 text-sm">{companyName}</p>
          )}
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${rating.color}`}>
            {Math.round((envScore + socScore + govScore) / 3)}
          </div>
          <div className={`text-sm ${rating.color}`}>{rating.label}</div>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
            <PolarGrid
              stroke="#334155"
              strokeDasharray="3 3"
            />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickLine={{ stroke: '#475569' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickCount={5}
              axisLine={{ stroke: '#475569' }}
            />
            <Radar
              name="ESG Score"
              dataKey="score"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.3}
              strokeWidth={2}
              dot={{
                r: 4,
                fill: '#10b981',
                stroke: '#fff',
                strokeWidth: 2,
              }}
              activeDot={{
                r: 6,
                fill: '#34d399',
                stroke: '#fff',
                strokeWidth: 2,
              }}
            />
            <Tooltip content={<CustomTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Score breakdown */}
      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-700">
        <div className="text-center">
          <div className="text-emerald-400 text-lg font-bold">{envScore.toFixed(1)}</div>
          <div className="text-slate-400 text-xs">Environmental</div>
        </div>
        <div className="text-center">
          <div className="text-blue-400 text-lg font-bold">{socScore.toFixed(1)}</div>
          <div className="text-slate-400 text-xs">Social</div>
        </div>
        <div className="text-center">
          <div className="text-purple-400 text-lg font-bold">{govScore.toFixed(1)}</div>
          <div className="text-slate-400 text-xs">Governance</div>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="text-sm text-slate-400">
          {envScore >= socScore && envScore >= govScore && (
            <span>Strongest in <span className="text-emerald-400 font-medium">Environmental</span> practices</span>
          )}
          {socScore > envScore && socScore >= govScore && (
            <span>Strongest in <span className="text-blue-400 font-medium">Social</span> responsibility</span>
          )}
          {govScore > envScore && govScore > socScore && (
            <span>Strongest in <span className="text-purple-400 font-medium">Governance</span> standards</span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ESGRadarChart;
