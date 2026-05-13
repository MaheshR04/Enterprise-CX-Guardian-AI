export function notFoundHandler(req, _res, next) {
  const error = new Error(`Route not found: ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
}

export function errorHandler(error, _req, res, _next) {
  let statusCode = error.statusCode || 500;
  let message = error.message || 'Internal server error';

  if (error.code === 11000) {
    statusCode = 409;
    message = 'Duplicate value already exists';
  }

  res.status(statusCode).json({
    success: false,
    message,
  });
}
