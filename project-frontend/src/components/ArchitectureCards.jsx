import React from 'react';
import { Database, Brain, Cpu, Shield } from 'lucide-react';

const ArchitectureCards = () => {
  const cards = [
    { icon: Database, title: 'Knowledge Graph', desc: 'RAG-based retrieval' },
    { icon: Brain, title: 'LLM Generation', desc: 'Fine-tuned models' },
    { icon: Cpu, title: 'Diffusion Synthesis', desc: 'Complex scenarios' },
    { icon: Shield, title: 'Validation', desc: 'Security checks' }
  ];

  return (
    <div className="grid md:grid-cols-4 gap-4">
      {cards.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div key={idx} className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-purple-500/20 text-center">
            <Icon className="w-10 h-10 text-purple-400 mx-auto mb-3" />
            <h3 className="font-semibold text-white mb-2">{item.title}</h3>
            <p className="text-sm text-purple-200">{item.desc}</p>
          </div>
        );
      })}
    </div>
  );
};

export default ArchitectureCards;