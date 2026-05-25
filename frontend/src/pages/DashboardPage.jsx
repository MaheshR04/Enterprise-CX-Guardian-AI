import { useState } from 'react';
import { LocateFixed, MapPinned, Navigation, RadioTower, Search, Siren } from 'lucide-react';
import GuardianContactsEditor from '../components/forms/GuardianContactsEditor.jsx';
import MapView from '../components/map/MapView.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { useCurrentLocation } from '../hooks/useCurrentLocation.js';
import { useLiveTracking } from '../hooks/useLiveTracking.js';
import { formatAccuracy, formatCoordinate, formatTimestamp } from '../services/mapService.js';
import { fetchRouteAlternatives, searchDestinations } from '../services/routeService.js';
import { compareRoutes, formatDistance, formatDuration } from '../utils/routeComparison.js';

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
    icon: Navigation,
    title: 'Safe route scoring',
    text: 'Route alternatives are ranked by safety, distance, ETA, and demo risk zones.',
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
  const [destinationQuery, setDestinationQuery] = useState('');
  const [destinationResults, setDestinationResults] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [selectedRouteId, setSelectedRouteId] = useState('');
  const [routeStatus, setRouteStatus] = useState('');
  const [routeError, setRouteError] = useState('');
  const [routeLoading, setRouteLoading] = useState(false);

  const safestRoute = routes.find((route) => route.isSafest);

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

  const handleDestinationSearch = async (event) => {
    event.preventDefault();
    setRouteError('');
    setRouteStatus('');
    setRouteLoading(true);

    try {
      const results = await searchDestinations(destinationQuery, location);
      setDestinationResults(results);
      setSelectedDestination(null);
      setRoutes([]);
      setSelectedRouteId('');

      if (results.length === 0) {
        setRouteError('No destination found. Try a more specific place name.');
      }
    } catch (requestError) {
      setRouteError(requestError.message || 'Destination search failed.');
    } finally {
      setRouteLoading(false);
    }
  };

  const selectDestination = (destination) => {
    setSelectedDestination(destination);
    setDestinationQuery(destination.label);
    setDestinationResults([]);
    setRoutes([]);
    setSelectedRouteId('');
    setRouteStatus('Destination selected. Generate safe routes when ready.');
  };

  const generateRoutes = async () => {
    setRouteError('');
    setRouteStatus('');

    if (!location) {
      setRouteError('Allow location access before generating routes.');
      return;
    }

    if (!selectedDestination) {
      setRouteError('Select a destination from search results first.');
      return;
    }

    setRouteLoading(true);

    try {
      const alternatives = await fetchRouteAlternatives(location, selectedDestination);
      const rankedRoutes = compareRoutes(alternatives);
      setRoutes(rankedRoutes);
      setSelectedRouteId(rankedRoutes[0]?.id || '');
      setRouteStatus(`${rankedRoutes.length} route option${rankedRoutes.length === 1 ? '' : 's'} generated.`);
    } catch (requestError) {
      setRouteError(requestError.message || 'Unable to generate routes.');
    } finally {
      setRouteLoading(false);
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

      <div className="mt-8 rounded-lg border border-slate-200 bg-white p-5 shadow-soft">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
          <form onSubmit={handleDestinationSearch} className="flex-1">
            <label htmlFor="destination" className="text-sm font-medium text-slate-700">
              Destination
            </label>
            <div className="mt-2 flex gap-3">
              <input
                id="destination"
                value={destinationQuery}
                onChange={(event) => setDestinationQuery(event.target.value)}
                placeholder="Search a place, landmark, or address"
                className="min-w-0 flex-1 rounded-md border border-slate-300 bg-white px-3 py-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-brand-600 focus:ring-4 focus:ring-brand-100"
                required
              />
              <button
                type="submit"
                disabled={routeLoading}
                className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-500 hover:text-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Search size={17} aria-hidden="true" />
                Search
              </button>
            </div>
          </form>

          <button
            type="button"
            onClick={generateRoutes}
            disabled={routeLoading || !selectedDestination}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Navigation size={17} aria-hidden="true" />
            Generate Safe Routes
          </button>
        </div>

        {destinationResults.length > 0 ? (
          <div className="mt-4 overflow-hidden rounded-md border border-slate-200">
            {destinationResults.map((destination) => (
              <button
                key={destination.id}
                type="button"
                onClick={() => selectDestination(destination)}
                className="block w-full border-b border-slate-100 px-4 py-3 text-left text-sm text-slate-700 transition last:border-b-0 hover:bg-brand-50 hover:text-brand-700"
              >
                {destination.label}
              </button>
            ))}
          </div>
        ) : null}

        {routeStatus ? <p className="mt-4 rounded-md bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{routeStatus}</p> : null}
        {routeError ? <p className="mt-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{routeError}</p> : null}
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_320px]">
        <MapView
          destination={selectedDestination}
          location={location}
          routes={routes}
          selectedRouteId={selectedRouteId}
          status={locationStatus}
        />

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

      {routes.length > 0 ? (
        <div className="mt-8 rounded-lg border border-slate-200 bg-white p-5 shadow-soft">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">Route comparison</p>
              <h2 className="mt-1 text-xl font-bold text-slate-950">
                Safest route score: {safestRoute?.safetyScore}
              </h2>
            </div>
            <p className="text-sm text-slate-500">Demo risk zones will be replaced by crime data in Step 6.</p>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {routes.map((route) => (
              <button
                key={route.id}
                type="button"
                onClick={() => setSelectedRouteId(route.id)}
                className={`rounded-lg border p-4 text-left transition ${
                  route.id === selectedRouteId
                    ? 'border-brand-500 bg-brand-50'
                    : 'border-slate-200 bg-white hover:border-brand-300'
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-slate-900">Option {route.rank}</span>
                  <span
                    className={`rounded-md px-2 py-1 text-xs font-bold ${
                      route.isSafest ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {route.isSafest ? 'Safest' : route.riskLevel}
                  </span>
                </div>
                <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <dt className="text-slate-500">Score</dt>
                    <dd className="mt-1 font-bold text-slate-950">{route.safetyScore}</dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">Distance</dt>
                    <dd className="mt-1 font-bold text-slate-950">{formatDistance(route.distance)}</dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">ETA</dt>
                    <dd className="mt-1 font-bold text-slate-950">{formatDuration(route.duration)}</dd>
                  </div>
                </dl>
              </button>
            ))}
          </div>
        </div>
      ) : null}

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
