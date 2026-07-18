import { DashboardRepository } from '../interfaces.js';

class MongoDashboardRepository extends DashboardRepository {
  async getSummary() {
    return {};
  }
}

export default MongoDashboardRepository;
