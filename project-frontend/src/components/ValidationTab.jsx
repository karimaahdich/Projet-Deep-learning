import React from 'react';
import { CheckCircle, XCircle, TrendingUp, Shield, AlertTriangle, AlertCircle } from 'lucide-react';
import { getRiskColor } from '../utils/helpers';

const ValidationTab = ({ result }) => {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
      {/* Validation Status */}
      <div className="flex items-center gap-4 mb-8">
        {result.result.valid ? (
          <CheckCircle className="w-12 h-12 text-green-400" />
        ) : (
          <XCircle className="w-12 h-12 text-red-400" />
        )}
        <div>
          <h2 className="text-2xl font-bold text-white">
            {result.result.valid ? 'Valid Command' : 'Invalid Command'}
          </h2>
          <p className="text-purple-200">{result.result.recommendation}</p>
        </div>
      </div>

      {/* Risk Score */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-white/5 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-yellow-400" />
            <span className="text-purple-300 font-semibold">Risk Score</span>
          </div>
          <p className="text-4xl font-bold text-white">{result.result.risk_score}/10</p>
        </div>
        <div className="bg-white/5 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-blue-400" />
            <span className="text-purple-300 font-semibold">Risk Level</span>
          </div>
          <span className={`inline-block px-4 py-2 rounded-lg font-bold text-lg ${getRiskColor(result.result.risk_level)}`}>
            {result.result.risk_level}
          </span>
        </div>
      </div>

      {/* Issues */}
      {result.result.issues?.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            Issues Found
          </h3>
          <div className="space-y-3">
            {result.result.issues.map((issue, idx) => (
              <div key={idx} className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-yellow-300 capitalize">{issue.type}</span>
                  <span className="text-sm px-2 py-1 bg-yellow-500/20 rounded text-yellow-200">
                    {issue.severity}
                  </span>
                </div>
                <p className="text-yellow-100 mb-2">{issue.message}</p>
                <p className="text-sm text-yellow-200/70">💡 {issue.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {result.result.warnings?.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-400" />
            Warnings
          </h3>
          <div className="space-y-2">
            {result.result.warnings.map((warning, idx) => (
              <div key={idx} className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
                <p className="text-orange-200">{warning}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationTab;