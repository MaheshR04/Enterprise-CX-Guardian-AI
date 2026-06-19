import { useEffect, useRef, useState } from 'react';
import { disconnectSocket, getSocket } from '../sockets/socketClient.js';

const LOCATION_EMIT_INTERVAL_MS = 5000;

export function useLiveTracking({ enabled, location, token }) {
  const latestLocationRef = useRef(location);
  const [socketStatus, setSocketStatus] = useState('idle');
  const [socketId, setSocketId] = useState('');
  const [lastSharedAt, setLastSharedAt] = useState(null);
  const [connectedUsers, setConnectedUsers] = useState([]);
  const [socketError, setSocketError] = useState('');

  useEffect(() => {
    latestLocationRef.current = location;
  }, [location]);

  useEffect(() => {
    if (!enabled || !token) {
      disconnectSocket();
      const resetTimer = window.setTimeout(() => {
        setSocketStatus('idle');
        setSocketId('');
      }, 0);
      return () => window.clearTimeout(resetTimer);
    }

    const socket = getSocket(token);

    const handleConnect = () => {
      setSocketStatus('connected');
      setSocketId(socket.id);
      setSocketError('');
    };

    const handleDisconnect = () => {
      setSocketStatus('disconnected');
      setSocketId('');
    };

    const handleConnectError = (error) => {
      setSocketStatus('error');
      setSocketError(error.message || 'Realtime connection failed');
    };

    const handleUserConnected = (payload) => {
      setConnectedUsers(payload.connectedUsers || []);
    };

    const handleConnectedUsers = (payload) => {
      setConnectedUsers(payload || []);
    };

    const handleAgentAdvisory = (payload) => {
      window.dispatchEvent(new CustomEvent('agent-advisory', { detail: payload }));
    };

    const handleAgentEscalation = (payload) => {
      window.dispatchEvent(new CustomEvent('agent-escalation', { detail: payload }));
    };

    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleConnectError);
    socket.on('user-connected', handleUserConnected);
    socket.on('connected-users', handleConnectedUsers);
    socket.on('agent-advisory', handleAgentAdvisory);
    socket.on('agent-escalation', handleAgentEscalation);

    const connectTimer = window.setTimeout(() => {
      setSocketStatus(socket.connected ? 'connected' : 'connecting');
    }, 0);
    socket.connect();

    return () => {
      window.clearTimeout(connectTimer);
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleConnectError);
      socket.off('user-connected', handleUserConnected);
      socket.off('connected-users', handleConnectedUsers);
      socket.off('agent-advisory', handleAgentAdvisory);
      socket.off('agent-escalation', handleAgentEscalation);
      disconnectSocket();
    };
  }, [enabled, token]);

  useEffect(() => {
    if (!enabled || !token) {
      return undefined;
    }

    const intervalId = window.setInterval(async () => {
      const socket = getSocket(token);
      const currentLocation = latestLocationRef.current;

      if (!socket.connected || !currentLocation) {
        return;
      }

      let battery = null;
      try {
        if (navigator.getBattery) {
          const batteryStatus = await navigator.getBattery();
          battery = {
            level: batteryStatus.level,
            charging: batteryStatus.charging,
          };
        }
      } catch (err) {
        console.error('Error fetching battery state:', err);
      }

      const payload = {
        location: currentLocation,
        battery,
        activeRoute: null,
      };

      socket.emit('location-update', payload, (response) => {
        if (response?.success) {
          setLastSharedAt(Date.now());
          setSocketError('');
        } else if (response?.message) {
          setSocketError(response.message);
        }
      });
    }, LOCATION_EMIT_INTERVAL_MS);

    return () => window.clearInterval(intervalId);

  }, [enabled, token]);

  return {
    connectedUsers,
    lastSharedAt,
    socketError,
    socketId,
    socketStatus,
  };
}
