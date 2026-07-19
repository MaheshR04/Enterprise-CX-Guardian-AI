import express from 'express';
import * as dashboardController from '../controllers/dashboardController.js';

const router = express.Router();

router.get('/summary',       dashboardController.getDashboardSummary);
router.get('/health',        dashboardController.getSystemHealth);
router.get('/model-usage',   dashboardController.getModelUsage);
router.get('/conversations', dashboardController.getConversationAnalytics);
router.get('/users',         dashboardController.getUserAnalytics);
router.get('/documents',     dashboardController.getDocumentAnalytics);

export default router;
