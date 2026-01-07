import React from 'react';
import { Search, ArrowRight } from 'lucide-react';

const QueryInput = ({ query, setQuery, loading, handleGenerate, exampleQueries }) => {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 mb-8 border border-purple-500/20">
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-purple-300 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
            placeholder="Describe your network scan requirements..."
            className="w-full pl-12 pr-4 py-4 bg-white/90 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
          />
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading || !query.trim()}
          className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              Processing...
            </>
          ) : (
            <>
              Generate <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-purple-200 text-sm">Try:</span>
        {exampleQueries.map((ex, idx) => (
          <button
            key={idx}
            onClick={() => setQuery(ex)}
            className="text-sm px-3 py-1 bg-white/20 hover:bg-white/30 text-purple-100 rounded-lg transition-colors"
          >
            {ex.substring(0, 40)}...
          </button>
        ))}
      </div>
    </div>
  );
};

export default QueryInput;