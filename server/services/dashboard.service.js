import repositoryFactory from '../repositories/repositoryFactory.js';

class DashboardService {
  constructor(dashboardRepository = null) {
    this.dashboardRepository = dashboardRepository;
  }

  get repository() {
    return this.dashboardRepository || repositoryFactory.getDashboardRepository();
  }

  async getSummary() {
    return this.repository.getSummary();
  }

  async getSystemHealth() {
    return this.repository.getSystemHealth();
  }

  async getModelUsage() {
    return this.repository.getModelUsage();
  }

  async getConversationAnalytics() {
    return this.repository.getConversationAnalytics();
  }

  async getUserAnalytics() {
    return this.repository.getUserAnalytics();
  }

  async getDocumentAnalytics() {
    return this.repository.getDocumentAnalytics();
  }
}

export default new DashboardService();
