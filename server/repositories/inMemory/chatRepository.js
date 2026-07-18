import { ChatRepository } from '../interfaces.js';

class InMemoryChatRepository extends ChatRepository {
  async findHistory() {
    return [
      {
        id: 'msg_101',
        sender: 'user',
        text: 'Hello, I need help with my enterprise subscription refund.',
        timestamp: new Date(Date.now() - 600000).toISOString()
      },
      {
        id: 'msg_102',
        sender: 'ai_agent',
        text: 'Hello from AI Service! I can assist you with your refund inquiry.',
        timestamp: new Date(Date.now() - 580000).toISOString()
      }
    ];
  }
}

export default InMemoryChatRepository;
