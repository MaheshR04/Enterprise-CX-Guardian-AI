import React from 'react';
import { useTheme } from '../context/ThemeContext';

export const ThemeToggle = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm flex items-center gap-2 text-sm font-medium"
      title="Toggle Dark / Light Mode"
      aria-label="Toggle Theme"
    >
      {isDark ? (
        <>
          <span className="text-amber-400">☀️</span>
          <span className="hidden sm:inline">Light Mode</span>
        </>
      ) : (
        <>
          <span className="text-indigo-500">🌙</span>
          <span className="hidden sm:inline">Dark Mode</span>
        </>
      )}
    </button>
  );
};

export default ThemeToggle;
