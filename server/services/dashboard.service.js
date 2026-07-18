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
}

export default new DashboardService();
