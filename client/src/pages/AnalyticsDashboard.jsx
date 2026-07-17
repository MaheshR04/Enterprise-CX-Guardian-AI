import React from 'react';
import { 
  TrendingUp, 
  Coins, 
  Activity, 
  ShieldCheck, 
  HelpCircle, 
  BarChart4, 
  Flame, 
  Smile, 
  Compass 
} from 'lucide-react';

export default function AnalyticsDashboard() {
  const stats = [
    { label: 'Calculated Cost Savings', value: '$24,912.40', change: 'Based on $12.50 per manual ticket', icon: Coins, color: 'text-accentemerald bg-emerald-50' },
    { label: 'Token Efficiency Index', value: '0.94 / 1.0', change: '8.4% less prompt overhead this week', icon: TrendingUp, color: 'text-primary bg-blue-50' },
    { label: 'SLA Success Rate', value: '99.98%', change: '2 breaches prevented by AI bypass', icon: ShieldCheck, color: 'text-primary bg-indigo-50' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* HEADER */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800">CX Automation & Cost Analytics</h3>
        <p className="text-[11px] text-slate-400 mt-0.5">Track financial performance, token consumption, and automation margins</p>
      </div>

      {/* KPI ROWS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">{stat.label}</span>
                  <h3 className="text-2xl font-bold text-slate-800 mt-1">{stat.value}</h3>
                </div>
                <div className={`p-2.5 rounded-lg ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <p className="text-[11px] text-slate-500 font-medium mt-3.5">{stat.change}</p>
            </div>
          );
        })}
      </div>

      {/* DETAILED METRICS CHART BLOCKS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* AUTOMATION FUNNEL CHART */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
          <div>
            <h3 className="text-sm font-bold text-slate-800">Resolution Funnel Volume</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Autonomous routing volumes for the current billing cycle</p>
          </div>

          <div className="space-y-4">
            
            {/* Opened tickets */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-600">1. Total Inquiries Opened</span>
                <span className="text-slate-800">14,290</span>
              </div>
              <div className="h-6 w-full bg-slate-100 rounded-lg overflow-hidden relative">
                <div className="h-full bg-slate-300 rounded-lg" style={{ width: '100%' }}></div>
                <span className="text-[10px] font-bold text-slate-700 absolute inset-y-1.5 left-3">100% Volume</span>
              </div>
            </div>

            {/* AI parsed */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-600">2. Parsed by AI Guardians</span>
                <span className="text-slate-800">12,490</span>
              </div>
              <div className="h-6 w-full bg-slate-100 rounded-lg overflow-hidden relative">
                <div className="h-full bg-blue-400 rounded-lg" style={{ width: '87.4%' }}></div>
                <span className="text-[10px] font-bold text-white absolute inset-y-1.5 left-3">87.4% Coverage</span>
              </div>
            </div>

            {/* Resolved */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-600">3. Resolved Autonomously</span>
                <span className="text-slate-800">10,566</span>
              </div>
              <div className="h-6 w-full bg-slate-100 rounded-lg overflow-hidden relative">
                <div className="h-full bg-accentemerald rounded-lg" style={{ width: '73.9%' }}></div>
                <span className="text-[10px] font-bold text-white absolute inset-y-1.5 left-3">73.9% Net Resolution Rate</span>
              </div>
            </div>

            {/* Human escalated */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-600">4. Escalled to Support Agents</span>
                <span className="text-slate-800">1,924</span>
              </div>
              <div className="h-6 w-full bg-slate-100 rounded-lg overflow-hidden relative">
                <div className="h-full bg-red-400 rounded-lg" style={{ width: '13.5%' }}></div>
                <span className="text-[10px] font-bold text-white absolute inset-y-1.5 left-3">13.5% Human Takeover</span>
              </div>
            </div>

          </div>
        </div>

        {/* SENTIMENT & SEGMENT BREAKDOWN (RIGHT) */}
        <div className="space-y-6">
          
          {/* Sentiment Gauge */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Sentiment Distribution</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Average customer sentiment classification metrics</p>
            </div>
            
            <div className="space-y-3.5">
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                  <span>Positive Sentiment</span>
                  <span className="text-accentemerald">75%</span>
                </div>
                <div className="w-full h-2 bg-slate-150 rounded-full overflow-hidden">
                  <div className="h-full bg-accentemerald" style={{ width: '75%' }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                  <span>Neutral / Inquisitive</span>
                  <span className="text-slate-600">20%</span>
                </div>
                <div className="w-full h-2 bg-slate-150 rounded-full overflow-hidden">
                  <div className="h-full bg-slate-400" style={{ width: '20%' }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                  <span>Angry / Critical Flags</span>
                  <span className="text-accentred">5%</span>
                </div>
                <div className="w-full h-2 bg-slate-150 rounded-full overflow-hidden">
                  <div className="h-full bg-accentred" style={{ width: '5%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Department automation rate */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">On-Target Automation Rates</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Departmental workflow conversion target thresholds</p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between items-center border-b border-slate-50 pb-1.5">
                <span className="text-slate-500 font-medium">Billing & Disputes</span>
                <span className="font-bold text-slate-800">92.4%</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-50 pb-1.5">
                <span className="text-slate-500 font-medium">Domain Configs</span>
                <span className="font-bold text-slate-800">81.0%</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-50 pb-1.5">
                <span className="text-slate-500 font-medium">Onboarding Specialist</span>
                <span className="font-bold text-slate-800">75.5%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">MFA Security Resets</span>
                <span className="font-bold text-slate-800">68.2%</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
