import { body } from 'express-validator';
import validateFields from './validateFields.js';

/**
 * Validation rules for POST /api/v1/chat request body.
 * Required: message (non-empty string)
 * Optional: conversationId / conversation_id (string)
 * Optional: customerId / customer_id (string)
 */
export const validateChatMessage = [
  body('message')
    .exists({ checkNull: true, checkFalsy: true })
    .withMessage('Message content is required')
    .isString()
    .withMessage('Message must be a string')
    .trim()
    .notEmpty()
    .withMessage('Message content cannot be empty'),

  body(['conversationId', 'conversation_id'])
    .optional()
    .isString()
    .withMessage('Conversation ID must be a string'),

  body(['customerId', 'customer_id'])
    .optional()
    .isString()
    .withMessage('Customer ID must be a string'),

  validateFields
];

export default validateChatMessage;
