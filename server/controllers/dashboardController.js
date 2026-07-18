import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Get dashboard metrics summary
 * @route GET /api/v1/dashboard/summary
 */
export const getDashboardSummary = asyncHandler(async (req, res, next) => {
  res.ok({}, "Dashboard Summary API Working - Controller Active");
});
