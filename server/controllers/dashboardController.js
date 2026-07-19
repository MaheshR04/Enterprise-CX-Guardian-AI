import asyncHandler from '../utils/asyncHandler.js';
import dashboardService from '../services/dashboard.service.js';

/**
 * @desc Get aggregated dashboard summary
 * @route GET /api/v1/dashboard/summary
 */
export const getDashboardSummary = asyncHandler(async (req, res, next) => {
  const summary = await dashboardService.getSummary();
  res.ok(summary, "Dashboard summary retrieved successfully");
});

/**
 * @desc Get system health metrics
 * @route GET /api/v1/dashboard/health
 */
export const getSystemHealth = asyncHandler(async (req, res, next) => {
  const health = await dashboardService.getSystemHealth();
  res.ok(health, "System health metrics retrieved successfully");
});

/**
 * @desc Get LLM model usage telemetry
 * @route GET /api/v1/dashboard/model-usage
 */
export const getModelUsage = asyncHandler(async (req, res, next) => {
  const modelUsage = await dashboardService.getModelUsage();
  res.ok(modelUsage, "Model usage telemetry retrieved successfully");
});

/**
 * @desc Get conversation analytics
 * @route GET /api/v1/dashboard/conversations
 */
export const getConversationAnalytics = asyncHandler(async (req, res, next) => {
  const analytics = await dashboardService.getConversationAnalytics();
  res.ok(analytics, "Conversation analytics retrieved successfully");
});

/**
 * @desc Get user analytics
 * @route GET /api/v1/dashboard/users
 */
export const getUserAnalytics = asyncHandler(async (req, res, next) => {
  const userAnalytics = await dashboardService.getUserAnalytics();
  res.ok(userAnalytics, "User analytics retrieved successfully");
});

/**
 * @desc Get document and RAG analytics
 * @route GET /api/v1/dashboard/documents
 */
export const getDocumentAnalytics = asyncHandler(async (req, res, next) => {
  const docAnalytics = await dashboardService.getDocumentAnalytics();
  res.ok(docAnalytics, "Document analytics retrieved successfully");
});
