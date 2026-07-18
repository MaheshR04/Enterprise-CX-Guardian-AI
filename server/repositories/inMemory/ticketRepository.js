import { TicketRepository } from '../interfaces.js';

const tickets = [
  { id: 'CX-4912', customer: 'Microsoft (Enterprise)', subject: 'Seat refund request accidental purchase', priority: 'High', status: 'Resolved' },
  { id: 'CX-4911', customer: 'Stripe API', subject: 'DNS key reset lockout validation', priority: 'High', status: 'Resolved' },
];

class InMemoryTicketRepository extends TicketRepository {
  async findAll() {
    return tickets.map((ticket) => ({ ...ticket }));
  }

  async findById(id) {
    const ticket = tickets.find((item) => item.id === id);
    return ticket ? { ...ticket } : null;
  }

  async create(ticket) {
    tickets.push({ ...ticket });
    return { ...ticket };
  }

  async updateById(id, updates) {
    const index = tickets.findIndex((ticket) => ticket.id === id);

    if (index === -1) {
      return null;
    }

    tickets[index] = {
      ...tickets[index],
      ...updates,
      id,
    };

    return { ...tickets[index] };
  }

  async deleteById(id) {
    const index = tickets.findIndex((ticket) => ticket.id === id);

    if (index === -1) {
      return false;
    }

    tickets.splice(index, 1);
    return true;
  }
}

export default InMemoryTicketRepository;
