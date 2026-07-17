import React, { useState } from 'react';
import { 
  Search, 
  Brain, 
  Clock, 
  TrendingUp, 
  CheckCircle2, 
  Terminal, 
  Cpu, 
  HelpCircle,
  Database,
  ArrowRight
} from 'lucide-react';

export default function ReasoningHub() {
  const logs = [
    {
      id: 'CX-4912',
      customer: 'Microsoft (Enterprise)',
      time: 'Just now',
      handlingTime: '8.4s',
      confidence: 98,
      issue: 'Customer requesting subscription refund due to accidental seat purchase',
      action: 'Refund processed via Stripe, seats adjusted',
      reasoningChain: [
        { step: '1. Intent Recognition', detail: 'Parsing ticket transcript... Identified core intent as "Refund Request" with entity "Seat Allocation Dispute".' },
        { step: '2. Database Context Gathering', detail: 'Fetched user billing record ref usr_8192a. User tier: Enterprise, Billing Cycle: Monthly, Seats: 45. Last charge: 3 days ago ($1,250).' },
        { step: '3. Fraud Risk Assessment', detail: 'Evaluated billing history and anomaly metrics. Risk score: 0.04 (highly benign). No prior disputes found.' },
        { step: '4. Rule Evaluation', detail: 'Checking active recipes... Matches rule "Billing Dispute Auto-Resolution". Conditions met: Seats added < 10 days ago, total dispute < $500.' },
        { step: '5. Action Dispatch', detail: 'Invoking Stripe API (ref: ch_1941a_ref). Result: Success. Invoked Okta Sync to deallocate 5 accidental seats.' }
      ]
    },
    {
      id: 'CX-4911',
      customer: 'Stripe API User',
      time: '2m ago',
      handlingTime: '12.1s',
      confidence: 94,
      issue: 'API keys reset failed, customer locked out of dev environment',
      action: 'API key rotated, backup codes sent via Twilio',
      reasoningChain: [
        { step: '1. Intent Recognition', detail: 'Identified core intent as "Credential Reset Request" and "Access Lockout". Critical tag applied.' },
        { step: '2. Identity Verification', detail: 'Validated requesting email domains against workspace configurations. Domain validation: Passed.' },
        { step: '3. Security Logs Scan', detail: 'Scanned past 24h auth logs. No suspicious IPs or brute-force attempts recorded.' },
        { step: '4. Action Dispatch', detail: 'Rotated active developer API key. Dispatched secure login envelope using configured Twilio SMS gateway.' }
      ]
    },
    {
      id: 'CX-4909',
      customer: 'Vercel Customer',
      time: '11m ago',
      handlingTime: '9.2s',
      confidence: 97,
      issue: 'Custom domain binding failing with SSL negotiation issue',
      action: 'DNS parameters verified, Let Let\'s Encrypt SSL re-issued',
      reasoningChain: [
        { step: '1. Intent Recognition', detail: 'Identified intent: "DNS Configuration Inquiry" and "SSL Handshake Failure".' },
        { step: '2. Network Dig Tool execution', detail: 'Initiated dig trace for domain test.vercel.app. ALIAS records matching, A records resolving.' },
        { step: '3. SSL Renewal Dispatch', detail: 'Triggered SSL renewal request via Vercel Edge API gateway. Renewal successful.' }
      ]
    }
  ];

  const [activeLog, setActiveLog] = useState(logs[0]);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = logs.filter(log => 
    log.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.customer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* EXPLAINABILITY SUB-HEADER */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800">Reasoning Explainability Dashboard</h3>
        <p className="text-[11px] text-slate-400 mt-0.5">Audit Chain-of-Thought logs and model decision confidence metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LOGS LIST (LEFT) */}
        <div className="space-y-4">
          
          {/* SEARCH BAR */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by ticket ID or account name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white border border-slate-200 pl-9 pr-4 py-2 rounded-xl text-xs outline-none focus:border-primary transition-colors"
            />
          </div>

          {/* LIST */}
          <div className="space-y-2">
            {filteredLogs.map(log => (
              <div
                key={log.id}
                onClick={() => setActiveLog(log)}
                className={`p-4 rounded-xl border text-left cursor-pointer transition-all ${
                  activeLog.id === log.id 
                    ? 'bg-white border-primary shadow-md' 
                    : 'bg-white/80 border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">{log.id}</span>
                  <span className="text-[10px] text-slate-400 font-medium">{log.time}</span>
                </div>
                <h4 className="text-xs font-bold text-slate-800 mt-2 truncate">{log.customer}</h4>
                <p className="text-[10px] text-slate-500 mt-1 line-clamp-1">{log.issue}</p>
                
                <div className="flex justify-between items-center mt-3 pt-3 border-t border-slate-100 text-[10px] font-semibold text-slate-400">
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {log.handlingTime}</span>
                  <span className="text-accentemerald">{log.confidence}% AI Confidence</span>
                </div>
              </div>
            ))}
          </div>

        </div>

        {/* LOG INSPECTOR DETAIL (RIGHT) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col justify-between min-h-[500px]">
          
          <div className="space-y-6">
            
            {/* Header info */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-100 pb-5">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-0.5 rounded">
                    {activeLog.id}
                  </span>
                  <h3 className="text-sm font-bold text-slate-800">{activeLog.customer}</h3>
                </div>
                <span className="text-[10px] text-slate-400 mt-1 block">Executed Autonomous Action</span>
              </div>
              
              {/* Confidence Meter */}
              <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 shrink-0">
                <Brain className="w-5 h-5 text-primary" />
                <div>
                  <span className="text-[9px] text-slate-400 uppercase font-extrabold tracking-wider">Confidence Level</span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <div className="w-20 h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-accentemerald rounded-full" style={{ width: `${activeLog.confidence}%` }}></div>
                    </div>
                    <span className="text-xs font-bold text-slate-800">{activeLog.confidence}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Incident Summary */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 border border-slate-150 rounded-xl">
              <div>
                <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider">Customer Inquiry</span>
                <p className="text-xs font-medium text-slate-700 mt-1 leading-relaxed">{activeLog.issue}</p>
              </div>
              <div>
                <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider">Autonomous Resolution Action</span>
                <p className="text-xs font-medium text-slate-700 mt-1 leading-relaxed">{activeLog.action}</p>
              </div>
            </div>

            {/* CHAIN-OF-THOUGHT TIMELINE */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <Terminal className="w-4 h-4 text-slate-500" />
                Chain-of-Thought (Explainability Logs)
              </h4>
              
              <div className="space-y-3.5">
                {activeLog.reasoningChain.map((chain, i) => (
                  <div key={i} className="flex gap-3">
                    <div className="flex flex-col items-center shrink-0">
                      <div className="w-6 h-6 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-[10px] font-bold text-primary">
                        {i + 1}
                      </div>
                      {i < activeLog.reasoningChain.length - 1 && (
                        <div className="w-px flex-1 bg-slate-200 my-1"></div>
                      )}
                    </div>
                    <div className="flex-1 bg-slate-50/50 border border-slate-100 hover:border-slate-200 rounded-lg p-3 transition-colors">
                      <span className="text-[10px] font-extrabold text-slate-700 uppercase tracking-wider">{chain.step}</span>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{chain.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-medium">
            <span className="flex items-center gap-1"><Database className="w-3.5 h-3.5" /> Immutable audit record stored in database</span>
            <button className="text-primary hover:underline font-bold flex items-center gap-1 cursor-pointer">
              Download Audit JSON <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}
