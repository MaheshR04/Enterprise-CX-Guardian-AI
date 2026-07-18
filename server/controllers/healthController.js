import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Get system health state
 * @route GET /api/v1/health
 */
export const getHealth = asyncHandler(async (req, res, next) => {
  res.status(200).json({
    status: "healthy",
    server: "Enterprise CX Guardian AI",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    uptime: `${Math.floor(process.uptime())}s`
  });
});
