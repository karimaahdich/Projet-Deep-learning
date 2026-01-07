import { Database, Zap, Brain, Cpu, Activity, Shield, Terminal } from 'lucide-react';

export const getAgentIcon = (agent) => {
  const icons = {
    'RAG': Database,
    'EASY': Zap,
    'MEDIUM': Brain,
    'DIFFUSION': Cpu,
    'HARD': Activity,
    'VALIDATION': Shield
  };
  return icons[agent] || Terminal;
};

export const getComplexityColor = (level) => {
  const colors = {
    'EASY': 'text-green-500 bg-green-500/20',
    'MEDIUM': 'text-yellow-500 bg-yellow-500/20',
    'HARD': 'text-red-500 bg-red-500/20'
  };
  return colors[level] || 'text-gray-500 bg-gray-500/20';
};

export const getRiskColor = (level) => {
  const colors = {
    'LOW': 'bg-green-100 text-green-800 border-green-300',
    'MEDIUM': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'HIGH': 'bg-red-100 text-red-800 border-red-300'
  };
  return colors[level] || 'bg-gray-100 text-gray-800 border-gray-300';
};