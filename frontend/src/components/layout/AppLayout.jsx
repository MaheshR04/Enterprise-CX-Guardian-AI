import { Outlet } from 'react-router-dom';
import Header from './Header.jsx';

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <Header />
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default AppLayout;
