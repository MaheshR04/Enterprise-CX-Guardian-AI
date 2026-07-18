/**
 * Middleware to intercept unmatched HTTP requests and forward a 404 Not Found error.
 */
const notFound = (req, res, next) => {
  const error = new Error(`Not Found - ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
};

export default notFound;
