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
    const logMsg = `[Outgoing Request to FastAPI] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`;
    if (logger && logger.info) {
      logger.info(logMsg);
    }
    return config;
  },
  (error) => {
    const errorMsg = `[Outgoing Request Error] ${error.message}`;
    if (logger && logger.error) {
      logger.error(errorMsg);
    }
    return Promise.reject(error);
  }
);

// =====================================================
// RESPONSE & ERROR RETRY INTERCEPTOR
// =====================================================
aiAxiosInstance.interceptors.response.use(
  (response) => {
    const durationMs = Date.now() - (response.config.metadata?.startTime || Date.now());
    const logMsg = `[Python Response] ${response.config.method?.toUpperCase()} ${response.config.url} status:${response.status} (${durationMs}ms)`;
    if (logger && logger.info) {
      logger.info(logMsg);
    }
    return response.data;
  },
  async (error) => {
    const config = error.config;
    if (!config) {
      if (logger && logger.error) {
        logger.error(`[Python Response Error] ${error.message}`);
      }
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
      
      const retryWarnMsg = `[Warning] [AI Client Retry] Connection issue (${error.message}). Retrying request (${config._retryCount}/${retryLimit}) in ${backoffDelay}ms...`;
      if (logger && logger.warn) {
        logger.warn(retryWarnMsg);
      }

      await new Promise((resolve) => setTimeout(resolve, backoffDelay));
      return aiAxiosInstance(config);
    }

    const errorDetail = error.response ? JSON.stringify(error.response.data) : error.message;
    const finalErrorMsg = `[Error] [Python AI Service Error] Failed ${config.method?.toUpperCase()} ${config.url}: ${errorDetail}`;
    if (logger && logger.error) {
      logger.error(finalErrorMsg);
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
        error: error.message || 'Python AI Service unavailable'
      };
    }
  }

  /**
   * Graceful connection failure handler returning meaningful HTTP statuses.
   * Node.js will NEVER crash if Python is unavailable.
   */
  static handleFailure(error, context) {
    let status = 503; // Service Unavailable default
    let message = 'Python AI Service unavailable';
    let detail = error.message || 'Connection failure';

    if (error.code === 'ECONNABORTED') {
      status = 504; // Gateway Timeout
      message = 'Python AI Service Timeout';
      detail = 'The request to the AI microservice timed out after 30 seconds.';
    } else if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      status = 503; // Service Unavailable
      message = 'Python AI Service Connection Refused';
      detail = 'Unable to establish network connection with the Python AI microservice.';
    } else if (error instanceof SyntaxError) {
      status = 400; // Bad Request
      message = 'Invalid JSON Response';
      detail = 'Received malformed JSON content from the AI microservice.';
    } else if (error.response) {
      status = error.response.status || 500;
      message = error.response.data?.message || 'Python AI Service Error';
      detail = error.response.data?.error || error.message;
    }

    if (logger && logger.error) {
      logger.error(`[Error] [AI Service Exception] ${context}: ${message} (${detail})`);
    }

    return {
      success: false,
      message,
      error: detail,
      status
    };
  }
}

export default AIClient;
