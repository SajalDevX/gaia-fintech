import { motion } from 'framer-motion';
import { Activity, CheckCircle2, Loader2 } from 'lucide-react';
import type { AgentStatus } from '../types';

interface AgentVisualizationProps {
  agents: AgentStatus[];
  isActive: boolean;
}

const AgentVisualization = ({ agents, isActive }: AgentVisualizationProps) => {
  const getStatusIcon = (status: AgentStatus['status']) => {
    switch (status) {
      case 'working':
        return <Loader2 className="w-5 h-5 text-amber-400 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-gaia-400" />;
      case 'debating':
        return <Activity className="w-5 h-5 text-purple-400 animate-pulse" />;
      default:
        return <div className="w-5 h-5 rounded-full bg-slate-600" />;
    }
  };

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
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`relative rounded-lg p-4 border-2 transition-all duration-300 ${getStatusColor(
              agent.status
            )}`}
          >
            {/* Agent Header */}
            <div className="flex items-start gap-3 mb-3">
              <div className="text-3xl">{agent.avatar}</div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white text-sm mb-1 truncate">
                  {agent.name}
                </h3>
                <p className="text-xs text-slate-400 truncate">{agent.role}</p>
              </div>
              {getStatusIcon(agent.status)}
            </div>

            {/* Current Task */}
            {agent.currentTask && (
              <div className="mb-3">
                <p className="text-xs text-slate-300 line-clamp-2">{agent.currentTask}</p>
              </div>
            )}

            {/* Progress Bar */}
            {agent.status === 'working' && (
              <div className="mb-2">
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${agent.progress}%` }}
                    transition={{ duration: 0.3 }}
                    className="h-full bg-gradient-to-r from-amber-500 to-amber-400"
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1 text-right">{agent.progress}%</p>
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
                className={`text-xs px-2 py-1 rounded-full font-medium ${
                  agent.status === 'working'
                    ? 'bg-amber-500/20 text-amber-300'
                    : agent.status === 'completed'
                    ? 'bg-gaia-500/20 text-gaia-300'
                    : agent.status === 'debating'
                    ? 'bg-purple-500/20 text-purple-300'
                    : 'bg-slate-700/50 text-slate-400'
                }`}
              >
                {agent.status}
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
