import React, { useState } from 'react';
import { 
  Cpu, 
  Activity, 
  Settings, 
  Pause, 
  Play, 
  TrendingUp, 
  AlertOctagon, 
  CheckCircle,
  Clock,
  Coins
} from 'lucide-react';

export default function AgentMonitor() {
  const [agents, setAgents] = useState([
    { id: 1, name: 'Billing Guardian', type: 'Fintech Specialist', status: 'active', activeSessions: 8, totalResolved: 1240, avgHandling: '8.2s', cost: 0.08, accuracy: 99.8, log: 'Monitoring Stripe events for unpaid seat adjustments...' },
    { id: 2, name: 'Setup Specialist', type: 'Onboarding Specialist', status: 'active', activeSessions: 12, totalResolved: 2490, avgHandling: '11.5s', cost: 0.12, accuracy: 98.9, log: 'Validating custom DNS parameters for microsoft.com...' },
    { id: 3, name: 'Upgrade Specialist', type: 'Expansion Advisor', status: 'standby', activeSessions: 0, totalResolved: 450, avgHandling: '14.1s', cost: 0.00, accuracy: 97.4, log: 'Agent resting. Standby for enterprise expansion triggers.' },
    { id: 4, name: 'Escalation Guardian', type: 'Threat Detector', status: 'active', activeSessions: 2, totalResolved: 180, avgHandling: '5.2s', cost: 0.15, accuracy: 99.5, log: 'Anger flag matched in ticket #4910. Alerting support manager.' }
  ]);

  const toggleAgentStatus = (id) => {
    setAgents(prev => prev.map(a => {
      if (a.id === id) {
        const nextStatus = a.status === 'active' ? 'paused' : 'active';
        return {
          ...a,
          status: nextStatus,
          activeSessions: nextStatus === 'active' ? 5 : 0,
          cost: nextStatus === 'active' ? 0.08 : 0.00,
          log: nextStatus === 'active' ? 'Initializing cognitive pipeline...' : 'Cognitive pipeline suspended.'
        };
      }
      return a;
    }));
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* AGENT INTRO */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-800">Autonomous AI Agent Monitor</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Control and inspect individual cognitive autonomous agents</p>
        </div>
        
        {/* Collective metrics */}
        <div className="flex gap-4">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">Average Accuracy</span>
            <span className="text-base font-extrabold text-accentemerald">98.9%</span>
          </div>
          <div className="h-8 w-px bg-slate-200"></div>
          <div className="text-right">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">Collective Processing Cost</span>
            <span className="text-base font-extrabold text-slate-800">$0.35/min</span>
          </div>
        </div>
      </div>

      {/* AGENT MONITOR GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {agents.map(agent => (
          <div key={agent.id} className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-200 flex flex-col justify-between">
            
            {/* Header portion */}
            <div className="p-6 border-b border-slate-100 space-y-4">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl border ${
                    agent.status === 'active' ? 'bg-blue-50 border-blue-100 text-primary animate-pulse' :
                    agent.status === 'paused' ? 'bg-red-50 border-red-100 text-accentred' :
                    'bg-slate-50 border-slate-150 text-slate-400'
                  }`}>
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800">{agent.name}</h4>
                    <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">{agent.type}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                    agent.status === 'active' ? 'bg-emerald-50 text-accentemerald border-emerald-100' :
                    agent.status === 'paused' ? 'bg-red-50 text-accentred border-red-100' :
                    'bg-slate-50 text-slate-400 border-slate-200'
                  }`}>
                    {agent.status.toUpperCase()}
                  </span>
                  
                  <button 
                    onClick={() => toggleAgentStatus(agent.id)}
                    className={`p-1.5 rounded-lg border cursor-pointer hover:bg-slate-50 transition-colors ${
                      agent.status === 'active' ? 'text-slate-500 border-slate-200' : 'text-primary border-blue-200 bg-blue-50'
                    }`}
                  >
                    {agent.status === 'active' ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Status parameters */}
              <div className="grid grid-cols-3 gap-2 bg-slate-50 border border-slate-150 rounded-xl p-3.5 text-center">
                <div>
                  <span className="text-[9px] text-slate-400 font-semibold uppercase block">Active Chats</span>
                  <span className="text-sm font-bold text-slate-800 block mt-0.5">{agent.activeSessions}</span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-400 font-semibold uppercase block">Total Resolved</span>
                  <span className="text-sm font-bold text-slate-800 block mt-0.5">{agent.totalResolved}</span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-400 font-semibold uppercase block">Avg Handling</span>
                  <span className="text-sm font-bold text-slate-800 block mt-0.5">{agent.avgHandling}</span>
                </div>
              </div>

              {/* Performance trackers */}
              <div className="space-y-2 pt-2">
                <div className="flex justify-between items-center text-[11px] text-slate-500 font-medium">
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> LLM Confidence rate</span>
                  <span className="font-bold text-slate-800">{agent.accuracy}%</span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-500 font-medium">
                  <span className="flex items-center gap-1"><Coins className="w-3.5 h-3.5" /> Running cost</span>
                  <span className="font-bold text-slate-800">${agent.cost.toFixed(2)}/min</span>
                </div>
              </div>
            </div>

            {/* Bottom logs tick */}
            <div className="px-6 py-4 bg-slate-900 border-t border-slate-950 font-mono text-[10px] text-slate-400 flex items-center gap-2 truncate">
              <span className="text-accentemerald shrink-0">&gt;_</span>
              <span className="truncate">{agent.log}</span>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
