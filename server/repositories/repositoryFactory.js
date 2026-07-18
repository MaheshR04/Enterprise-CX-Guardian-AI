import { STORAGE_BACKEND } from '../config/index.js';

const supportedBackends = new Set(['memory', 'mongodb', 'redis', 'postgres', 'cosmos']);
const backendDirectories = {
  memory: 'inMemory',
  mongodb: 'mongodb',
  redis: 'redis',
  postgres: 'postgres',
  cosmos: 'cosmos',
};

const repositoryModules = {
  analytics: 'analyticsRepository',
  auth: 'authRepository',
  chat: 'chatRepository',
  customer: 'customerRepository',
  dashboard: 'dashboardRepository',
  ticket: 'ticketRepository',
};

class RepositoryFactory {
  constructor(storageBackend = STORAGE_BACKEND) {
    this.storageBackend = storageBackend.toLowerCase();
    this.repositories = null;
  }

  async initialize() {
    if (this.repositories) {
      return;
    }

    if (!supportedBackends.has(this.storageBackend)) {
      throw new Error(`Unsupported STORAGE_BACKEND "${this.storageBackend}".`);
    }

    const backendDirectory = backendDirectories[this.storageBackend];
    const repositories = {};

    for (const [repositoryName, moduleName] of Object.entries(repositoryModules)) {
      try {
        const module = await import(`./${backendDirectory}/${moduleName}.js`);
        repositories[repositoryName] = new module.default();
      } catch (error) {
        throw new Error(
          `Storage backend "${this.storageBackend}" is missing adapter "${backendDirectory}/${moduleName}.js".`
        );
      }
    }

    this.repositories = repositories;
  }

  getRepository(repositoryName) {
    if (!this.repositories) {
      throw new Error(
        'RepositoryFactory is not initialized. Call repositoryFactory.initialize() before loading routes.'
      );
    }

    return this.repositories[repositoryName];
  }

  getAnalyticsRepository() {
    return this.getRepository('analytics');
  }

  getAuthRepository() {
    return this.getRepository('auth');
  }

  getChatRepository() {
    return this.getRepository('chat');
  }

  getCustomerRepository() {
    return this.getRepository('customer');
  }

  getDashboardRepository() {
    return this.getRepository('dashboard');
  }

  getTicketRepository() {
    return this.getRepository('ticket');
  }
}

const repositoryFactory = new RepositoryFactory();

export default repositoryFactory;
