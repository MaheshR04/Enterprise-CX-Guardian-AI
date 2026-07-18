import { AuthRepository } from '../interfaces.js';

class InMemoryAuthRepository extends AuthRepository {
  async login() {
    return {};
  }

  async register() {
    return {};
  }
}

export default InMemoryAuthRepository;
