import React, { useState } from 'react';
import QueryInput from './components/QueryInput';
import ResultTabs from './components/ResultTabs';
import ErrorDisplay from './components/ErrorDisplay';
import ArchitectureCards from './components/ArchitectureCards';
import Header from './components/Header';
import { generateCommand } from './services/api';

const App = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('query');

  const exampleQueries = [
    "Scan all ports on 192.168.1.1",
    "Perform a stealth scan with 10 random decoys and fragment packets on 192.168.1.0/24",
    "Quick service version detection on scanme.nmap.org",
    "Aggressive OS detection with script scanning on 10.0.0.1"
  ];

  /**
   * Extract target (IP address or hostname) from query text
   */
  const extractTarget = (text) => {
    // Match IP address (IPv4)
    const ipv4Regex = /\b(?:\d{1,3}\.){3}\d{1,3}(?:\/\d{1,2})?\b/;
    const ipMatch = text.match(ipv4Regex);
    if (ipMatch) {
      return ipMatch[0];
    }

    // Match hostname/domain
    const hostnameRegex = /\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b/i;
    const hostnameMatch = text.match(hostnameRegex);
    if (hostnameMatch) {
      return hostnameMatch[0];
    }

    return null;
  };

  const handleGenerate = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    console.log('🔍 Query:', query);

    try {
      // Extract target from query
      const target = extractTarget(query);
      
      // Build context with target if found
      const context = target ? { target: target } : {};
      
      console.log('📦 Context:', context);

      // Call the API with proper backend schema
      const data = await generateCommand(query, context);
      
      console.log('✅ Response:', data);
      setResult(data);
      setActiveTab('result');
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.message || 'Failed to generate command. Please check your backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Header />

        <QueryInput
          query={query}
          setQuery={setQuery}
          loading={loading}
          handleGenerate={handleGenerate}
          exampleQueries={exampleQueries}
        />

        <ErrorDisplay error={error} />

        {result && (
          <ResultTabs
            result={result}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        )}

        {!result && !loading && <ArchitectureCards />}
      </div>
    </div>
  );
};

export default App;