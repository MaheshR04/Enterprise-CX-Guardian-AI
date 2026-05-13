import { useEffect, useState } from 'react';
import { healthCheck } from '../services/healthService.js';

export function useApiHealth() {
  const [status, setStatus] = useState({
    loading: true,
    online: false,
    message: 'Checking backend connection...',
  });

  useEffect(() => {
    let isMounted = true;

    async function checkApi() {
      try {
        const response = await healthCheck();

        if (isMounted) {
          setStatus({
            loading: false,
            online: true,
            message: response.message,
          });
        }
      } catch (error) {
        if (isMounted) {
          setStatus({
            loading: false,
            online: false,
            message: error?.message || 'Backend is unavailable',
          });
        }
      }
    }

    checkApi();

    return () => {
      isMounted = false;
    };
  }, []);

  return status;
}
