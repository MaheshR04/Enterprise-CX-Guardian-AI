import { CRIME_ZONES } from '../data/crimeZones.js';

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

function getRouteRiskPenalty(route) {
  return CRIME_ZONES.reduce((totalPenalty, zone) => {
    const closestDistance = route.geometry.reduce((closest, [latitude, longitude]) => {
      const distance = getDistanceMeters({ latitude, longitude }, zone);
      return Math.min(closest, distance);
    }, Number.POSITIVE_INFINITY);

    if (closestDistance > zone.radiusMeters) {
      return totalPenalty;
    }

    const proximityRatio = 1 - closestDistance / zone.radiusMeters;
    return totalPenalty + zone.weight * proximityRatio;
  }, 0);
}

function getNamedRoadRatio(route) {
  if (!route.steps.length) {
    return 0.5;
  }

  const namedSteps = route.steps.filter((step) => step.name?.trim()).length;
  return namedSteps / route.steps.length;
}

export function calculateRouteSafetyScore(route, shortestDistance, fastestDuration) {
  const riskPenalty = getRouteRiskPenalty(route);
  const distancePenalty = shortestDistance > 0 ? ((route.distance - shortestDistance) / shortestDistance) * 12 : 0;
  const durationPenalty = fastestDuration > 0 ? ((route.duration - fastestDuration) / fastestDuration) * 10 : 0;
  const namedRoadBonus = getNamedRoadRatio(route) * 8;
  const score = 100 - riskPenalty - distancePenalty - durationPenalty + namedRoadBonus;

  return Math.max(0, Math.min(100, Math.round(score)));
}

export function getRiskLabel(score) {
  if (score >= 85) return 'LOW';
  if (score >= 70) return 'MEDIUM';
  if (score >= 55) return 'HIGH';
  return 'CRITICAL';
}

export function getDemoRiskZones() {
  return CRIME_ZONES;
}
