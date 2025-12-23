import { useState } from 'react';
import { motion } from 'framer-motion';
import { Globe2, Sparkles } from 'lucide-react';
import AnalysisDashboard from './components/AnalysisDashboard';

function App() {
  const [started, setStarted] = useState(false);

  if (!started) {
    return (
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-radial from-gaia-600/20 to-transparent animate-pulse-slow" />
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-radial from-emerald-600/20 to-transparent animate-pulse-slow delay-1000" />
        </div>

        {/* Hero content */}
        <div className="relative z-10 text-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center justify-center mb-6">
              <Globe2 className="w-20 h-20 text-gaia-400 animate-spin-slow" />
            </div>

            <h1 className="text-7xl font-bold mb-4 gradient-text">
              GAIA
            </h1>

            <p className="text-2xl text-slate-300 mb-2">
              Global AI Intelligence Analyzer
            </p>

            <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
              Multi-agent AI system for comprehensive ESG analysis, SDG impact assessment,
              and greenwashing detection powered by 6 specialized AI agents working in harmony.
            </p>

            <motion.button
              onClick={() => setStarted(true)}
              className="group relative px-8 py-4 bg-gradient-to-r from-gaia-600 to-emerald-600 rounded-xl text-white font-semibold text-lg shadow-lg hover:shadow-gaia-500/50 transition-all duration-300 hover:scale-105"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Start Analysis
              </span>
              <div className="absolute inset-0 rounded-xl bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.button>

            <div className="mt-16 grid grid-cols-3 gap-8 max-w-3xl mx-auto">
              {[
                { label: 'AI Agents', value: '6' },
                { label: 'SDG Goals', value: '17' },
                { label: 'ESG Metrics', value: '100+' },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  className="glass rounded-lg p-6"
                >
                  <div className="text-4xl font-bold text-gaia-400 mb-2">{stat.value}</div>
                  <div className="text-slate-400">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return <AnalysisDashboard />;
}

export default App;
