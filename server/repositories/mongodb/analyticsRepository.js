import { AnalyticsRepository } from '../interfaces.js';

class MongoAnalyticsRepository extends AnalyticsRepository {
  async getPerformanceMetrics() {
    return {};
  }

  async getSentimentAnalysis() {
    return {};
  }
}

export default MongoAnalyticsRepository;
