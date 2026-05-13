import { useState } from 'react';
import { LocateFixed, MapPinned, RadioTower, Siren } from 'lucide-react';
import GuardianContactsEditor from '../components/forms/GuardianContactsEditor.jsx';
import MapView from '../components/map/MapView.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { useCurrentLocation } from '../hooks/useCurrentLocation.js';
import { useLiveTracking } from '../hooks/useLiveTracking.js';
import { formatAccuracy, formatCoordinate, formatTimestamp } from '../services/mapService.js';

const cards = [
  {
    icon: LocateFixed,
    title: 'Location tracking',
    text: 'Browser geolocation is active and feeds the map marker as coordinates change.',
  },
  {
    icon: RadioTower,
    title: 'Realtime sockets',
    text: 'Socket.IO shares coordinates with the backend and private guardian rooms.',
  },
  {
    icon: Siren,
    title: 'SOS response',
    text: 'Emergency logs, alerts, and Twilio notifications will be added in Steps 7 and 8.',
  },
];

function DashboardPage() {
  const { token, updateGuardianContacts, user } = useAuth();
  const {
    error: locationError,
    isTracking,
    location,
    startTracking,
    status: locationStatus,
    stopTracking,
  } = useCurrentLocation();
  const { connectedUsers, lastSharedAt, socketError, socketId, socketStatus } = useLiveTracking({
    enabled: isTracking,
    location,
    token,
  });
  const [guardianContacts, setGuardianContacts] = useState(user?.guardianContacts || []);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const saveContacts = async (event) => {
    event.preventDefault();
    setStatus('');
    setError('');
    setSaving(true);

    const cleanedContacts = guardianContacts.filter(
      (contact) => contact.name.trim() && contact.phoneNumber.trim(),
    );

    try {
      await updateGuardianContacts(cleanedContacts);
      setGuardianContacts(cleanedContacts);
      setStatus('Guardian contacts saved successfully.');
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to save guardian contacts.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">Protected area</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">Safety Dashboard</h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          Welcome, {user?.name}. Your account is authenticated and ready for map, tracking, and SOS features.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <article key={card.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft">
            <card.icon className="text-brand-700" size={26} aria-hidden="true" />
            <h2 className="mt-4 text-lg font-semibold text-slate-950">{card.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{card.text}</p>
          </article>
        ))}
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_320px]">
        <MapView location={location} status={locationStatus} />

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">Live coordinates</p>
              <h2 className="mt-2 text-xl font-bold text-slate-950">Current location</h2>
            </div>
            <span className="grid h-11 w-11 place-items-center rounded-md bg-brand-50 text-brand-700">
              <MapPinned size={22} aria-hidden="true" />
            </span>
          </div>

          <dl className="mt-6 space-y-4 text-sm">
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
              <dt className="font-medium text-slate-500">Status</dt>
              <dd className="font-semibold capitalize text-slate-900">{locationStatus}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
              <dt className="font-medium text-slate-500">Socket</dt>
              <dd className="font-semibold capitalize text-slate-900">{socketStatus}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
              <dt className="font-medium text-slate-500">Latitude</dt>
              <dd className="font-mono text-slate-900">{formatCoordinate(location?.latitude)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
              <dt className="font-medium text-slate-500">Longitude</dt>
              <dd className="font-mono text-slate-900">{formatCoordinate(location?.longitude)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
              <dt className="font-medium text-slate-500">Accuracy</dt>
              <dd className="font-semibold text-slate-900">{formatAccuracy(location?.accuracy)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt className="font-medium text-slate-500">Last update</dt>
              <dd className="font-semibold text-slate-900">{formatTimestamp(location?.timestamp)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-t border-slate-100 pt-3">
              <dt className="font-medium text-slate-500">Last shared</dt>
              <dd className="font-semibold text-slate-900">{formatTimestamp(lastSharedAt)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt className="font-medium text-slate-500">Online users</dt>
              <dd className="font-semibold text-slate-900">{connectedUsers.length}</dd>
            </div>
          </dl>

          {locationError ? (
            <p className="mt-5 rounded-md bg-amber-50 px-4 py-3 text-sm text-amber-700">{locationError}</p>
          ) : null}
          {socketError ? (
            <p className="mt-5 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{socketError}</p>
          ) : null}
          {socketId ? <p className="mt-4 truncate text-xs text-slate-400">Socket ID: {socketId}</p> : null}

          <button
            type="button"
            onClick={isTracking ? stopTracking : startTracking}
            className="mt-6 w-full rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            {isTracking ? 'Pause Tracking' : 'Start Tracking'}
          </button>
        </aside>
      </div>

      <form onSubmit={saveContacts} className="mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-soft">
        <GuardianContactsEditor contacts={guardianContacts} onChange={setGuardianContacts} />

        {status ? <p className="mt-5 rounded-md bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{status}</p> : null}
        {error ? <p className="mt-5 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}

        <button
          type="submit"
          disabled={saving}
          className="mt-6 rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {saving ? 'Saving contacts...' : 'Save Guardian Contacts'}
        </button>
      </form>
    </section>
  );
}

export default DashboardPage;
