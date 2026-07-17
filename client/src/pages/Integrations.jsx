import React, { useState } from 'react';
import { 
  CheckCircle, 
  HelpCircle, 
  Link2, 
  Link2Off, 
  RefreshCw, 
  Database,
  MessageSquare,
  Users
} from 'lucide-react';

export default function Integrations() {
  const [integrations, setIntegrations] = useState([
    { id: 1, name: 'Salesforce CRM', desc: 'Sync customer records, account tier flags, and contact hierarchies for LLM prompt context.', category: 'CRM', connected: true, status: 'Active Sync', iconBg: 'bg-sky-50 text-sky-600 border-sky-100' },
    { id: 2, name: 'Zendesk Support', desc: 'Auto-dispatch and import ticket backlogs into the AI pipeline. Closes resolved tickets.', category: 'Help Desk', connected: true, status: 'Active Sync', iconBg: 'bg-emerald-50 text-accentemerald border-emerald-100' },
    { id: 3, name: 'HubSpot Marketing', desc: 'Sync customer details and feed autonomous expansion leads directly into HubSpot deal boards.', category: 'CRM', connected: false, status: 'Disconnected', iconBg: 'bg-orange-50 text-accentorange border-orange-100' },
    { id: 4, name: 'Slack Alerts', desc: 'Broadcast critical sentiment warnings and manual agent takeover pages directly to #cx-alerts.', category: 'Communication', connected: true, status: 'Active Sync', iconBg: 'bg-purple-50 text-purple-600 border-purple-100' },
    { id: 5, name: 'Jira Software', desc: 'Let autonomous agents create technical bug logs and link context directly to developer boards.', category: 'Development', connected: false, status: 'Disconnected', iconBg: 'bg-blue-50 text-blue-600 border-blue-100' }
  ]);

  const [activeTab, setActiveTab] = useState('All');
  const [syncingId, setSyncingId] = useState(null);

  const toggleConnection = (id) => {
    setIntegrations(prev => prev.map(item => {
      if (item.id === id) {
        return {
          ...item,
          connected: !item.connected,
          status: !item.connected ? 'Active Sync' : 'Disconnected'
        };
      }
      return item;
    }));
  };

  const triggerSync = (id) => {
    setSyncingId(id);
    setTimeout(() => {
      setSyncingId(null);
    }, 1500);
  };

  const tabs = ['All', 'CRM', 'Help Desk', 'Communication', 'Development'];

  const filteredIntegrations = activeTab === 'All' 
    ? integrations 
    : integrations.filter(item => item.category === activeTab);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* INTEGRATIONS INTRO */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800">Enterprise Integrations</h3>
        <p className="text-[11px] text-slate-400 mt-0.5">Connect external platforms to feed data into autonomous agent memory cycles</p>
      </div>

      {/* FILTER TABS */}
      <div className="flex gap-2 border-b border-slate-200 pb-3">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
              activeTab === tab 
                ? 'bg-slate-800 text-white' 
                : 'text-slate-500 hover:bg-slate-100'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIntegrations.map(item => (
          <div key={item.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 flex flex-col justify-between min-h-[220px]">
            
            {/* Header info */}
            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <div className={`p-2 rounded-lg border ${item.iconBg}`}>
                  {item.name.includes('Salesforce') && <Database className="w-5 h-5" />}
                  {item.name.includes('Zendesk') && <MessageSquare className="w-5 h-5" />}
                  {item.name.includes('HubSpot') && <Users className="w-5 h-5" />}
                  {item.name.includes('Slack') && <MessageSquare className="w-5 h-5" />}
                  {item.name.includes('Jira') && <Database className="w-5 h-5" />}
                </div>

                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                  item.connected ? 'bg-emerald-50 text-accentemerald border-emerald-100' : 'bg-slate-50 text-slate-400 border-slate-250'
                }`}>
                  {item.status}
                </span>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-800">{item.name}</h4>
                <p className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase mt-0.5">{item.category}</p>
              </div>

              <p className="text-[10px] text-slate-500 leading-relaxed pt-1.5">{item.desc}</p>
            </div>

            {/* Actions button */}
            <div className="flex gap-2 pt-4 border-t border-slate-100 mt-4">
              <button 
                onClick={() => toggleConnection(item.id)}
                className={`flex-1 px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-colors border flex items-center justify-center gap-1.5 ${
                  item.connected 
                    ? 'border-slate-200 text-slate-600 hover:bg-slate-50' 
                    : 'border-primary bg-primary text-white hover:bg-primary-hover shadow-sm shadow-blue-500/10'
                }`}
              >
                {item.connected ? (
                  <>
                    <Link2Off className="w-3.5 h-3.5" /> Disconnect
                  </>
                ) : (
                  <>
                    <Link2 className="w-3.5 h-3.5" /> Connect Platform
                  </>
                )}
              </button>

              {item.connected && (
                <button 
                  onClick={() => triggerSync(item.id)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-slate-800 cursor-pointer flex items-center justify-center"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${syncingId === item.id ? 'animate-spin text-primary' : ''}`} />
                </button>
              )}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
