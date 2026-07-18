import axios from 'axios';
import { PYTHON_AI_URL } from '../config/index.js';

/**
 * Configure Axios Client instance for communicating with PYTHON_AI_URL service.
 */
export const aiClient = axios.create({
  baseURL: PYTHON_AI_URL,
  timeout: 5000, // 5 seconds timeout limit
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Axios Response Interceptor to execute retries on connection timeout/errors
aiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config: originalConfig } = error;
    if (!originalConfig) {
      return Promise.reject(error);
    }

    // Set default retry counter
    originalConfig._retryCount = originalConfig._retryCount || 0;
    const maxRetries = 3;

    // Retry only on timeouts or network connection failures
    const isNetworkError = !error.response && error.code !== 'ERR_CANCELED';
    const isTimeout = error.code === 'ECONNABORTED';

    if (originalConfig._retryCount < maxRetries && (isNetworkError || isTimeout)) {
      originalConfig._retryCount += 1;
      
      const delay = 1000 * originalConfig._retryCount;
      console.warn(`[AI Client] Connection issue: ${error.message}. Retrying request (${originalConfig._retryCount}/${maxRetries}) in ${delay}ms...`);
      
      // Delay before retrying (exponential backoff)
      await new Promise((resolve) => setTimeout(resolve, delay));
      return aiClient(originalConfig);
    }

    return Promise.reject(error);
  }
);

/**
 * Verifies if the FastAPI AI microservice is responsive.
 */
export const checkAiServiceHealth = async () => {
  try {
    const response = await aiClient.get('/');
    return {
      status: 'healthy',
      details: response.data
    };
  } catch (error) {
    console.error(`[AI Client Health Check] Offline: ${error.message}`);
    return {
      status: 'offline',
      error: error.message
    };
  }
};
