import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Eye, EyeOff, Lock, Mail, Building } from 'lucide-react';

export default function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();
    // Simulate company registered, navigate to login
    navigate('/login');
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
            Protect and Scale Customer Operations.
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Link Zendesk or Salesforce accounts in seconds. Configure safety workflows, 
            empower autonomous autopilots, and retain full oversight of automated ticketing metrics.
          </p>
        </div>

        <div className="z-10 flex justify-between items-center text-[10px] text-slate-500 font-semibold tracking-wider uppercase border-t border-slate-800 pt-6">
          <span>Enterprise Registration Portal</span>
          <span>Version 1.4.0</span>
        </div>

      </div>

      {/* RIGHT COLUMN: REGISTER FORM */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center px-6 sm:px-12 lg:px-20 bg-white">
        <div className="max-w-sm w-full mx-auto space-y-8">
          
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Register Corporate Account</h1>
            <p className="text-[11px] text-slate-400 mt-1 font-medium">Onboard your enterprise organization to CX Guardian</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            
            {/* COMPANY NAME */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Company name</label>
              <div className="relative">
                <Building className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Acme Corp"
                  required
                  className="w-full bg-slate-50 border border-slate-200 pl-9 pr-4 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors"
                />
              </div>
            </div>

            {/* EMAIL */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Corporate Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@company.com"
                  required
                  className="w-full bg-slate-50 border border-slate-200 pl-9 pr-4 py-2.5 rounded-lg text-xs outline-none focus:border-primary focus:bg-white transition-colors"
                />
              </div>
            </div>

            {/* PASSWORD */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Create password</label>
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

            {/* AGREEMENT CHECKBOX */}
            <div className="flex items-start gap-2 pt-1">
              <input
                type="checkbox"
                id="terms"
                required
                className="w-3.5 h-3.5 mt-0.5 border-slate-300 rounded text-primary focus:ring-primary focus:ring-offset-0 cursor-pointer"
              />
              <label htmlFor="terms" className="text-[10px] text-slate-500 font-medium leading-relaxed cursor-pointer">
                I agree to the <a href="#" className="text-primary hover:underline font-semibold">Terms of Service</a> and <a href="#" className="text-primary hover:underline font-semibold">Privacy Policy</a>, including Duty of Care data terms.
              </label>
            </div>

            {/* SUBMIT BUTTON */}
            <button
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover text-white text-xs font-bold py-3 rounded-lg shadow-sm shadow-blue-500/10 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              Onboard Organization <ArrowRight className="w-4 h-4" />
            </button>

          </form>

          <div className="text-center pt-2">
            <span className="text-[11px] text-slate-500 font-medium">Already have a company portal? </span>
            <Link to="/login" className="text-[11px] text-primary hover:underline font-bold">
              Sign In
            </Link>
          </div>

        </div>
      </div>

    </div>
  );
}
