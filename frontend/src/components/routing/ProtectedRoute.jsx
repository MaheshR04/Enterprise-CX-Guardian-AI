import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.js';

function ProtectedRoute({ children }) {
  const location = useLocation();
  const { initializing, isAuthenticated } = useAuth();

  if (initializing) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 text-sm font-medium text-slate-600 sm:px-6 lg:px-8">
        Checking your secure session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

export default ProtectedRoute;
