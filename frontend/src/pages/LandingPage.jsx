import { Activity, MapPinned, ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import StatusBadge from '../components/ui/StatusBadge.jsx';
import { useApiHealth } from '../hooks/useApiHealth.js';

const features = [
  {
    icon: ShieldAlert,
    title: 'Risk-aware travel',
    description: 'Crime datasets and safety scoring will help users avoid high-risk zones.',
  },
  {
    icon: MapPinned,
    title: 'Live map foundation',
    description: 'OpenStreetMap, routing, and location tracking will plug into this frontend shell.',
  },
  {
    icon: Activity,
    title: 'Realtime alerts',
    description: 'Socket.IO is ready for live tracking, danger alerts, and guardian rooms.',
  },
];

function LandingPage() {
  const apiStatus = useApiHealth();

  return (
    <section className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8 lg:py-16">
      <div className="flex flex-col justify-center">
        <StatusBadge online={apiStatus.online} loading={apiStatus.loading}>
          {apiStatus.message}
        </StatusBadge>
        <h1 className="mt-6 max-w-3xl text-4xl font-bold leading-tight text-slate-950 sm:text-5xl">
          GuardianPath AI safety navigation starts here.
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
          This MVP foundation connects a React client to an Express API, with MongoDB and Socket.IO
          architecture ready for authentication, live tracking, safe routes, and SOS workflows.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            to="/signup"
            className="rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-brand-700"
          >
            Create Account
          </Link>
          <Link
            to="/login"
            className="rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-500 hover:text-brand-700"
          >
            Login
          </Link>
          <a
            href="http://localhost:5000/api/health"
            className="rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-500 hover:text-brand-700"
          >
            Check API
          </a>
        </div>
      </div>

      <div className="grid content-center gap-4">
        {features.map((feature) => (
          <article key={feature.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft">
            <div className="flex items-start gap-4">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-md bg-brand-50 text-brand-700">
                <feature.icon size={22} aria-hidden="true" />
              </span>
              <div>
                <h2 className="text-base font-semibold text-slate-950">{feature.title}</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">{feature.description}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default LandingPage;
