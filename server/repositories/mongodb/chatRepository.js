import { ChatRepository } from '../interfaces.js';
import MongoBaseRepository from './baseRepository.js';

class MongoChatRepository extends ChatRepository {
  constructor() {
    super();
    this.store = new MongoBaseRepository('chat_messages');
  }

  async findHistory() {
    return this.store.collection
      .find({}, { projection: { _id: 0 } })
      .sort({ timestamp: 1 })
      .toArray();
  }
}

export default MongoChatRepository;
