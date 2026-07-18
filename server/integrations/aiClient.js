import axios from 'axios';
import { PYTHON_AI_URL, AI_TIMEOUT, MAX_RETRIES, logger } from '../config/index.js';

/**
 * Reusable Axios Client Instance for Python FastAPI AI Microservice.
 */
export const aiAxiosInstance = axios.create({
  baseURL: PYTHON_AI_URL || 'http://localhost:8000',
  timeout: AI_TIMEOUT || 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Client-Source': 'Express-Backend'
  }
});

// =====================================================
// REQUEST INTERCEPTOR
// =====================================================
aiAxiosInstance.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: Date.now() };
    const logMsg = `[AI Client Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`;
    if (logger && logger.info) {
      logger.info(logMsg);
    } else {
      console.log(logMsg);
    }
    return config;
  },
  (error) => {
    const errorMsg = `[AI Client Request Error] ${error.message}`;
    if (logger && logger.error) {
      logger.error(errorMsg);
    } else {
      console.error(errorMsg);
    }
    return Promise.reject(error);
  }
);

// =====================================================
// RESPONSE & ERROR RETRY INTERCEPTOR
// =====================================================
aiAxiosInstance.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config.metadata?.startTime || Date.now());
    const logMsg = `[AI Client Response] ${response.config.method?.toUpperCase()} ${response.config.url} status:${response.status} (${duration}ms)`;
    if (logger && logger.info) {
      logger.info(logMsg);
    } else {
      console.log(logMsg);
    }
    return response.data;
  },
  async (error) => {
    const config = error.config;
    if (!config) {
      return Promise.reject(error);
    }

    config._retryCount = config._retryCount || 0;
    const retryLimit = MAX_RETRIES || 3;

    // Retry conditions: Network errors, Timeouts, or HTTP 5xx Server Errors
    const isNetworkError = !error.response && error.code !== 'ERR_CANCELED';
    const isTimeout = error.code === 'ECONNABORTED';
    const isServerError = error.response && error.response.status >= 500;

    if (config._retryCount < retryLimit && (isNetworkError || isTimeout || isServerError)) {
      config._retryCount += 1;
      const backoffDelay = 1000 * config._retryCount;
      
      const retryWarnMsg = `[AI Client Retry] Connection issue (${error.message}). Retrying request (${config._retryCount}/${retryLimit}) in ${backoffDelay}ms...`;
      if (logger && logger.warn) {
        logger.warn(retryWarnMsg);
      } else {
        console.warn(retryWarnMsg);
      }

      await new Promise((resolve) => setTimeout(resolve, backoffDelay));
      return aiAxiosInstance(config);
    }

    const errorDetail = error.response ? JSON.stringify(error.response.data) : error.message;
    const finalErrorMsg = `[AI Client Error] Failed ${config.method?.toUpperCase()} ${config.url}: ${errorDetail}`;
    if (logger && logger.error) {
      logger.error(finalErrorMsg);
    } else {
      console.error(finalErrorMsg);
    }

    return Promise.reject(error);
  }
);

// =====================================================
// AI CLIENT HELPER CLASS
// =====================================================
export class AIClient {
  /**
   * Generic GET request helper.
   */
  static async get(endpoint, params = {}, config = {}) {
    try {
      return await aiAxiosInstance.get(endpoint, { params, ...config });
    } catch (error) {
      return this.handleFailure(error, `GET ${endpoint}`);
    }
  }

  /**
   * Generic POST request helper.
   */
  static async post(endpoint, data = {}, config = {}) {
    try {
      return await aiAxiosInstance.post(endpoint, data, config);
    } catch (error) {
      return this.handleFailure(error, `POST ${endpoint}`);
    }
  }

  /**
   * Health check method verifying AI microservice connectivity.
   */
  static async checkHealth() {
    try {
      const response = await aiAxiosInstance.get('/api/v1/health');
      return {
        status: 'healthy',
        data: response
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message || 'AI Service is unreachable'
      };
    }
  }

  /**
   * Graceful connection failure handler.
   */
  static handleFailure(error, context) {
    const message = error.response?.data?.message || error.message || 'AI Service Communication Error';
    const detail = error.response?.data?.error || null;
    
    return {
      success: false,
      message: `[AI Service Communication Error] ${context}: ${message}`,
      error: detail || error.message,
      status: error.response?.status || 503
    };
  }
}

export default AIClient;
