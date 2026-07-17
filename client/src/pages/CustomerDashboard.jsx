import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, 
  Clock, 
  HelpCircle, 
  Send, 
  MessageSquare,
  AlertCircle,
  FileText,
  BadgeAlert,
  ArrowRight
} from 'lucide-react';

export default function CustomerDashboard() {
  const [tickets, setTickets] = useState([
    { id: 'CX-4912', subject: 'Refund accidental seat purchase', category: 'Billing', status: 'Resolved', isAiResolved: true, date: '1h ago' },
    { id: 'CX-4890', subject: 'Custom domain SSL binding failure', category: 'Technical', status: 'Resolved', isAiResolved: true, date: '2 days ago' },
    { id: 'CX-4712', subject: 'Reset MFA keys lockout', category: 'Security', status: 'Resolved', isAiResolved: false, date: '1 week ago' },
    { id: 'CX-4919', subject: 'Billing cycle error on credit card sync', category: 'Billing', status: 'Processing', isAiResolved: true, date: 'Just now' },
  ]);

  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Billing');
  const [priority, setPriority] = useState('Medium');
  const navigate = useNavigate();

  const handleCreateTicket = (e) => {
    e.preventDefault();
    const newId = `CX-${Math.floor(Math.random() * 1000) + 5000}`;
    const newTicket = {
      id: newId,
      subject,
      category,
      status: 'Processing',
      isAiResolved: true,
      date: 'Just now'
    };
    setTickets([newTicket, ...tickets]);
    setSubject('');
    setDescription('');
    // Mock navigating to tickets workspace for interactive feel
    navigate('/tickets');
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* CUSTOMER GREETING BAR */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-800">Customer Self-Service Hub</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Welcome back, Sarah (Corporate account: Microsoft Enterprise)</p>
        </div>
        <div className="bg-blue-50 text-primary border border-blue-100 rounded-lg px-4 py-2 text-xs font-semibold">
          SLA Level: Premium Gold (2h response guarantee)
        </div>
      </div>

      {/* STATS OVERVIEW */}
      <div className="grid grid-cols-3 gap-5">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm text-center">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Resolved Autonomously</span>
          <span className="text-xl font-extrabold text-accentemerald block mt-1">3 Tickets</span>
          <span className="text-[9px] text-slate-400 font-semibold block mt-1">Via CX Guardian AI</span>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm text-center">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Pending Actions</span>
          <span className="text-xl font-extrabold text-slate-800 block mt-1">1 Ticket</span>
          <span className="text-[9px] text-slate-400 font-semibold block mt-1">Analyzing details</span>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm text-center">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">SLA Compliance</span>
          <span className="text-xl font-extrabold text-primary block mt-1">100%</span>
          <span className="text-[9px] text-slate-400 font-semibold block mt-1">All thresholds met</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LOG NEW TICKET FORM (LEFT) */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-800">Submit New Support Case</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Assigned instantly to our autonomous guard network</p>
          </div>

          <form onSubmit={handleCreateTicket} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Issue Subject</label>
              <input
                type="text"
                placeholder="Briefly state the issue..."
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 px-3 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors cursor-pointer"
                >
                  <option value="Billing">Billing Inquiry</option>
                  <option value="Technical">Technical SSL/DNS</option>
                  <option value="Security">Security Lockout</option>
                  <option value="Onboarding">Onboarding</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors cursor-pointer"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Full Description</label>
              <textarea
                rows="4"
                placeholder="Detail error codes, steps to reproduce, or account IDs..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 px-3 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors resize-none"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover text-white text-xs font-bold py-3 rounded-lg shadow-sm shadow-blue-500/10 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              Dispatch to AI Autopilot <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

        {/* TICKET TRACKER LIST (RIGHT) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col justify-between">
          <div>
            <div className="px-6 py-5 border-b border-slate-200 bg-slate-50/50">
              <h3 className="text-sm font-bold text-slate-800">Support Request History</h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Inspect open tickets and AI resolution reasoning sheets</p>
            </div>

            <div className="divide-y divide-slate-100">
              {tickets.map((t, idx) => (
                <div 
                  key={idx} 
                  onClick={() => navigate('/tickets')}
                  className="px-6 py-4 flex items-center justify-between hover:bg-slate-50/60 cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                      {t.id}
                    </span>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-800">{t.subject}</span>
                      <span className="text-[10px] text-slate-400 mt-0.5">Category: {t.category}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {t.isAiResolved && (
                      <span className="text-[9px] font-extrabold bg-blue-50 border border-blue-100 text-primary px-2 py-0.5 rounded-full flex items-center gap-1">
                        AI Autopilot Guard
                      </span>
                    )}

                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      t.status === 'Resolved' 
                        ? 'bg-emerald-50 text-accentemerald border-emerald-100' 
                        : 'bg-amber-50 text-accentorange border-amber-100 animate-pulse'
                    }`}>
                      {t.status}
                    </span>

                    <span className="text-[10px] text-slate-400 font-medium w-16 text-right">{t.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-slate-100 bg-slate-50/30 flex justify-between items-center text-[10px] text-slate-400 font-medium">
            <span>Click on any ticket to open live chat console</span>
            <span className="text-primary font-semibold flex items-center gap-1 cursor-pointer">
              Go to Workspace <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
