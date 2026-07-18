import { AuthRepository } from '../interfaces.js';

class MongoAuthRepository extends AuthRepository {
  async login() {
    return {};
  }

  async register() {
    return {};
  }
}

export default MongoAuthRepository;
