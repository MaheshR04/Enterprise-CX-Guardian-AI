class RepositoryInterface {
  notImplemented(methodName) {
    throw new Error(`${this.constructor.name}.${methodName} must be implemented by a storage adapter.`);
  }
}

export class AuthRepository extends RepositoryInterface {
  async login() {
    this.notImplemented('login');
  }

  async register() {
    this.notImplemented('register');
  }
}

export class CustomerRepository extends RepositoryInterface {
  async findAll() {
    this.notImplemented('findAll');
  }

  async findById() {
    this.notImplemented('findById');
  }
}

export class TicketRepository extends RepositoryInterface {
  async findAll() {
    this.notImplemented('findAll');
  }

  async findById() {
    this.notImplemented('findById');
  }

  async create() {
    this.notImplemented('create');
  }

  async updateById() {
    this.notImplemented('updateById');
  }

  async deleteById() {
    this.notImplemented('deleteById');
  }
}

export class ChatRepository extends RepositoryInterface {
  async findHistory() {
    this.notImplemented('findHistory');
  }
}

export class AnalyticsRepository extends RepositoryInterface {
  async getPerformanceMetrics() {
    this.notImplemented('getPerformanceMetrics');
  }

  async getSentimentAnalysis() {
    this.notImplemented('getSentimentAnalysis');
  }
}

export class DashboardRepository extends RepositoryInterface {
  async getSummary() {
    this.notImplemented('getSummary');
  }
}
