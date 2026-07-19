import React from 'react';

/**
 * Reusable Skeleton Loaders for Dashboard, Chat, and Tables.
 */
export const CardSkeleton = () => (
  <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-24"></div>
      <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-xl"></div>
    </div>
    <div className="h-8 bg-slate-300 dark:bg-slate-600 rounded w-36 mb-2"></div>
    <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-28"></div>
  </div>
);

export const ChatMessageSkeleton = ({ isUser = false }) => (
  <div className={`flex gap-3 mb-4 animate-pulse ${isUser ? 'flex-row-reverse' : ''}`}>
    <div className="w-9 h-9 rounded-full bg-slate-300 dark:bg-slate-700 flex-shrink-0"></div>
    <div className={`max-w-[70%] space-y-2 p-4 rounded-2xl ${isUser ? 'bg-indigo-100 dark:bg-indigo-900/50' : 'bg-slate-100 dark:bg-slate-800'}`}>
      <div className="h-4 bg-slate-300 dark:bg-slate-600 rounded w-48"></div>
      <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-32"></div>
    </div>
  </div>
);

export const TableRowSkeleton = ({ columns = 5 }) => (
  <tr className="animate-pulse border-b border-slate-100 dark:border-slate-800">
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="py-4 px-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-full"></div>
      </td>
    ))}
  </tr>
);
