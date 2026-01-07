import React from 'react';
import { Terminal } from 'lucide-react';

const Header = () => {
  return (
    <div className="text-center mb-12">
      <div className="flex items-center justify-center gap-3 mb-4">
        <Terminal className="w-12 h-12 text-purple-400" />
        <h1 className="text-4xl font-bold text-white">
          Nmap Command Generator
        </h1>
      </div>
      <p className="text-purple-200 text-lg">
        AI-Powered Network Scanning with Multi-Agent Validation
      </p>
    </div>
  );
};

export default Header;