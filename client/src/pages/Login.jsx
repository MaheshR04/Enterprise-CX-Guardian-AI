import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Eye, EyeOff, Lock, Mail } from 'lucide-react';

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('admin@company.com');
  const [password, setPassword] = useState('password123');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // Simulate navigation to dashboard
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex overflow-hidden font-sans">
      
      {/* LEFT COLUMN: BRAND VISUAL PANEL */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#1E293B] text-slate-300 flex-col justify-between p-12 relative overflow-hidden">
        
        {/* Background gradient effects */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] -mr-40 -mt-40"></div>
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px] -ml-40 -mb-40"></div>
        
        <div className="z-10 flex items-center gap-3">
          <div className="bg-primary flex items-center justify-center p-2.5 rounded-xl text-white shadow-lg shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <span className="font-extrabold text-white text-lg tracking-tight">
            CX Guardian AI
          </span>
        </div>

        <div className="z-10 max-w-md">
          <h2 className="text-3xl font-extrabold text-white leading-tight mb-4 tracking-tight">
            Deploy Autonomous Agents with Complete Explainability.
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Ensure customer experience excellence, audit reasoning loops in real-time, 
            and automate CRM workflows securely under enterprise guardrails.
          </p>
        </div>

        <div className="z-10 flex justify-between items-center text-[10px] text-slate-500 font-semibold tracking-wider uppercase border-t border-slate-800 pt-6">
          <span>Enterprise Autopilot Portal</span>
          <span>Version 1.4.0</span>
        </div>

      </div>

      {/* RIGHT COLUMN: LOGIN FORM */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center px-6 sm:px-12 lg:px-20 bg-white">
        <div className="max-w-sm w-full mx-auto space-y-8">
          
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Sign In to Dashboard</h1>
            <p className="text-[11px] text-slate-400 mt-1 font-medium">Access your enterprise autonomous CX cockpit</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            
            {/* EMAIL */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Corporate Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  className="w-full bg-slate-50 border border-slate-200 pl-9 pr-4 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors"
                />
              </div>
            </div>

            {/* PASSWORD */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Password</label>
                <a href="#" className="text-[10px] text-primary hover:underline font-semibold">Forgot Password?</a>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full bg-slate-50 border border-slate-200 pl-9 pr-10 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* REMEMBER ME */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="remember"
                  className="w-3.5 h-3.5 border-slate-300 rounded text-primary focus:ring-primary focus:ring-offset-0 cursor-pointer"
                />
                <label htmlFor="remember" className="text-[11px] text-slate-500 font-medium cursor-pointer">
                  Keep me logged in for 30 days
                </label>
              </div>
            </div>

            {/* SUBMIT BUTTON */}
            <button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover text-white text-xs font-bold py-3 rounded-lg shadow-sm shadow-blue-500/10 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              Sign In to Console <ArrowRight className="w-4 h-4" />
            </button>

          </form>

          <div className="text-center pt-2">
            <span className="text-[11px] text-slate-500 font-medium">Don't have an enterprise account? </span>
            <Link to="/register" className="text-[11px] text-primary hover:underline font-bold">
              Register Company
            </Link>
          </div>

        </div>
      </div>

    </div>
  );
}
