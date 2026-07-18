import { logger, NODE_ENV } from '../config/index.js';
import ApiError from '../utils/ApiError.js';

/**
 * Centered error processing middleware yielding standardized Error responses.
 */
const errorHandler = (err, req, res, next) => {
  let statusCode = err.statusCode || 500;
  let message = 'Internal Server Error';
  let errorDetail = err.message || 'Something went wrong';

  // Log error callstack using Winston logger
  logger.error(`[Express Error] ${err.stack || err.message}`);

  // Handle ApiError/Operational Errors
  if (err instanceof ApiError || err.statusCode) {
    message = 'Operational Error';
    errorDetail = err.message;
  }

  // Handle Mongoose validation errors
  if (err.name === 'ValidationError') {
    statusCode = 400;
    message = 'Validation Error';
    errorDetail = Object.values(err.errors).map(val => val.message).join(', ');
  }
  
  // Handle Mongoose cast errors
  if (err.name === 'CastError') {
    statusCode = 400;
    message = 'Cast Error';
    errorDetail = `Resource not found with id of ${err.value}`;
  }

  res.status(statusCode).json({
    success: false,
    message,
    error: errorDetail,
    stack: NODE_ENV === 'development' ? err.stack : undefined
  });
};

export default errorHandler;
