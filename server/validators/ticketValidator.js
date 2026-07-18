import { body } from 'express-validator';
import validateFields from './validateFields.js';
import { constants } from '../config/index.js';

const priorities = Object.values(constants.TICKET_PRIORITY);

/**
 * Reusable ticket validation schema rules template.
 */
export const validateTicket = [
  body('customer')
    .notEmpty()
    .withMessage('Customer association is required')
    .isString()
    .withMessage('Customer name must be a string value'),

  body('subject')
    .notEmpty()
    .withMessage('Ticket subject is required')
    .isLength({ min: 5 })
    .withMessage('Subject must be at least 5 characters long'),

  body('priority')
    .optional()
    .isIn(priorities)
    .withMessage(`Priority must be one of: ${priorities.join(', ')}`),

  validateFields
];
