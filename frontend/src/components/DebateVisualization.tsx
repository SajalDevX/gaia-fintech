import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Scale, AlertTriangle, CheckCircle2, Brain, Zap } from 'lucide-react';

interface DebateArgument {
  agent_name: string;
  stance: 'support' | 'challenge' | 'neutral';
  argument: string;
  confidence: number;
  round: number;
  evidence?: string[];
}

interface DebateSession {
  topic: string;
  findings: any[];
  arguments: DebateArgument[];
  resolution?: {
    winner: string;
    final_confidence: number;
    reasoning: string;
  };
}

interface GreenwashingSignal {
  signal_type: string;
  description: string;
  severity: string;
  indicators: string[];
  confidence: number;
}

interface DebateVisualizationProps {
  debates?: DebateSession[];
  greenwashingSignals?: GreenwashingSignal[];
  isDebating?: boolean;
  currentRound?: number;
}

const agentAvatars: Record<string, { avatar: string; color: string }> = {
  sentinel: { avatar: '🛡️', color: 'emerald' },
  veritas: { avatar: '🔍', color: 'blue' },
  pulse: { avatar: '📊', color: 'purple' },
  regulus: { avatar: '⚖️', color: 'amber' },
  impact: { avatar: '🎯', color: 'green' },
  nexus: { avatar: '🌐', color: 'cyan' },
  orchestrator: { avatar: '🧠', color: 'pink' },
  advocate: { avatar: '👍', color: 'green' },
  challenger: { avatar: '👎', color: 'red' },
};

const DebateVisualization = ({
  debates = [],
  greenwashingSignals = [],
  isDebating = false,
  currentRound = 0
}: DebateVisualizationProps) => {
  const [activeDebate, setActiveDebate] = useState(0);
  const [visibleArgs, setVisibleArgs] = useState<number>(0);
  const debateRef = useRef<HTMLDivElement>(null);

  // Animate arguments appearing one by one
  useEffect(() => {
    if (debates[activeDebate]?.arguments) {
      const args = debates[activeDebate].arguments;
      if (visibleArgs < args.length) {
        const timer = setTimeout(() => {
          setVisibleArgs(prev => prev + 1);
        }, 800);
        return () => clearTimeout(timer);
      }
    }
  }, [debates, activeDebate, visibleArgs]);

  // Reset visible args when changing debate
  useEffect(() => {
    setVisibleArgs(0);
  }, [activeDebate]);

  // Auto-scroll to bottom when new arguments appear
  useEffect(() => {
    if (debateRef.current) {
      debateRef.current.scrollTop = debateRef.current.scrollHeight;
    }
  }, [visibleArgs]);

  const getStanceColor = (stance: string) => {
    switch (stance) {
      case 'support':
        return 'border-green-500/50 bg-green-500/10';
      case 'challenge':
        return 'border-red-500/50 bg-red-500/10';
      default:
        return 'border-slate-500/50 bg-slate-500/10';
    }
  };

  const getStanceIcon = (stance: string) => {
    switch (stance) {
      case 'support':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'challenge':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <Scale className="w-4 h-4 text-slate-400" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/20 text-red-300 border-red-500/50';
      case 'high':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
      case 'medium':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
      default:
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
    }
  };

  return (
    <div className="glass rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-600/20 rounded-full flex items-center justify-center">
            <Brain className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Adversarial Debate</h2>
            <p className="text-sm text-slate-400">AI agents challenging findings to detect bias</p>
          </div>
        </div>
        {isDebating && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 rounded-full">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
            <span className="text-sm text-purple-300">Round {currentRound}</span>
          </div>
        )}
      </div>

      {/* Debate Tabs */}
      {debates.length > 1 && (
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {debates.map((debate, idx) => (
            <button
              key={idx}
              onClick={() => setActiveDebate(idx)}
              className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                activeDebate === idx
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
              }`}
            >
              Debate {idx + 1}: {debate.topic?.slice(0, 30) || 'Conflict Resolution'}
              {debate.topic?.length > 30 && '...'}
            </button>
          ))}
        </div>
      )}

      {/* Debate Arena */}
      {debates.length > 0 ? (
        <div className="space-y-4">
          {/* Topic */}
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium text-slate-300">Debate Topic</span>
            </div>
            <p className="text-white">{debates[activeDebate]?.topic || 'Analyzing conflicting findings...'}</p>
          </div>

          {/* Arguments */}
          <div ref={debateRef} className="space-y-3 max-h-96 overflow-y-auto pr-2">
            <AnimatePresence mode="popLayout">
              {debates[activeDebate]?.arguments?.slice(0, visibleArgs).map((arg, idx) => {
                const agent = agentAvatars[arg.agent_name.toLowerCase()] || { avatar: '🤖', color: 'slate' };
                const isLeft = arg.stance === 'support';

                return (
                  <motion.div
                    key={`${activeDebate}-${idx}`}
                    initial={{ opacity: 0, x: isLeft ? -20 : 20, scale: 0.95 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${isLeft ? 'justify-start' : 'justify-end'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 border-2 ${getStanceColor(arg.stance)} ${
                        isLeft ? 'rounded-tl-sm' : 'rounded-tr-sm'
                      }`}
                    >
                      {/* Agent header */}
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">{agent.avatar}</span>
                        <span className="font-medium text-white capitalize">{arg.agent_name}</span>
                        {getStanceIcon(arg.stance)}
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          arg.stance === 'support' ? 'bg-green-500/20 text-green-300' :
                          arg.stance === 'challenge' ? 'bg-red-500/20 text-red-300' :
                          'bg-slate-500/20 text-slate-300'
                        }`}>
                          {arg.stance}
                        </span>
                      </div>

                      {/* Argument */}
                      <p className="text-slate-200 text-sm leading-relaxed">{arg.argument}</p>

                      {/* Evidence */}
                      {arg.evidence && arg.evidence.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700/50">
                          <p className="text-xs text-slate-400 mb-1">Evidence:</p>
                          <ul className="text-xs text-slate-300 space-y-1">
                            {arg.evidence.slice(0, 2).map((e, i) => (
                              <li key={i} className="flex items-start gap-1">
                                <span className="text-purple-400">•</span>
                                {e}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Confidence */}
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              arg.stance === 'support' ? 'bg-green-500' :
                              arg.stance === 'challenge' ? 'bg-red-500' : 'bg-slate-500'
                            }`}
                            style={{ width: `${arg.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">
                          {Math.round(arg.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {/* Typing indicator when debating */}
            {isDebating && debates[activeDebate]?.arguments && visibleArgs >= debates[activeDebate].arguments.length && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 p-3 bg-slate-800/30 rounded-lg"
              >
                <Zap className="w-4 h-4 text-purple-400 animate-pulse" />
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-slate-400">Agents are deliberating...</span>
              </motion.div>
            )}
          </div>

          {/* Resolution */}
          {debates[activeDebate]?.resolution && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg border border-purple-500/30"
            >
              <div className="flex items-center gap-2 mb-2">
                <Scale className="w-5 h-5 text-purple-400" />
                <span className="font-semibold text-white">Resolution</span>
              </div>
              <p className="text-slate-300 text-sm">{debates[activeDebate].resolution.reasoning}</p>
              <div className="mt-2 flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Winner:</span>
                  <span className="text-sm text-white capitalize">{debates[activeDebate].resolution.winner}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Confidence:</span>
                  <span className="text-sm text-purple-300">
                    {Math.round(debates[activeDebate].resolution.final_confidence * 100)}%
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-slate-400">
          <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No debates recorded yet</p>
          <p className="text-sm mt-1">Debates will appear when agents challenge each other's findings</p>
        </div>
      )}

      {/* Greenwashing Signals */}
      {greenwashingSignals.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold text-white">Greenwashing Signals Detected</h3>
            <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded-full text-xs">
              {greenwashingSignals.length}
            </span>
          </div>
          <div className="space-y-3">
            {greenwashingSignals.map((signal, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`p-4 rounded-lg border ${getSeverityColor(signal.severity)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{signal.signal_type}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(signal.severity)}`}>
                    {signal.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-slate-300 mb-2">{signal.description}</p>
                {signal.indicators && signal.indicators.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {signal.indicators.slice(0, 3).map((indicator, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-slate-800/50 rounded text-slate-400">
                        {indicator}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DebateVisualization;
