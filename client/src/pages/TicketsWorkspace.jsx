import React, { useState } from 'react';
import { 
  ShieldCheck, 
  UserCheck2, 
  MessageSquare, 
  Brain, 
  Clock, 
  Activity, 
  Send, 
  ArrowRight, 
  Sliders, 
  Building,
  Terminal,
  Database,
  User,
  ExternalLink,
  ChevronDown,
  Sparkles
} from 'lucide-react';

export default function TicketsWorkspace() {
  const [isAutopilotActive, setIsAutopilotActive] = useState(true);
  const [messages, setMessages] = useState([
    { sender: 'user', name: 'Sarah Jenkins', role: 'VP Operations', text: 'Hi, I accidentally added 5 new seat slots on our subscription yesterday. Can you please revert this and refund the accidental seats?', time: '1h ago' },
    { sender: 'ai', name: 'Billing Guardian', role: 'AI Autopilot', text: 'Checking seat allocations and billing logs... I have validated that 5 seats were added yesterday at 4:15 PM UTC. Total dispute: $199.00 USD. Verified against Microsoft Enterprise contract details.', time: '1h ago' },
    { sender: 'ai', name: 'Billing Guardian', role: 'AI Autopilot', text: 'Stripe refund ch_1941a_ref triggered successfully. Refunded amount: $199.00 USD. Checked account limits: 5 seats deallocated from your Active Directory group. Confirming seat count reset to 40.', time: '1h ago' },
    { sender: 'user', name: 'Sarah Jenkins', role: 'VP Operations', text: 'That was incredibly fast! Thank you so much for the auto-resolution.', time: '55m ago' }
  ]);
  const [newMsg, setNewMsg] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMsg.trim()) return;
    
    // Simulate manual response or mock AI trigger
    const userMessage = {
      sender: 'admin',
      name: 'Admin Console',
      role: 'Support Manager',
      text: newMsg,
      time: 'Just now'
    };
    
    setMessages([...messages, userMessage]);
    setNewMsg('');

    if (isAutopilotActive) {
      setTimeout(() => {
        setMessages(prev => [
          ...prev,
          {
            sender: 'ai',
            name: 'Billing Guardian',
            role: 'AI Autopilot',
            text: 'Autonomous autopilot is active. Re-evaluating context... Feedback logged for workflow adjustment.',
            time: 'Just now'
          }
        ]);
      }, 1500);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] overflow-hidden gap-5 max-w-8xl mx-auto">
      
      {/* COLUMN 1: CUSTOMER 360 PANEL (LEFT) */}
      <div className="w-1/4 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col justify-between overflow-y-auto p-5 space-y-5">
        
        {/* Profile Card */}
        <div className="space-y-4 text-center">
          <div className="relative inline-block mx-auto">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center border border-slate-200">
              <User className="w-8 h-8 text-slate-500" />
            </div>
            <span className="absolute bottom-0 right-0 w-4 h-4 bg-emerald-500 border-2 border-white rounded-full"></span>
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-800">Sarah Jenkins</h4>
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">VP Operations</span>
          </div>
          
          <div className="flex justify-center gap-1.5">
            <span className="text-[9px] font-bold bg-blue-50 border border-blue-100 text-primary px-2.5 py-0.5 rounded-full">
              Gold Tier
            </span>
            <span className="text-[9px] font-bold bg-emerald-50 border border-emerald-100 text-accentemerald px-2.5 py-0.5 rounded-full">
              CSAT 4.8/5
            </span>
          </div>
        </div>

        <div className="h-px bg-slate-150"></div>

        {/* Customer Details metadata */}
        <div className="space-y-4">
          <div>
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Account Association</span>
            <div className="flex items-center gap-2 mt-1">
              <Building className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-bold text-slate-800">Microsoft Corp</span>
            </div>
          </div>

          <div>
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Contract Details</span>
            <div className="space-y-1.5 mt-1 text-[11px] text-slate-600">
              <div className="flex justify-between">
                <span>ARR Value</span>
                <span className="font-bold text-slate-800">$154,200</span>
              </div>
              <div className="flex justify-between">
                <span>Active Seats</span>
                <span className="font-bold text-slate-800">40 / 45</span>
              </div>
              <div className="flex justify-between">
                <span>Renewal Date</span>
                <span className="font-bold text-slate-800">Oct 24, 2026</span>
              </div>
            </div>
          </div>

          <div>
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Recent Touchpoints</span>
            <div className="space-y-2 mt-2 text-[10px] text-slate-500 leading-normal">
              <div className="flex gap-2 items-start">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full mt-1 shrink-0"></span>
                <span>Seat refund resolved (CX-4912) - 1h ago</span>
              </div>
              <div className="flex gap-2 items-start">
                <span className="w-1.5 h-1.5 bg-slate-300 rounded-full mt-1 shrink-0"></span>
                <span>DNS record binds verified - 2 days ago</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-auto pt-4 border-t border-slate-100 flex justify-between items-center text-[10px] text-primary hover:underline font-bold cursor-pointer">
          <span>Inspect Salesforce Data</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </div>

      </div>

      {/* COLUMN 2: ACTIVE CONVERSATION (MIDDLE) */}
      <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col justify-between">
        
        {/* Chat header controls */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center z-10 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">CX-4912</span>
            <div>
              <h3 className="text-xs font-bold text-slate-800">Refund seat allocations</h3>
              <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mt-0.5">Assigned to: Billing Specialist</p>
            </div>
          </div>

          {/* AUTOPILOT TOGGLE */}
          <div className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-xl">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">AI Autopilot</span>
            <button 
              onClick={() => setIsAutopilotActive(!isAutopilotActive)}
              className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${
                isAutopilotActive ? 'bg-primary' : 'bg-slate-300'
              }`}
            >
              <span className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-all ${
                isAutopilotActive ? 'right-0.5' : 'left-0.5'
              }`} />
            </button>
          </div>
        </div>

        {/* MESSAGES LIST AREA */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">
          {messages.map((msg, i) => (
            <div 
              key={i} 
              className={`flex flex-col max-w-[80%] ${
                msg.sender === 'user' ? 'mr-auto items-start' : 'ml-auto items-end'
              }`}
            >
              <span className="text-[9px] text-slate-400 font-bold tracking-wider uppercase mb-1">
                {msg.name} ({msg.role})
              </span>
              
              <div className={`p-3.5 rounded-xl text-xs leading-relaxed ${
                msg.sender === 'user' 
                  ? 'bg-white border border-slate-200 text-slate-700' 
                  : msg.sender === 'ai'
                  ? 'bg-blue-50 border border-blue-100 text-slate-800 font-medium'
                  : 'bg-slate-800 text-white'
              }`}>
                {msg.text}
              </div>
              
              <span className="text-[9px] text-slate-400 mt-1">{msg.time}</span>
            </div>
          ))}
        </div>

        {/* INPUT COMPOSER */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200 bg-white shrink-0">
          <div className="relative">
            <input
              type="text"
              placeholder={isAutopilotActive ? "Type response to take over from Autopilot..." : "Reply as manager console..."}
              value={newMsg}
              onChange={(e) => setNewMsg(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 pl-4 pr-10 py-3 rounded-xl text-xs outline-none focus:border-primary focus:bg-white transition-colors"
            />
            <button 
              type="submit" 
              className="absolute right-2 top-2 bg-primary hover:bg-primary-hover p-1.5 rounded-lg text-white transition-colors cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="flex justify-between items-center mt-2.5 text-[9px] text-slate-400 font-medium px-1">
            <span>SLA Response Window: 1h 4m left</span>
            <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" /> End-to-end sandbox security active</span>
          </div>
        </form>

      </div>

      {/* COLUMN 3: REAL-TIME REASONING ENGINE (RIGHT) */}
      <div className="w-1/4 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col justify-between overflow-y-auto p-5 space-y-5">
        
        <div>
          {/* Header */}
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <div>
              <h4 className="text-xs font-extrabold text-slate-800">AI Reasoning Panel</h4>
              <span className="text-[10px] text-slate-400 font-medium">Chain-of-thought inspector</span>
            </div>
            <div className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-emerald-50 text-accentemerald rounded-full border border-emerald-100 text-[10px] font-bold">
              <Sparkles className="w-3 h-3 animate-pulse" /> 98% Conf
            </div>
          </div>

          {/* Reasoning chain list */}
          <div className="space-y-4 mt-4">
            
            <div className="space-y-1">
              <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider block">1. Intent recognized</span>
              <p className="text-[10px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 leading-normal">
                Matched transcript to category: <span className="font-bold text-slate-800">Refund</span> (0.99 match probability).
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider block">2. DB context sync</span>
              <p className="text-[10px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 leading-normal">
                Found Microsoft contract data: 45 total slots, LTV $154k. Billing ID <span className="font-mono text-slate-800">usr_8192a</span>.
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider block">3. Safety limit guard</span>
              <p className="text-[10px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 leading-normal">
                Disputed refund: <span className="font-bold text-slate-800">$199.00</span>. Anomaly metrics: 0.04 risk rating (Cleared).
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider block">4. Action executed</span>
              <p className="text-[10px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 leading-normal">
                Invoked Stripe API. Result: <span className="text-accentemerald font-semibold">Success</span>. Syncing seat adjustment with active tenant accounts.
              </p>
            </div>

          </div>
        </div>

        {/* Bottom details */}
        <div className="pt-4 border-t border-slate-100 text-[10px] text-slate-400 leading-normal space-y-2">
          <div className="flex justify-between items-center">
            <span className="flex items-center gap-1"><Terminal className="w-3.5 h-3.5" /> Reasoning Run ID</span>
            <span className="font-mono text-slate-600">run_4912x</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="flex items-center gap-1"><Database className="w-3.5 h-3.5" /> Synced to CRM</span>
            <span className="text-accentemerald font-semibold">Success</span>
          </div>
        </div>

      </div>

    </div>
  );
}
