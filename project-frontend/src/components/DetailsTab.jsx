import React from 'react';

const DetailsTab = ({ result }) => {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-purple-500/20">
      <h2 className="text-2xl font-bold text-white mb-6">Request Details</h2>
      <div className="space-y-4">
        <div className="bg-white/5 rounded-lg p-4">
          <span className="text-sm font-semibold text-purple-300 block mb-2">User Query</span>
          <p className="text-white">{result.query.query}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-4">
          <span className="text-sm font-semibold text-purple-300 block mb-2">Timestamp</span>
          <p className="text-white font-mono">{new Date(result.result.timestamp).toLocaleString()}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-4">
          <span className="text-sm font-semibold text-purple-300 block mb-2">Status</span>
          <p className="text-white capitalize">{result.result.status}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-4">
          <span className="text-sm font-semibold text-purple-300 block mb-2">User ID</span>
          <p className="text-white font-mono">{result.query.user_id}</p>
        </div>
      </div>
    </div>
  );
};

export default DetailsTab;