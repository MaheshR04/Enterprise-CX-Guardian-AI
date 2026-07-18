import repositoryFactory from '../repositories/repositoryFactory.js';
import ApiError from '../utils/ApiError.js';

class TicketService {
  constructor(ticketRepository = null) {
    this.ticketRepository = ticketRepository;
  }

  get repository() {
    return this.ticketRepository || repositoryFactory.getTicketRepository();
  }

  async getTickets() {
    return this.repository.findAll();
  }

  async getTicketById(id) {
    const ticket = await this.repository.findById(id);

    if (!ticket) {
      throw new ApiError(404, `Ticket not found with id of ${id}`);
    }

    return ticket;
  }

  async createTicket(payload) {
    const newTicket = {
      id: `CX-${Math.floor(Math.random() * 9000) + 1000}`,
      customer: payload.customer || 'Unknown Customer',
      subject: payload.subject || 'Default Subject',
      priority: payload.priority || 'Medium',
      status: 'Open'
    };

    return this.repository.create(newTicket);
  }

  async updateTicket(id, payload) {
    const ticket = await this.repository.updateById(id, payload);

    if (!ticket) {
      throw new ApiError(404, `Ticket not found with id of ${id}`);
    }

    return ticket;
  }

  async deleteTicket(id) {
    const deleted = await this.repository.deleteById(id);

    if (!deleted) {
      throw new ApiError(404, `Ticket not found with id of ${id}`);
    }

    return {};
  }
}

export default new TicketService();
