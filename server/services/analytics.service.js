import repositoryFactory from '../repositories/repositoryFactory.js';

class AnalyticsService {
  constructor(analyticsRepository = null) {
    this.analyticsRepository = analyticsRepository;
  }

  get repository() {
    return this.analyticsRepository || repositoryFactory.getAnalyticsRepository();
  }

  async getPerformanceMetrics() {
    return this.repository.getPerformanceMetrics();
  }

  async getSentimentAnalysis() {
    return this.repository.getSentimentAnalysis();
  }
}

export default new AnalyticsService();
