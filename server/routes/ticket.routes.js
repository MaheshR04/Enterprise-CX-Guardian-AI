import express from 'express';
import * as ticketController from '../controllers/ticketController.js';
import { validateTicket } from '../validators/ticketValidator.js';

const router = express.Router();

router.route('/')
  .get(ticketController.getTickets)
  .post(validateTicket, ticketController.createTicket);

router.route('/:id')
  .get(ticketController.getTicketById)
  .put(ticketController.updateTicket)
  .delete(ticketController.deleteTicket);

export default router;
