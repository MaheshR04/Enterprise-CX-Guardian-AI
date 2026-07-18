/**
 * Wrapper utility to catch async resolution errors and forward them to Express error middlewares.
 */
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

export default asyncHandler;
