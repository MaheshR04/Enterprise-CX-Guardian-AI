function StatusBadge({ children, loading, online }) {
  const colorClass = loading
    ? 'border-amber-200 bg-amber-50 text-amber-700'
    : online
      ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
      : 'border-red-200 bg-red-50 text-red-700';

  return (
    <span className={`inline-flex w-fit items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium ${colorClass}`}>
      <span className="h-2 w-2 rounded-full bg-current" aria-hidden="true" />
      {children}
    </span>
  );
}

export default StatusBadge;
