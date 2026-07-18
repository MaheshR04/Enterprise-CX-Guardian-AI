import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Get analytics performance metrics
 * @route GET /api/v1/analytics/performance
 */
export const getPerformanceMetrics = asyncHandler(async (req, res, next) => {
  res.ok({}, "Analytics Performance API Working - Controller Active");
});

/**
 * @desc Get customer sentiment distributions
 * @route GET /api/v1/analytics/sentiment
 */
export const getSentimentAnalysis = asyncHandler(async (req, res, next) => {
  res.ok({}, "Analytics Sentiment API Working - Controller Active");
});
