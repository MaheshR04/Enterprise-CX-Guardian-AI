import { useCallback, useEffect, useRef, useState } from 'react';

const GEOLOCATION_OPTIONS = {
  enableHighAccuracy: true,
  maximumAge: 5000,
  timeout: 15000,
};

function getErrorMessage(error) {
  if (error?.code === error?.PERMISSION_DENIED) {
    return 'Location permission was denied.';
  }

  if (error?.code === error?.POSITION_UNAVAILABLE) {
    return 'Current location is unavailable.';
  }

  if (error?.code === error?.TIMEOUT) {
    return 'Location request timed out.';
  }

  return 'Unable to read current location.';
}

export function useCurrentLocation({ autoStart = true } = {}) {
  const watchIdRef = useRef(null);
  const [isTracking, setIsTracking] = useState(false);
  const [location, setLocation] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');

  const stopTracking = useCallback(() => {
    if (watchIdRef.current !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }

    setIsTracking(false);
    setStatus((currentStatus) => (currentStatus === 'ready' ? 'idle' : currentStatus));
  }, []);

  const startTracking = useCallback(() => {
    if (!navigator.geolocation) {
      setStatus('unsupported');
      setError('Geolocation is not supported in this browser.');
      return;
    }

    if (watchIdRef.current !== null) {
      return;
    }

    setStatus('locating');
    setError('');

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          heading: position.coords.heading,
          speed: position.coords.speed,
          timestamp: position.timestamp,
        });
        setStatus('ready');
      },
      (positionError) => {
        if (watchIdRef.current !== null) {
          navigator.geolocation.clearWatch(watchIdRef.current);
          watchIdRef.current = null;
        }

        setIsTracking(false);
        setError(getErrorMessage(positionError));
        setStatus(positionError.code === positionError.PERMISSION_DENIED ? 'denied' : 'error');
      },
      GEOLOCATION_OPTIONS,
    );
    setIsTracking(true);
  }, []);

  useEffect(() => {
    let timerId;

    if (autoStart) {
      timerId = window.setTimeout(startTracking, 0);
    }

    return () => {
      window.clearTimeout(timerId);
      stopTracking();
    };
  }, [autoStart, startTracking, stopTracking]);

  return {
    error,
    isTracking,
    location,
    startTracking,
    status,
    stopTracking,
  };
}
