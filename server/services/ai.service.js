import { AIClient } from '../integrations/aiClient.js';

/**
 * AI Service Manager.
 * Wraps and delegates calls from the Node.js backend to the Python FastAPI microservice.
 * All requests pass exclusively through AIClient.
 */
class AIService {
  /**
   * Delegates chat interaction messages to the Python AI service.
   * @param {Object} payload - Message payload ({ message, conversation_id, customer_id })
   */
  async chat(payload = {}) {
    return await AIClient.post('/api/v1/chat', payload);
  }

  /**
   * Delegates health check query to the Python AI service.
   */
  async health() {
    return await AIClient.checkHealth();
  }

  /**
   * Pings the Python AI service health endpoint.
   */
  async ping() {
    return await AIClient.get('/api/v1/health');
  }

  // =====================================================
  // FUTURE PLACEHOLDER METHODS
  // =====================================================

  /**
   * Placeholder method for sentiment analysis.
   * @param {Object} payload - Sentiment analysis input text
   */
  async analyzeSentiment(payload = {}) {
    // Placeholder stub - delegating to /api/v1/sentiment endpoint
    return await AIClient.post('/api/v1/sentiment', payload);
  }

  /**
   * Placeholder method for root-cause reasoning.
   * @param {Object} payload - Issue description and ticket context
   */
  async reason(payload = {}) {
    // Placeholder stub - delegating to /api/v1/reasoning endpoint
    return await AIClient.post('/api/v1/reasoning', payload);
  }

  /**
   * Placeholder method for next-best-action recommendations.
   * @param {Object} payload - Customer tier and ticket history
   */
  async recommend(payload = {}) {
    // Placeholder stub - delegating to /api/v1/recommendation endpoint
    return await AIClient.post('/api/v1/recommendation', payload);
  }

  /**
   * Placeholder method for customer intent detection.
   * @param {Object} payload - Customer message text
   */
  async detectIntent(payload = {}) {
    // Placeholder stub - delegating to /api/v1/analyze endpoint
    return await AIClient.post('/api/v1/analyze', payload);
  }
}

const aiServiceInstance = new AIService();
export default aiServiceInstance;
