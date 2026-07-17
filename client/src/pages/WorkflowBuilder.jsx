import React, { useState } from 'react';
import { 
  Plus, 
  Trash2, 
  GitCommit, 
  HelpCircle, 
  Play, 
  Save, 
  Zap, 
  ShieldAlert, 
  Send,
  Sliders,
  CheckCircle,
  GitBranch
} from 'lucide-react';

export default function WorkflowBuilder() {
  const [workflows, setWorkflows] = useState([
    {
      id: 1,
      name: 'Billing Dispute Autonomous Resolution',
      description: 'Auto-handles customer requests for refunds and subscription disputes',
      active: true,
      nodes: [
        { type: 'Trigger', title: 'Incoming Ticket', desc: 'Category matching "Refund" or "Billing Inquiry"', status: 'active' },
        { type: 'AI Decision', title: 'Reasoning Engine', desc: 'Predict fraud risk and evaluate payment logs', status: 'active' },
        { type: 'Condition', title: 'Refund Limit Filter', desc: 'If Refund Amount is < $100 USD', status: 'active' },
        { type: 'Action', title: 'Stripe Refund API', desc: 'Approve automatically, trigger refund, email customer', status: 'success' },
      ]
    },
    {
      id: 2,
      name: 'Critical Sentiment Protection Hook',
      description: 'Escalates anger-flagged conversations instantly to Slack Support channel',
      active: false,
      nodes: [
        { type: 'Trigger', title: 'Sentiment Drop Alert', desc: 'Sentiment Score falling below 0.35', status: 'active' },
        { type: 'AI Decision', title: 'Sentiment Classifier', desc: 'Flag user frustration intensity and core complaints', status: 'active' },
        { type: 'Action', title: 'Pause Autonomous Autopilot', desc: 'Freeze autonomous replies to prevent escalation loops', status: 'active' },
        { type: 'Action', title: 'Human Takeover Notification', desc: 'Post ticket logs to Slack channel #support-alerts', status: 'success' },
      ]
    }
  ]);

  const [activeWorkflow, setActiveWorkflow] = useState(workflows[0]);
  const [showAddNodeModal, setShowAddNodeModal] = useState(false);

  const toggleWorkflowStatus = (id) => {
    setWorkflows(prev => prev.map(w => w.id === id ? { ...w, active: !w.active } : w));
    if (activeWorkflow.id === id) {
      setActiveWorkflow(prev => ({ ...prev, active: !prev.active }));
    }
  };

  const handleAddNode = (type, title, desc) => {
    const newNode = { type, title, desc, status: 'active' };
    const updatedNodes = [...activeWorkflow.nodes, newNode];
    const updatedWorkflow = { ...activeWorkflow, nodes: updatedNodes };
    
    setWorkflows(prev => prev.map(w => w.id === activeWorkflow.id ? updatedWorkflow : w));
    setActiveWorkflow(updatedWorkflow);
    setShowAddNodeModal(false);
  };

  const handleDeleteNode = (index) => {
    const updatedNodes = activeWorkflow.nodes.filter((_, i) => i !== index);
    const updatedWorkflow = { ...activeWorkflow, nodes: updatedNodes };
    
    setWorkflows(prev => prev.map(w => w.id === activeWorkflow.id ? updatedWorkflow : w));
    setActiveWorkflow(updatedWorkflow);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* HEADER SECTION */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div>
          <h3 className="text-sm font-bold text-slate-800">Autonomous Workflow Recipes</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">Automate decision trees using LLM reasoning conditions</p>
        </div>
        <div className="flex gap-2">
          <button className="bg-slate-100 text-slate-600 px-3.5 py-1.5 rounded-lg text-xs font-semibold hover:bg-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer">
            <Play className="w-3.5 h-3.5" /> Test Simulation
          </button>
          <button className="bg-primary text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold hover:bg-primary-hover flex items-center gap-1.5 shadow-sm shadow-blue-500/10 transition-colors cursor-pointer">
            <Save className="w-3.5 h-3.5" /> Save Changes
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* WORKFLOW LIST (LEFT SIDE) */}
        <div className="lg:col-span-1 space-y-3">
          {workflows.map(wf => (
            <div 
              key={wf.id}
              onClick={() => setActiveWorkflow(wf)}
              className={`p-4 rounded-xl border text-left cursor-pointer transition-all duration-200 ${
                activeWorkflow.id === wf.id 
                  ? 'bg-white border-primary shadow-md' 
                  : 'bg-white/80 border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex justify-between items-start">
                <h4 className="text-xs font-bold text-slate-800 pr-2 line-clamp-1">{wf.name}</h4>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleWorkflowStatus(wf.id);
                  }}
                  className={`w-8 h-4 rounded-full transition-colors relative ${wf.active ? 'bg-accentemerald' : 'bg-slate-300'}`}
                >
                  <span className={`w-3.5 h-3.5 bg-white rounded-full absolute top-0.25 transition-all ${
                    wf.active ? 'right-0.5' : 'left-0.5'
                  }`} />
                </button>
              </div>
              <p className="text-[10px] text-slate-400 mt-2 line-clamp-2 leading-relaxed">{wf.description}</p>
              <div className="flex items-center gap-1.5 mt-3 text-[10px] font-semibold text-slate-500">
                <GitCommit className="w-3.5 h-3.5" /> {wf.nodes.length} Configured Steps
              </div>
            </div>
          ))}
        </div>

        {/* WORKFLOW CANVAS (RIGHT SIDE) */}
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col justify-between min-h-[480px]">
          <div>
            <div className="flex justify-between items-center border-b border-slate-100 pb-4 mb-6">
              <div>
                <h3 className="text-sm font-bold text-slate-800">{activeWorkflow.name}</h3>
                <span className="text-[11px] text-slate-400 mt-0.5">Visual Autonomous Architecture Flow</span>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                activeWorkflow.active 
                  ? 'bg-emerald-50 text-accentemerald border-emerald-100' 
                  : 'bg-slate-50 text-slate-400 border-slate-200'
              }`}>
                {activeWorkflow.active ? 'ACTIVE AUTOPILOT' : 'PAUSED'}
              </span>
            </div>

            {/* NODES TIMELINE CANVAS */}
            <div className="space-y-6 relative before:absolute before:left-5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
              {activeWorkflow.nodes.map((node, idx) => (
                <div key={idx} className="flex items-start gap-4 relative group">
                  
                  {/* Node icon indicator */}
                  <div className={`w-10 h-10 rounded-xl border flex items-center justify-center shrink-0 z-10 shadow-sm ${
                    node.type === 'Trigger' ? 'bg-blue-50 border-blue-100 text-primary' :
                    node.type === 'AI Decision' ? 'bg-purple-50 border-purple-100 text-purple-600' :
                    node.type === 'Condition' ? 'bg-amber-50 border-amber-100 text-accentorange' :
                    'bg-emerald-50 border-emerald-100 text-accentemerald'
                  }`}>
                    {node.type === 'Trigger' && <Zap className="w-5 h-5" />}
                    {node.type === 'AI Decision' && <Sliders className="w-5 h-5" />}
                    {node.type === 'Condition' && <GitBranch className="w-5 h-5" />}
                    {node.type === 'Action' && <CheckCircle className="w-5 h-5" />}
                  </div>

                  {/* Node content card */}
                  <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-4 flex justify-between items-start hover:border-slate-300 transition-colors">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">{node.type}</span>
                        <span className="h-1 w-1 bg-slate-300 rounded-full"></span>
                        <h4 className="text-xs font-bold text-slate-800">{node.title}</h4>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">{node.desc}</p>
                    </div>
                    <button 
                      onClick={() => handleDeleteNode(idx)}
                      className="text-slate-400 hover:text-accentred p-1 rounded hover:bg-slate-100 transition-colors opacity-0 group-hover:opacity-100 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                </div>
              ))}
            </div>
          </div>

          {/* ADD STEP BUTTON */}
          <div className="mt-8 pt-4 border-t border-slate-100 flex justify-between items-center">
            <button 
              onClick={() => setShowAddNodeModal(true)}
              className="border border-slate-200 text-slate-600 hover:border-primary hover:text-primary px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Add Workflow Node
            </button>
            <span className="text-[10px] text-slate-400 font-medium">Nodes run linearly left-to-right</span>
          </div>
        </div>

      </div>

      {/* ADD NODE MODAL (MOCK) */}
      {showAddNodeModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-filter backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-white border border-slate-200 rounded-xl shadow-xl w-full max-w-md p-6 animate-in scale-in duration-200">
            <h3 className="text-sm font-bold text-slate-800">Add Workflow Step</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">Select step type and write conditions</p>
            
            <div className="grid grid-cols-2 gap-3 mt-4">
              <button 
                onClick={() => handleAddNode('Trigger', 'Slack Trigger Alert', 'Incoming message in #urgent-support')}
                className="p-3 border border-slate-200 rounded-xl text-left hover:border-primary group transition-all"
              >
                <Zap className="w-5 h-5 text-primary mb-2 group-hover:scale-105 transition-transform" />
                <span className="text-xs font-bold text-slate-800 block">Trigger Node</span>
                <span className="text-[9px] text-slate-400 block mt-0.5">Detects system webhook events</span>
              </button>
              <button 
                onClick={() => handleAddNode('AI Decision', 'Fraud Assessment Agent', 'Verify purchase date vs dispute history')}
                className="p-3 border border-slate-200 rounded-xl text-left hover:border-primary group transition-all"
              >
                <Sliders className="w-5 h-5 text-purple-600 mb-2 group-hover:scale-105 transition-transform" />
                <span className="text-xs font-bold text-slate-800 block">AI Agent Node</span>
                <span className="text-[9px] text-slate-400 block mt-0.5">Autonomous LLM reasoning</span>
              </button>
              <button 
                onClick={() => handleAddNode('Condition', 'Geo Filter Check', 'If customer country matches EEA list')}
                className="p-3 border border-slate-200 rounded-xl text-left hover:border-primary group transition-all"
              >
                <GitBranch className="w-5 h-5 text-accentorange mb-2 group-hover:scale-105 transition-transform" />
                <span className="text-xs font-bold text-slate-800 block">Condition Node</span>
                <span className="text-[9px] text-slate-400 block mt-0.5">Linear branch filters</span>
              </button>
              <button 
                onClick={() => handleAddNode('Action', 'Close Conversation API', 'Set Zendesk ticket status to Closed')}
                className="p-3 border border-slate-200 rounded-xl text-left hover:border-primary group transition-all"
              >
                <CheckCircle className="w-5 h-5 text-accentemerald mb-2 group-hover:scale-105 transition-transform" />
                <span className="text-xs font-bold text-slate-800 block">Action Node</span>
                <span className="text-[9px] text-slate-400 block mt-0.5">Executes API requests</span>
              </button>
            </div>
            
            <div className="mt-5 flex justify-end">
              <button 
                onClick={() => setShowAddNodeModal(false)}
                className="text-xs text-slate-500 hover:text-slate-700 font-semibold px-4 py-2 cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
