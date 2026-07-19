import React from 'react';

export const NotFoundPage = () => (
  <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-6">
    <div className="text-center max-w-md bg-slate-800/80 p-8 rounded-3xl border border-slate-700 backdrop-blur-xl shadow-2xl">
      <div className="text-7xl font-extrabold text-indigo-500 mb-2">404</div>
      <h1 className="text-2xl font-bold mb-3">Page Not Found</h1>
      <p className="text-slate-400 text-sm mb-8">
        The page you are looking for doesn't exist or has been moved to another route in Enterprise CX Guardian AI.
      </p>
      <a
        href="/"
        className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-all shadow-lg shadow-indigo-600/30"
      >
        <span>←</span> Back to Dashboard
      </a>
    </div>
  </div>
);

export default NotFoundPage;
