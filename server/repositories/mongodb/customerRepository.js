import { CustomerRepository } from '../interfaces.js';
import MongoBaseRepository from './baseRepository.js';

class MongoCustomerRepository extends CustomerRepository {
  constructor() {
    super();
    this.store = new MongoBaseRepository('customers');
  }

  async findAll() {
    const customers = await this.store.collection.find({}, { projection: { _id: 0 } }).toArray();
    return customers;
  }

  async findById(id) {
    const customer = await this.store.collection.findOne({ id }, { projection: { _id: 0 } });
    return customer || {};
  }
}

export default MongoCustomerRepository;
