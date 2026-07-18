import asyncHandler from '../utils/asyncHandler.js';
import analyticsService from '../services/analytics.service.js';

/**
 * @desc Get analytics performance metrics
 * @route GET /api/v1/analytics/performance
 */
export const getPerformanceMetrics = asyncHandler(async (req, res, next) => {
  const metrics = await analyticsService.getPerformanceMetrics();
  res.ok(metrics, "Analytics Performance API Working - Controller Active");
});

/**
 * @desc Get customer sentiment distributions
 * @route GET /api/v1/analytics/sentiment
 */
export const getSentimentAnalysis = asyncHandler(async (req, res, next) => {
  const sentiment = await analyticsService.getSentimentAnalysis();
  res.ok(sentiment, "Analytics Sentiment API Working - Controller Active");
});
