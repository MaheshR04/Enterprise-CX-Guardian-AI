import asyncHandler from '../utils/asyncHandler.js';
import ApiError from '../utils/ApiError.js';

// Mock tickets cache data
const mockTickets = [
  { id: 'CX-4912', customer: 'Microsoft (Enterprise)', subject: 'Seat refund request accidental purchase', priority: 'High', status: 'Resolved' },
  { id: 'CX-4911', customer: 'Stripe API', subject: 'DNS key reset lockout validation', priority: 'High', status: 'Resolved' },
];

/**
 * @desc Get all support tickets
 * @route GET /api/v1/tickets
 */
export const getTickets = asyncHandler(async (req, res, next) => {
  res.ok(mockTickets, "Tickets retrieved successfully");
});

/**
 * @desc Get single ticket
 * @route GET /api/v1/tickets/:id
 */
export const getTicketById = asyncHandler(async (req, res, next) => {
  const ticket = mockTickets.find(t => t.id === req.params.id);
  if (!ticket) {
    throw new ApiError(404, `Ticket not found with id of ${req.params.id}`);
  }
  res.ok(ticket, "Ticket details retrieved successfully");
});

/**
 * @desc Create new ticket
 * @route POST /api/v1/tickets
 */
export const createTicket = asyncHandler(async (req, res, next) => {
  const newTicket = {
    id: `CX-${Math.floor(Math.random() * 9000) + 1000}`,
    customer: req.body.customer || 'Unknown Customer',
    subject: req.body.subject || 'Default Subject',
    priority: req.body.priority || 'Medium',
    status: 'Open'
  };

  res.created(newTicket, "Ticket created successfully");
});

/**
 * @desc Update support ticket
 * @route PUT /api/v1/tickets/:id
 */
export const updateTicket = asyncHandler(async (req, res, next) => {
  res.ok({}, `Ticket ${req.params.id} updated successfully`);
});

/**
 * @desc Delete support ticket
 * @route DELETE /api/v1/tickets/:id
 */
export const deleteTicket = asyncHandler(async (req, res, next) => {
  res.ok({}, `Ticket ${req.params.id} deleted successfully`);
});
