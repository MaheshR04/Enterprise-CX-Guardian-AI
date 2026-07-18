import { DashboardRepository } from '../interfaces.js';

class InMemoryDashboardRepository extends DashboardRepository {
  async getSummary() {
    return {};
  }
}

export default InMemoryDashboardRepository;
