import { useEffect, useRef } from 'react';
import { getSocket } from '../sockets/socketClient.js';
import { playDangerAlarm } from '../utils/alarmSound.js';

export function useDangerAlertSocket({ assessment, enabled, location, token }) {
  const lastAlertKeyRef = useRef('');

  useEffect(() => {
    if (!enabled || !token || !location || !assessment?.shouldAlert) {
      return;
    }

    const primaryZone = assessment.nearbyZones[0];
    const alertKey = `${assessment.riskLevel}:${primaryZone?.id || 'unknown'}`;

    if (lastAlertKeyRef.current === alertKey) {
      return;
    }

    lastAlertKeyRef.current = alertKey;
    playDangerAlarm();

    const socket = getSocket(token);

    if (!socket.connected) {
      return;
    }

    socket.emit('danger-alert', {
      location,
      riskLevel: assessment.riskLevel,
      riskScore: assessment.riskScore,
      zone: primaryZone
        ? {
            id: primaryZone.id,
            label: primaryZone.label,
            category: primaryZone.category,
            distanceMeters: Math.round(primaryZone.distanceMeters),
          }
        : null,
    });
  }, [assessment, enabled, location, token]);
}
