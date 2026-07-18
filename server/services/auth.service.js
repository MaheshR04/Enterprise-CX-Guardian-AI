import repositoryFactory from '../repositories/repositoryFactory.js';

class AuthService {
  constructor(authRepository = null) {
    this.authRepository = authRepository;
  }

  get repository() {
    return this.authRepository || repositoryFactory.getAuthRepository();
  }

  async login(credentials) {
    return this.repository.login(credentials);
  }

  async register(userDetails) {
    return this.repository.register(userDetails);
  }
}

export default new AuthService();
