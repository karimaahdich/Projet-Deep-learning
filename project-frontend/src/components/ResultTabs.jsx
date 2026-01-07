import React from 'react';
import ResultTab from './ResultTab';
import ValidationTab from './ValidationTab';
import DetailsTab from './DetailsTab';

const ResultTabs = ({ result, activeTab, setActiveTab }) => {
  return (
    <div className="space-y-6">
      {/* Tabs Navigation */}
      <div className="flex gap-2 bg-white/10 p-2 rounded-xl">
        {['result', 'validation', 'details'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold capitalize transition-all ${
              activeTab === tab
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-purple-200 hover:bg-white/10'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'result' && <ResultTab result={result} />}
      {activeTab === 'validation' && <ValidationTab result={result} />}
      {activeTab === 'details' && <DetailsTab result={result} />}
    </div>
  );
};

export default ResultTabs;