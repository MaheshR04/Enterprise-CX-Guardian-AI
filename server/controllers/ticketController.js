import asyncHandler from '../utils/asyncHandler.js';
import ticketService from '../services/ticket.service.js';

/**
 * @desc Get all support tickets
 * @route GET /api/v1/tickets
 */
export const getTickets = asyncHandler(async (req, res, next) => {
  const tickets = await ticketService.getTickets();
  res.ok(tickets, "Tickets retrieved successfully");
});

/**
 * @desc Get single ticket
 * @route GET /api/v1/tickets/:id
 */
export const getTicketById = asyncHandler(async (req, res, next) => {
  const ticket = await ticketService.getTicketById(req.params.id);
  res.ok(ticket, "Ticket details retrieved successfully");
});

/**
 * @desc Create new ticket
 * @route POST /api/v1/tickets
 */
export const createTicket = asyncHandler(async (req, res, next) => {
  const newTicket = await ticketService.createTicket(req.body);
  res.created(newTicket, "Ticket created successfully");
});

/**
 * @desc Update support ticket
 * @route PUT /api/v1/tickets/:id
 */
export const updateTicket = asyncHandler(async (req, res, next) => {
  const ticket = await ticketService.updateTicket(req.params.id, req.body);
  res.ok(ticket, `Ticket ${req.params.id} updated successfully`);
});

/**
 * @desc Delete support ticket
 * @route DELETE /api/v1/tickets/:id
 */
export const deleteTicket = asyncHandler(async (req, res, next) => {
  const result = await ticketService.deleteTicket(req.params.id);
  res.ok(result, `Ticket ${req.params.id} deleted successfully`);
});
