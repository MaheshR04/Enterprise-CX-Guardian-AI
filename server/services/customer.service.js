import repositoryFactory from '../repositories/repositoryFactory.js';

class CustomerService {
  constructor(customerRepository = null) {
    this.customerRepository = customerRepository;
  }

  get repository() {
    return this.customerRepository || repositoryFactory.getCustomerRepository();
  }

  async getCustomers() {
    return this.repository.findAll();
  }

  async getCustomerById(id) {
    return this.repository.findById(id);
  }
}

export default new CustomerService();
