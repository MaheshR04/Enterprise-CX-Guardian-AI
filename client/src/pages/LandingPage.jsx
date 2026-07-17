import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  ArrowRight, 
  Brain, 
  Cpu, 
  Zap, 
  Activity, 
  ChevronRight,
  Sparkles,
  GitMerge,
  MessagesSquare
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      
      {/* LANDING HEADER */}
      <header className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-slate-200 h-16 flex items-center justify-between px-6 md:px-12 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-primary flex items-center justify-center p-2 rounded-lg text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span className="font-extrabold text-slate-900 tracking-tight text-base">
            Enterprise CX Guardian AI
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link 
            to="/login" 
            className="text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Sign In
          </Link>
          <Link 
            to="/dashboard" 
            className="bg-primary hover:bg-primary-hover text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm shadow-blue-500/10 transition-colors flex items-center gap-1"
          >
            Launch Console <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 max-w-4xl mx-auto relative">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-50 border border-blue-100 text-primary rounded-full text-xs font-semibold mb-6 animate-fade-in">
          <Sparkles className="w-3.5 h-3.5" /> Autonomous AI Agent Platform
        </div>
        
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1] mb-6">
          Automate Customer Experience <br />
          <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
            With Explainable AI Autopilots
          </span>
        </h1>
        
        <p className="text-sm md:text-base text-slate-500 leading-relaxed max-w-2xl mb-10">
          An AI-powered Autonomous Customer Experience Agent that understands customers, 
          predicts issues, explains its reasoning, and automates enterprise support workflows.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link 
            to="/dashboard" 
            className="bg-primary hover:bg-primary-hover text-white text-xs font-bold px-6 py-3.5 rounded-lg shadow-md shadow-blue-500/10 transition-all flex items-center justify-center gap-1.5"
          >
            Launch Manager Console <ArrowRight className="w-4 h-4" />
          </Link>
          <Link 
            to="/customer" 
            className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold px-6 py-3.5 rounded-lg transition-all flex items-center justify-center gap-1.5"
          >
            Customer Self-Service Portal <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {/* HERO MOCK DASHBOARD */}
        <div className="mt-16 w-full max-w-3xl bg-white border border-slate-200 rounded-2xl shadow-2xl p-4 overflow-hidden transform hover:scale-[1.01] transition-transform duration-300">
          <div className="flex items-center gap-1.5 border-b border-slate-100 pb-3 mb-4">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase ml-2">Console Sandbox Mode</span>
          </div>
          
          <div className="grid grid-cols-3 gap-3 text-left">
            <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-xl">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Auto-Resolutions</span>
              <span className="text-xl font-extrabold text-slate-800 block mt-1">84.6%</span>
              <span className="text-[9px] text-accentemerald font-medium block mt-1">⚡ Autopilot enabled</span>
            </div>
            <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-xl">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">AI Handling Time</span>
              <span className="text-xl font-extrabold text-slate-800 block mt-1">11.8s</span>
              <span className="text-[9px] text-slate-400 font-medium block mt-1">Saves average 14m</span>
            </div>
            <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-xl">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Active Agents</span>
              <span className="text-xl font-extrabold text-slate-800 block mt-1">4 Running</span>
              <span className="text-[9px] text-accentemerald font-medium block mt-1">● Vector database synced</span>
            </div>
          </div>
        </div>
      </section>

      {/* CORE FEATURES GRID */}
      <section className="bg-white border-t border-slate-200 py-20 px-6 md:px-12">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Designed for Modern Enterprise Support Teams</h2>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Outperforms traditional conversational chatbots</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-3.5 p-5 border border-slate-100 rounded-xl hover:border-slate-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-primary flex items-center justify-center">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">Explainable AI Reasoning</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Auditable Chain-of-Thought logs display the exact logic pathways and payment safety scores computed for every single customer resolution.
              </p>
            </div>

            <div className="space-y-3.5 p-5 border border-slate-100 rounded-xl hover:border-slate-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <GitMerge className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">Autonomous Workflow Builder</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Connect your database models, configure webhook triggers, and write step-by-step logic rules to automate billing disputes and account setup tasks.
              </p>
            </div>

            <div className="space-y-3.5 p-5 border border-slate-100 rounded-xl hover:border-slate-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-accentemerald flex items-center justify-center">
                <Cpu className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">Customer 360 Context Integration</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Autonomous agents pull live user session statistics, check subscription tiers, and scan lifetime value context before issuing any automated refunds.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mt-auto border-t border-slate-200 bg-slate-100/50 py-8 px-6 text-center text-xs text-slate-500 font-medium">
        <p>&copy; 2026 Enterprise CX Guardian AI. Built for corporate duty-of-care pipelines.</p>
      </footer>

    </div>
  );
}
