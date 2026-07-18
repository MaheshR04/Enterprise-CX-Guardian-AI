import express from 'express';
import healthRoutes from './health.routes.js';
import authRoutes from './auth.routes.js';
import customerRoutes from './customer.routes.js';
import ticketRoutes from './ticket.routes.js';
import dashboardRoutes from './dashboard.routes.js';
import analyticsRoutes from './analytics.routes.js';
import chatRoutes from './chat.routes.js';

const router = express.Router();

// Register router sub-modules
router.use('/health', healthRoutes);
router.use('/auth', authRoutes);
router.use('/customers', customerRoutes);
router.use('/tickets', ticketRoutes);
router.use('/dashboard', dashboardRoutes);
router.use('/analytics', analyticsRoutes);
router.use('/chat', chatRoutes);

export default router;
