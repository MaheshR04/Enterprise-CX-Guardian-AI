import { CRIME_ZONES } from '../data/crimeZones.js';
import { getDistanceMeters } from './safetyScoring.js';

const RISK_LEVEL_ORDER = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4,
};

function getLevelFromScore(score) {
  if (score >= 75) return 'CRITICAL';
  if (score >= 52) return 'HIGH';
  if (score >= 26) return 'MEDIUM';
  return 'LOW';
}

function getHighestLevel(zones) {
  return zones.reduce((highest, zone) => {
    if (RISK_LEVEL_ORDER[zone.level] > RISK_LEVEL_ORDER[highest]) {
      return zone.level;
    }

    return highest;
  }, 'LOW');
}

export function analyzeCrimeRisk(location, zones = CRIME_ZONES) {
  if (!location) {
    return {
      nearbyZones: [],
      riskLevel: 'LOW',
      riskScore: 0,
      shouldAlert: false,
    };
  }

  const nearbyZones = zones
    .map((zone) => {
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
    .filter((zone) => zone.insideZone)
    .sort((zoneA, zoneB) => zoneB.riskContribution - zoneA.riskContribution);

  const proximityScore = nearbyZones.reduce((total, zone) => total + zone.riskContribution, 0);
  const highestZoneLevel = getHighestLevel(nearbyZones);
  const calculatedLevel = getLevelFromScore(proximityScore);
  const riskLevel =
    RISK_LEVEL_ORDER[highestZoneLevel] > RISK_LEVEL_ORDER[calculatedLevel] ? highestZoneLevel : calculatedLevel;

  return {
    nearbyZones,
    riskLevel,
    riskScore: Math.min(100, proximityScore),
    shouldAlert: riskLevel === 'HIGH' || riskLevel === 'CRITICAL',
  };
}

export function getRiskToneClass(level) {
  if (level === 'CRITICAL') return 'bg-red-600 text-white';
  if (level === 'HIGH') return 'bg-red-50 text-red-700';
  if (level === 'MEDIUM') return 'bg-amber-50 text-amber-700';
  return 'bg-emerald-50 text-emerald-700';
}
