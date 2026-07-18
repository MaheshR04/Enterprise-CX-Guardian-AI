import asyncHandler from '../utils/asyncHandler.js';
import healthService from '../services/health.service.js';

/**
 * @desc Get system health state (Node backend + Python AI service)
 * @route GET /api/v1/health
 */
export const getHealth = asyncHandler(async (req, res, next) => {
  const healthData = await healthService.getSystemHealth();
  
  if (res.ok) {
    return res.ok(healthData, 'System health retrieved successfully');
  }

  return res.status(200).json({
    success: true,
    message: 'System health retrieved successfully',
    data: healthData,
    errors: null
  });
});
