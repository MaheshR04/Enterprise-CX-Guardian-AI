import repositoryFactory from '../repositories/repositoryFactory.js';
import aiService from './ai.service.js';

class ChatService {
  constructor(chatRepository = null) {
    this.chatRepository = chatRepository;
  }

  get repository() {
    return this.chatRepository || repositoryFactory.getChatRepository();
  }

  async sendMessage(payload) {
    return aiService.chat(payload);
  }

  async getHealth() {
    return aiService.health();
  }

  async getHistory() {
    return this.repository.findHistory();
  }
}

export default new ChatService();
