import { CustomerRepository } from '../interfaces.js';

const customers = [];

class InMemoryCustomerRepository extends CustomerRepository {
  async findAll() {
    return [...customers];
  }

  async findById(id) {
    return customers.find((customer) => customer.id === id) || {};
  }
}

export default InMemoryCustomerRepository;
