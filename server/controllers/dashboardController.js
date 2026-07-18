import asyncHandler from '../utils/asyncHandler.js';
import dashboardService from '../services/dashboard.service.js';

/**
 * @desc Get dashboard metrics summary
 * @route GET /api/v1/dashboard/summary
 */
export const getDashboardSummary = asyncHandler(async (req, res, next) => {
  const summary = await dashboardService.getSummary();
  res.ok(summary, "Dashboard Summary API Working - Controller Active");
});
