import { TicketRepository } from '../interfaces.js';
import MongoBaseRepository from './baseRepository.js';

class MongoTicketRepository extends TicketRepository {
  constructor() {
    super();
    this.store = new MongoBaseRepository('tickets');
  }

  async findAll() {
    return this.store.collection.find({}, { projection: { _id: 0 } }).toArray();
  }

  async findById(id) {
    const ticket = await this.store.collection.findOne({ id }, { projection: { _id: 0 } });
    return ticket || null;
  }

  async create(ticket) {
    await this.store.collection.insertOne({ ...ticket });
    return { ...ticket };
  }

  async updateById(id, updates) {
    const result = await this.store.collection.findOneAndUpdate(
      { id },
      { $set: { ...updates, id } },
      { projection: { _id: 0 }, returnDocument: 'after' }
    );

    return this.store.withoutMongoId(result);
  }

  async deleteById(id) {
    const result = await this.store.collection.deleteOne({ id });
    return result.deletedCount > 0;
  }
}

export default MongoTicketRepository;
