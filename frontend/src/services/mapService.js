export const DEFAULT_CENTER = [19.076, 72.8777];
export const DEFAULT_ZOOM = 12;
export const LOCATION_ZOOM = 16;
export const OPEN_STREET_MAP_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
export const OPEN_STREET_MAP_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

export function toLatLng(location) {
  if (!location) {
    return DEFAULT_CENTER;
  }

  return [location.latitude, location.longitude];
}

export function formatCoordinate(value) {
  if (typeof value !== 'number') {
    return 'Unavailable';
  }

  return value.toFixed(6);
}

export function formatAccuracy(value) {
  if (typeof value !== 'number') {
    return 'Unavailable';
  }

  return `${Math.round(value)} m`;
}

export function formatTimestamp(value) {
  if (!value) {
    return 'Waiting';
  }

  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(value));
}
