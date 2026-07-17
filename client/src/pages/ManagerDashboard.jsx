import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  CheckCircle2, 
  Clock, 
  Brain, 
  ArrowUpRight, 
  AlertTriangle,
  Play,
  Cpu
} from 'lucide-react';

export default function ManagerDashboard() {
  const [liveTickets, setLiveTickets] = useState([
    { id: 'CX-4912', customer: 'Microsoft (Enterprise)', agent: 'Billing Specialist', action: 'Refund Issued ($199)', status: 'Success', time: 'Just now', sentiment: 'Positive' },
    { id: 'CX-4911', customer: 'Stripe API', agent: 'Setup Specialist', action: 'Webhook Reset', status: 'Success', time: '2m ago', sentiment: 'Neutral' },
    { id: 'CX-4910', customer: 'Zoom Inc.', agent: 'Billing Specialist', action: 'Escalated: Refund Limit Exceeded', status: 'Escalated', time: '5m ago', sentiment: 'Negative' },
    { id: 'CX-4909', customer: 'Vercel Customer', agent: 'DNS Specialist', action: 'Custom Domain Bound', status: 'Success', time: '11m ago', sentiment: 'Positive' },
  ]);

  const navigate = useNavigate();

  useEffect(() => {
    const actions = [
      { id: 'CX-4916', customer: 'Tesla Corp', agent: 'Setup Specialist', action: 'MFA Deactivated', status: 'Success', time: 'Just now', sentiment: 'Positive' },
      { id: 'CX-4915', customer: 'Airbnb Support', agent: 'Refund Specialist', action: 'Escalated: Suspicious Activity', status: 'Escalated', time: 'Just now', sentiment: 'Negative' },
      { id: 'CX-4914', customer: 'GitHub Enterprise', agent: 'Billing Specialist', action: 'Subscription Upgraded', status: 'Success', time: 'Just now', sentiment: 'Positive' },
    ];
    const interval = setInterval(() => {
      const randomAction = actions[Math.floor(Math.random() * actions.length)];
      setLiveTickets(prev => [
        { ...randomAction, id: `CX-${Math.floor(Math.random() * 1000) + 5000}`, time: 'Just now' },
        ...prev.slice(0, 3)
      ]);
    }, 12000);
    return () => clearInterval(interval);
  }, []);

  const stats = [
    { label: 'Autonomous Resolutions', value: '84.6%', change: '+3.2% vs yesterday', icon: CheckCircle2, color: 'text-accentemerald bg-emerald-50' },
    { label: 'AI Agent Handling Time', value: '11.8s', change: 'Human average: 14.5m', icon: Clock, color: 'text-primary bg-blue-50' },
    { label: 'Active Sessions', value: '142', change: 'Processing peak loads', icon: Activity, color: 'text-primary bg-indigo-50' },
    { label: 'Explainable Reasoning Runs', value: '19,410', change: '100% Chain-of-Thought logged', icon: Brain, color: 'text-accentorange bg-amber-50' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* STATS ROW */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">{stat.label}</span>
                  <h3 className="text-2xl font-bold text-slate-800 mt-1">{stat.value}</h3>
                </div>
                <div className={`p-2.5 rounded-lg ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-3.5 flex items-center gap-1">
                <span className="text-xs font-medium text-slate-500">{stat.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* DASHBOARD GRID CONTENT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LIVE ACTIVITY FEED */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col justify-between">
          <div>
            <div className="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Autonomous Agent Activity Logs</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">Real-time processing feed across integration pipelines</p>
              </div>
              <div 
                onClick={() => navigate('/reasoning')}
                className="flex items-center gap-1.5 text-xs text-primary font-semibold hover:underline cursor-pointer"
              >
                <span>View reasoning runs</span>
                <ArrowUpRight className="w-4 h-4" />
              </div>
            </div>
            
            <div className="divide-y divide-slate-100">
              {liveTickets.map((ticket, index) => (
                <div 
                  key={index} 
                  onClick={() => navigate('/tickets')}
                  className="px-6 py-4 flex items-center justify-between hover:bg-slate-50/60 cursor-pointer transition-colors duration-150"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded">
                      {ticket.id}
                    </span>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-800">{ticket.customer}</span>
                      <span className="text-[11px] text-slate-400 mt-0.5">{ticket.agent}</span>
                    </div>
                  </div>

                  <div className="text-left max-w-xs truncate">
                    <span className="text-xs text-slate-600 font-medium">{ticket.action}</span>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      ticket.sentiment === 'Positive' 
                        ? 'bg-emerald-50 text-accentemerald border-emerald-100'
                        : ticket.sentiment === 'Neutral'
                        ? 'bg-slate-50 text-slate-600 border-slate-100'
                        : 'bg-red-50 text-accentred border-red-100'
                    }`}>
                      {ticket.sentiment}
                    </span>

                    <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                      ticket.status === 'Success' 
                        ? 'bg-emerald-50 text-accentemerald border-emerald-100' 
                        : 'bg-red-50 text-accentred border-red-100 animate-pulse'
                    }`}>
                      {ticket.status}
                    </span>

                    <span className="text-[10px] text-slate-400 font-medium w-14 text-right">{ticket.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-slate-100 bg-slate-50/30 text-center">
            <span className="text-xs text-slate-400 font-medium">Monitoring active streams</span>
          </div>
        </div>

        {/* SENTIMENT & CRITICAL PIPELINE INDEX */}
        <div className="space-y-6">
          
          {/* CRITICAL SENTIMENT ALERTS */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Critical Sentiment Alerts</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">High-priority ticket escalations requiring human backup</p>
            </div>
            
            <div className="space-y-3">
              <div className="p-3 bg-red-50 border border-red-100 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-accentred shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex justify-between">
                    <span className="text-xs font-bold text-accentred">Incident #CX-4910</span>
                    <span className="text-[10px] text-slate-400 font-medium">5m ago</span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1">
                    Zoom Inc. requested refund above standard AI limit ($1500). Customer expressed anger.
                  </p>
                  <button 
                    onClick={() => navigate('/tickets')}
                    className="text-[10px] text-primary hover:underline font-bold mt-2 cursor-pointer"
                  >
                    Takeover Ticket
                  </button>
                </div>
              </div>

              <div className="p-3 bg-amber-50 border border-amber-100 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-accentorange shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex justify-between">
                    <span className="text-xs font-bold text-accentorange">Incident #CX-4892</span>
                    <span className="text-[10px] text-slate-400 font-medium">1h ago</span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1">
                    Snowflake API key rotating agent loop detected. Autopilot paused agent.
                  </p>
                  <button 
                    onClick={() => navigate('/reasoning')}
                    className="text-[10px] text-primary hover:underline font-bold mt-2 cursor-pointer"
                  >
                    Inspect Reasoning
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* SYSTEM PERFORMANCE & DISPATCH */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Autopilot Integrity</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Autonomous core system health status</p>
            </div>
            
            <div className="space-y-3.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Autonomous API Engine</span>
                <span className="font-semibold text-accentemerald flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-accentemerald rounded-full animate-pulse"></span> Operational
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Reasoning Vector Database</span>
                <span className="font-semibold text-accentemerald flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-accentemerald rounded-full"></span> Active (4.2ms query latency)
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Twilio Alert Gateway</span>
                <span className="font-semibold text-accentemerald flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-accentemerald rounded-full"></span> Standby
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Auto-Escalation Engine</span>
                <span className="font-semibold text-accentemerald flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-accentemerald rounded-full"></span> Armed
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
