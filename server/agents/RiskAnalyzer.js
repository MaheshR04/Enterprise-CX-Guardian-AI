import { CRIME_ZONES } from '../config/crimeZones.js';

function toRadians(value) {
  return (value * Math.PI) / 180;
}

export function getDistanceMeters(pointA, pointB) {
  const earthRadiusMeters = 6371000;
  const latDistance = toRadians(pointB.latitude - pointA.latitude);
  const lonDistance = toRadians(pointB.longitude - pointA.longitude);
  const lat1 = toRadians(pointA.latitude);
  const lat2 = toRadians(pointB.latitude);

  const haversine =
    Math.sin(latDistance / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(lonDistance / 2) ** 2;

  return earthRadiusMeters * 2 * Math.atan2(Math.sqrt(haversine), Math.sqrt(1 - haversine));
}

export function calculateCrimeRisk(location) {
  if (!location?.latitude || !location?.longitude) {
    return { score: 0, nearbyZones: [] };
  }

  const nearbyZones = CRIME_ZONES.map((zone) => {
    const distanceMeters = getDistanceMeters(location, zone);
    const insideZone = distanceMeters <= zone.radiusMeters;
    const proximity = insideZone ? 1 - distanceMeters / zone.radiusMeters : 0;
    return {
      ...zone,
      distanceMeters,
      insideZone,
      proximity,
      riskContribution: Math.round(zone.weight * proximity),
    };
  })
    .filter((z) => z.insideZone)
    .sort((a, b) => b.riskContribution - a.riskContribution);

  const score = Math.min(
    100,
    nearbyZones.reduce((total, z) => total + z.riskContribution, 0),
  );

  return {
    score,
    nearbyZones,
  };
}

export function calculateBatteryRisk(battery) {
  const level = battery?.level;
  const charging = battery?.charging;

  if (typeof level !== 'number' || charging === true) {
    return 0;
  }

  // Level is represented as 0 to 1 (e.g. 0.8 = 80%) or 0 to 100
  // Standardize to 0 - 100
  const normalizedLevel = level <= 1 ? level * 100 : level;

  if (normalizedLevel < 15) return 80;
  if (normalizedLevel < 30) return 40;
  if (normalizedLevel < 50) return 20;
  return 0;
}

export function calculateTemporalRisk() {
  const currentHour = new Date().getHours();
  // Late night (10 PM to 5 AM)
  if (currentHour >= 22 || currentHour < 5) return 30;
  // Late evening (8 PM to 10 PM)
  if (currentHour >= 20 && currentHour < 22) return 15;
  return 0;
}

export function calculateDeviationRisk(location, activeRoute) {
  if (!location || !activeRoute || !activeRoute.geometry?.length) {
    return 0;
  }

  // Find the closest point in the route geometry
  let minDistance = Number.POSITIVE_INFINITY;
  
  for (const point of activeRoute.geometry) {
    // route geometries are usually stored as [latitude, longitude] or [longitude, latitude]
    // Let's assume standard [latitude, longitude] as mapped in mapService
    const routePt = { latitude: point[0], longitude: point[1] };
    const dist = getDistanceMeters(location, routePt);
    if (dist < minDistance) {
      minDistance = dist;
    }
  }

  // If user is more than 120 meters off the active route, flag deviation
  if (minDistance > 120) {
    return 50; // Moderate high deviation risk score
  }

  return 0;
}

export function analyzeAllRisks(memory) {
  const latestLocation = memory.locationHistory[memory.locationHistory.length - 1];
  const battery = memory.battery;
  const activeRoute = memory.activeRoute;

  const crimeRisk = calculateCrimeRisk(latestLocation);
  const batteryRisk = calculateBatteryRisk(battery);
  const temporalRisk = calculateTemporalRisk();
  const deviationRisk = calculateDeviationRisk(latestLocation, activeRoute);

  return {
    crime: crimeRisk,
    battery: batteryRisk,
    temporal: temporalRisk,
    deviation: deviationRisk,
    timestamp: new Date(),
  };
}
