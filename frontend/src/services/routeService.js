const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org/search';
const OSRM_BASE_URL = 'https://router.project-osrm.org/route/v1/driving';

function formatPlaceName(place) {
  return place.display_name || [place.name, place.city, place.state, place.country].filter(Boolean).join(', ');
}

export async function searchDestinations(query, location) {
  const trimmedQuery = query.trim();

  if (trimmedQuery.length < 3) {
    return [];
  }

  const params = new URLSearchParams({
    q: trimmedQuery,
    format: 'jsonv2',
    limit: '5',
    addressdetails: '1',
  });

  if (location) {
    params.set(
      'viewbox',
      `${location.longitude - 0.4},${location.latitude + 0.4},${location.longitude + 0.4},${location.latitude - 0.4}`,
    );
    params.set('bounded', '0');
  }

  const response = await fetch(`${NOMINATIM_BASE_URL}?${params.toString()}`, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Destination search failed');
  }

  const places = await response.json();

  return places.map((place) => ({
    id: place.place_id,
    label: formatPlaceName(place),
    latitude: Number(place.lat),
    longitude: Number(place.lon),
  }));
}

export async function fetchRouteAlternatives(origin, destination) {
  if (!origin || !destination) {
    throw new Error('Origin and destination are required');
  }

  const coordinates = `${origin.longitude},${origin.latitude};${destination.longitude},${destination.latitude}`;
  const params = new URLSearchParams({
    alternatives: 'true',
    overview: 'full',
    geometries: 'geojson',
    steps: 'true',
  });

  const response = await fetch(`${OSRM_BASE_URL}/${coordinates}?${params.toString()}`);

  if (!response.ok) {
    throw new Error('Route generation failed');
  }

  const data = await response.json();

  if (data.code !== 'Ok' || !data.routes?.length) {
    throw new Error('No route found for this destination');
  }

  return data.routes.map((route, index) => ({
    id: `route-${index + 1}`,
    distance: route.distance,
    duration: route.duration,
    geometry: route.geometry.coordinates.map(([longitude, latitude]) => [latitude, longitude]),
    steps: route.legs?.flatMap((leg) => leg.steps || []) || [],
  }));
}
