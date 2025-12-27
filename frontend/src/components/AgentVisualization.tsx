import { motion } from 'framer-motion';
import { Activity, CheckCircle2, Loader2 } from 'lucide-react';
import type { AgentStatus } from '../types';

interface AgentVisualizationProps {
  agents: AgentStatus[];
  isActive: boolean;
}

const AgentVisualization = ({ agents, isActive }: AgentVisualizationProps) => {
  const getStatusColor = (status: AgentStatus['status']) => {
    switch (status) {
      case 'working':
        return 'border-amber-500/50 bg-amber-500/10';
      case 'completed':
        return 'border-gaia-500/50 bg-gaia-500/10';
      case 'debating':
        return 'border-purple-500/50 bg-purple-500/10';
      default:
        return 'border-slate-700 bg-slate-800/30';
    }
  };

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-gaia-400" />
        <h2 className="text-xl font-semibold text-white">AI Agent Network</h2>
        {isActive && (
          <span className="ml-auto flex items-center gap-2 text-sm text-gaia-400">
            <div className="w-2 h-2 bg-gaia-400 rounded-full animate-pulse" />
            Active
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{
              opacity: 1,
              scale: 1,
              boxShadow: agent.status === 'working'
                ? ['0 0 0 0 rgba(245, 158, 11, 0)', '0 0 20px 2px rgba(245, 158, 11, 0.3)', '0 0 0 0 rgba(245, 158, 11, 0)']
                : '0 0 0 0 rgba(0, 0, 0, 0)'
            }}
            transition={{
              delay: index * 0.1,
              boxShadow: {
                duration: 2,
                repeat: agent.status === 'working' ? Infinity : 0,
                ease: 'easeInOut'
              }
            }}
            className={`relative rounded-lg p-4 border-2 transition-all duration-300 ${getStatusColor(
              agent.status
            )}`}
          >
            {/* Agent Header */}
            <div className="flex items-start gap-3 mb-3">
              <motion.div
                className="text-3xl"
                animate={agent.status === 'working' ? {
                  scale: [1, 1.1, 1],
                } : {}}
                transition={{
                  duration: 1.5,
                  repeat: agent.status === 'working' ? Infinity : 0,
                  ease: 'easeInOut'
                }}
              >
                {agent.avatar}
              </motion.div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white text-sm mb-1 truncate">
                  {agent.name}
                </h3>
                <p className="text-xs text-slate-400 truncate">{agent.role}</p>
              </div>
            </div>

            {/* Current Task */}
            {(agent.currentTask || agent.status === 'working') && (
              <div className="mb-3">
                <p className="text-xs text-slate-300 line-clamp-2">
                  {agent.currentTask || `Gathering ${agent.role.toLowerCase()} data...`}
                </p>
              </div>
            )}

            {/* Completed Indicator */}
            {agent.status === 'completed' && (
              <div className="mb-3">
                <div className="flex items-center gap-2 text-xs text-gaia-400">
                  <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 0.5 }}
                      className="h-full bg-gradient-to-r from-gaia-500 to-emerald-400"
                    />
                  </div>
                  <span className="font-medium">Done</span>
                </div>
              </div>
            )}

            {/* Progress Bar */}
            {agent.status === 'working' && (
              <div className="mb-2">
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden relative">
                  {agent.progress > 0 ? (
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${agent.progress}%` }}
                      transition={{ duration: 0.3 }}
                      className="h-full bg-gradient-to-r from-amber-500 to-amber-400"
                    />
                  ) : (
                    /* Indeterminate loading animation when progress is 0 */
                    <motion.div
                      className="absolute h-full w-1/3 bg-gradient-to-r from-transparent via-amber-500 to-transparent"
                      animate={{
                        x: ['-100%', '400%'],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                    />
                  )}
                </div>
                <div className="flex justify-between items-center mt-1">
                  <p className="text-xs text-amber-400/70">
                    {agent.progress === 0 ? 'Initializing...' : 'Processing...'}
                  </p>
                  <p className="text-xs text-slate-500">{agent.progress}%</p>
                </div>
              </div>
            )}

            {/* Findings */}
            {agent.findings && agent.findings.length > 0 && (
              <div className="space-y-1">
                {agent.findings.slice(0, 2).map((finding, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className="w-1 h-1 bg-gaia-400 rounded-full mt-1.5 flex-shrink-0" />
                    <p className="text-xs text-slate-400 line-clamp-1">{finding}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Status Badge */}
            <div className="absolute top-2 right-2">
              <div
                className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5 ${
                  agent.status === 'working'
                    ? 'bg-amber-500/20 text-amber-300'
                    : agent.status === 'completed'
                    ? 'bg-gaia-500/20 text-gaia-300'
                    : agent.status === 'debating'
                    ? 'bg-purple-500/20 text-purple-300'
                    : 'bg-slate-700/50 text-slate-400'
                }`}
              >
                {agent.status === 'completed' && (
                  <CheckCircle2 className="w-3 h-3" />
                )}
                {agent.status === 'working' && (
                  <Loader2 className="w-3 h-3 animate-spin" />
                )}
                {agent.status === 'debating' && (
                  <Activity className="w-3 h-3" />
                )}
                <span>{agent.status}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Agent Connection Visualization */}
      {isActive && (
        <div className="mt-6 pt-6 border-t border-slate-700">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-gaia-400 rounded-full animate-pulse" />
              <span>Data Flow</span>
            </div>
            <span className="text-slate-600">→</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse delay-500" />
              <span>Agent Debate</span>
            </div>
            <span className="text-slate-600">→</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse delay-1000" />
              <span>Consensus</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentVisualization;
