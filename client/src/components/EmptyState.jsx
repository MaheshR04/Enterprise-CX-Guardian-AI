import React from 'react';

export const EmptyState = ({ title = 'No Data Found', message = 'There are no items to display at this time.', icon = '📭', action = null }) => (
  <div className="flex flex-col items-center justify-center p-12 text-center bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 my-4">
    <div className="text-5xl mb-4 animate-bounce">{icon}</div>
    <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-1">{title}</h3>
    <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-6">{message}</p>
    {action && action}
  </div>
);

export default EmptyState;
