import { AnalyticsRepository } from '../interfaces.js';

class InMemoryAnalyticsRepository extends AnalyticsRepository {
  async getPerformanceMetrics() {
    return {};
  }

  async getSentimentAnalysis() {
    return {};
  }
}

export default InMemoryAnalyticsRepository;
