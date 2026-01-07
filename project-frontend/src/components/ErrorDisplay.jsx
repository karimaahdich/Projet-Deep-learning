import React from 'react';
import { XCircle } from 'lucide-react';

const ErrorDisplay = ({ error }) => {
  if (!error) return null;

  return (
    <div className="bg-red-500/20 border border-red-500 rounded-xl p-4 mb-8 flex items-center gap-3">
      <XCircle className="w-6 h-6 text-red-400" />
      <p className="text-red-200">{error}</p>
    </div>
  );
};

export default ErrorDisplay;