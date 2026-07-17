import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  GitFork, 
  Brain, 
  Cpu, 
  Settings2, 
  Search, 
  Bell, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  UserCheck2,
  HelpCircle
} from 'lucide-react';

export default function AppLayout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, text: "Billing Guardian auto-resolved payment dispute", type: "success" },
    { id: 2, text: "Customer sentiment drop flagged on Ticket #4912", type: "warning" },
  ]);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();

  // Helper to map route to a title
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Executive Overview';
      case '/builder':
        return 'Autonomous Workflow Builder';
      case '/reasoning':
        return 'Reasoning Engine & Explainability Hub';
      case '/agents':
        return 'Autonomous Agent Monitor';
      case '/integrations':
        return 'CRM & System Integrations';
      default:
        return 'CX Guardian Console';
    }
  };

  const navItems = [
    { to: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
    { to: '/builder', label: 'Workflow Builder', icon: GitFork },
    { to: '/reasoning', label: 'Reasoning Hub', icon: Brain },
    { to: '/agents', label: 'Agent Monitor', icon: Cpu },
    { to: '/integrations', label: 'Integrations', icon: Settings2 },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      
      {/* SIDEBAR NAVIGATION */}
      <aside 
        className={`bg-[#1E293B] text-slate-300 flex flex-col justify-between transition-all duration-300 relative border-r border-slate-800 ${
          isCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        <div>
          {/* Logo Brand area */}
          <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-800">
            <div className="bg-primary flex items-center justify-center p-2 rounded-lg text-white shadow-lg shadow-blue-500/20 shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="font-extrabold text-white text-base tracking-tight leading-tight">
                  CX GUARDIAN AI
                </span>
                <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
                  Enterprise Agent
                </span>
              </div>
            )}
          </div>

          {/* Navigation links */}
          <nav className="mt-6 px-3 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3.5 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive 
                        ? 'bg-primary text-white shadow-md shadow-blue-500/10' 
                        : 'hover:bg-slate-800 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  {!isCollapsed && <span>{item.label}</span>}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer area */}
        <div className="p-3 border-t border-slate-800">
          <div className={`flex items-center gap-3 p-2 rounded-lg bg-slate-900/50 ${isCollapsed ? 'justify-center' : ''}`}>
            <div className="relative">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white uppercase">
                AD
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-accentemerald border border-slate-900 rounded-full"></span>
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-white truncate">Admin Console</span>
                <span className="text-[10px] text-slate-400 truncate">guardian@company.com</span>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar collapse button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -right-3.5 top-6 bg-[#1E293B] border border-slate-800 text-slate-400 hover:text-white p-1 rounded-full shadow-md z-50 cursor-pointer hidden md:block"
        >
          {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* TOP NAVBAR */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-40">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              {getPageTitle()}
            </h2>
            <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-emerald-50 text-accentemerald rounded-full border border-emerald-100 text-xs font-semibold">
              <span className="w-1.5 h-1.5 bg-accentemerald rounded-full animate-ping"></span>
              4 Agents Autonomous
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* SEARCH */}
            <div className="relative hidden md:block w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search reasoning logs, nodes..."
                className="w-full bg-slate-50 border border-slate-200 pl-9 pr-4 py-1.5 rounded-lg text-xs outline-none focus:bg-white focus:border-primary transition-all duration-200"
              />
            </div>

            {/* NOTIFICATIONS */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors relative cursor-pointer"
              >
                <Bell className="w-5 h-5" />
                {notifications.length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-accentred rounded-full"></span>
                )}
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="px-4 py-1.5 border-b border-slate-100 flex justify-between items-center">
                    <span className="text-xs font-bold text-slate-800">System Logs</span>
                    <button 
                      onClick={() => setNotifications([])}
                      className="text-[10px] text-primary hover:underline"
                    >
                      Clear all
                    </button>
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-6 text-center text-xs text-slate-400">
                        No system flags reported
                      </div>
                    ) : (
                      notifications.map(notif => (
                        <div key={notif.id} className="px-4 py-3 hover:bg-slate-50 border-b border-slate-50 last:border-b-0 flex items-start gap-2.5">
                          <span className={`w-1.5 h-1.5 rounded-full mt-1.5 ${
                            notif.type === 'success' ? 'bg-accentemerald' : 'bg-accentorange'
                          }`}></span>
                          <span className="text-[11px] text-slate-600 leading-normal">{notif.text}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="h-6 w-px bg-slate-200"></div>

            {/* Help / Platform Status */}
            <div className="flex items-center gap-1 text-slate-500 text-xs font-medium">
              <HelpCircle className="w-4 h-4" />
              <span className="hidden sm:inline">Help Center</span>
            </div>
          </div>
        </header>

        {/* CONTAINER FOR OUTLET */}
        <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
          <Outlet />
        </main>
      </div>

    </div>
  );
}
