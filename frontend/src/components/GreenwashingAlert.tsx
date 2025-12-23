import { motion } from 'framer-motion';
import { AlertTriangle, AlertCircle, Info, XCircle, Shield } from 'lucide-react';
import type { GreenwashingAlert as AlertType } from '../types';

interface GreenwashingAlertProps {
  alerts: AlertType[];
}

const GreenwashingAlert = ({ alerts }: GreenwashingAlertProps) => {
  const getSeverityIcon = (severity: AlertType['severity']) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'high':
        return <AlertTriangle className="w-6 h-6 text-orange-500" />;
      case 'medium':
        return <AlertCircle className="w-6 h-6 text-amber-500" />;
      default:
        return <Info className="w-6 h-6 text-blue-500" />;
    }
  };

  const getSeverityColor = (severity: AlertType['severity']) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500/50 bg-red-500/10';
      case 'high':
        return 'border-orange-500/50 bg-orange-500/10';
      case 'medium':
        return 'border-amber-500/50 bg-amber-500/10';
      default:
        return 'border-blue-500/50 bg-blue-500/10';
    }
  };

  const getSeverityBadgeColor = (severity: AlertType['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/20 text-red-300';
      case 'high':
        return 'bg-orange-500/20 text-orange-300';
      case 'medium':
        return 'bg-amber-500/20 text-amber-300';
      default:
        return 'bg-blue-500/20 text-blue-300';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-red-400';
    if (confidence >= 0.6) return 'text-amber-400';
    return 'text-slate-400';
  };

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-amber-400" />
        <h2 className="text-xl font-semibold text-white">Greenwashing Detection</h2>
        <span className="ml-auto text-sm text-slate-400">
          {alerts.length} {alerts.length === 1 ? 'Alert' : 'Alerts'} Found
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gaia-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-gaia-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No Alerts Detected</h3>
          <p className="text-slate-400 text-sm">
            No significant greenwashing indicators found in the analysis.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative rounded-lg p-5 border-2 ${getSeverityColor(alert.severity)}`}
            >
              {/* Alert Header */}
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0 mt-1">
                  {getSeverityIcon(alert.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h3 className="font-semibold text-white text-base">{alert.category}</h3>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span
                        className={`text-xs px-3 py-1 rounded-full font-medium uppercase ${getSeverityBadgeColor(
                          alert.severity
                        )}`}
                      >
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-slate-300 mb-3">{alert.description}</p>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-slate-400">Confidence Level</span>
                  <span className={`text-sm font-semibold ${getConfidenceColor(alert.confidence)}`}>
                    {(alert.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${alert.confidence * 100}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-full ${
                      alert.confidence >= 0.8
                        ? 'bg-gradient-to-r from-red-500 to-orange-500'
                        : alert.confidence >= 0.6
                        ? 'bg-gradient-to-r from-amber-500 to-yellow-500'
                        : 'bg-gradient-to-r from-slate-500 to-slate-400'
                    }`}
                  />
                </div>
              </div>

              {/* Evidence */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Supporting Evidence
                </h4>
                <div className="space-y-2">
                  {alert.evidence.map((evidence, i) => (
                    <div key={i} className="flex items-start gap-2 bg-slate-800/50 rounded p-3">
                      <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 flex-shrink-0" />
                      <p className="text-sm text-slate-300">{evidence}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendation */}
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-slate-400">
                    Review these claims for accuracy and ensure third-party verification where
                    possible. Consider providing specific, measurable data to support
                    sustainability claims.
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {alerts.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-700">
          <div className="grid grid-cols-4 gap-4">
            {['critical', 'high', 'medium', 'low'].map((severity) => {
              const count = alerts.filter((a) => a.severity === severity).length;
              return (
                <div key={severity} className="text-center">
                  <div
                    className={`text-2xl font-bold mb-1 ${
                      severity === 'critical'
                        ? 'text-red-400'
                        : severity === 'high'
                        ? 'text-orange-400'
                        : severity === 'medium'
                        ? 'text-amber-400'
                        : 'text-blue-400'
                    }`}
                  >
                    {count}
                  </div>
                  <div className="text-xs text-slate-500 uppercase">{severity}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default GreenwashingAlert;
