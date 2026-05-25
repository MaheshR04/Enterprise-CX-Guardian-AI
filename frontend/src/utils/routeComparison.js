import { calculateRouteSafetyScore, getRiskLabel } from './safetyScoring.js';

export function compareRoutes(routes) {
  if (!routes.length) {
    return [];
  }

  const shortestDistance = Math.min(...routes.map((route) => route.distance));
  const fastestDuration = Math.min(...routes.map((route) => route.duration));

  return routes
    .map((route) => {
      const safetyScore = calculateRouteSafetyScore(route, shortestDistance, fastestDuration);

      return {
        ...route,
        safetyScore,
        riskLevel: getRiskLabel(safetyScore),
        isSafest: false,
      };
    })
    .sort((routeA, routeB) => routeB.safetyScore - routeA.safetyScore)
    .map((route, index) => ({
      ...route,
      rank: index + 1,
      isSafest: index === 0,
    }));
}

export function formatDistance(meters) {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }

  return `${(meters / 1000).toFixed(1)} km`;
}

export function formatDuration(seconds) {
  const minutes = Math.round(seconds / 60);

  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours} hr ${remainingMinutes} min`;
}
