import express from 'express';
import * as analyticsController from '../controllers/analyticsController.js';

const router = express.Router();

router.get('/performance', analyticsController.getPerformanceMetrics);
router.get('/sentiment', analyticsController.getSentimentAnalysis);

export default router;
