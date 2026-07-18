import { logger } from '../config/index.js';
import ApiError from '../utils/ApiError.js';

/**
 * Centered error processing middleware yielding standardized Error responses.
 */
const errorHandler = (err, req, res, next) => {
  let statusCode = err.statusCode || err.status || 500;
  let message = 'Python AI Service unavailable';
  let errorDetail = err.message || 'Connection failure';

  // Handle specific connection & parse errors
  if (err.code === 'ECONNABORTED') {
    statusCode = 504; // Gateway Timeout
    message = 'Gateway Timeout';
    errorDetail = 'AI Microservice request timed out';
  } else if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') {
    statusCode = 503; // Service Unavailable
    message = 'Service Unavailable';
    errorDetail = 'Python AI Service is currently offline or connection was refused';
  } else if (err instanceof SyntaxError) {
    statusCode = 400; // Bad Request
    message = 'Bad Request';
    errorDetail = 'Invalid JSON payload structure';
  } else if (err instanceof ApiError || err.statusCode) {
    message = err.message || 'Operational Error';
    errorDetail = err.message || 'Request execution failed';
  } else if (err.name === 'ValidationError') {
    statusCode = 400;
    message = 'Validation Error';
    errorDetail = Object.values(err.errors).map(val => val.message).join(', ');
  } else if (err.name === 'CastError') {
    statusCode = 400;
    message = 'Cast Error';
    errorDetail = `Resource not found with id of ${err.value}`;
  }

  // Log error callstack using Winston logger
  if (logger && logger.error) {
    logger.error(`[Express Error] ${err.stack || err.message}`);
  }

  return res.status(statusCode).json({
    success: false,
    message,
    error: errorDetail
  });
};

export default errorHandler;
