/**
 * /api/v1 sub-router — all stable routes for version 1.
 * Mirrors the structure of server/routes/index.js
 * but isolated per version for independent evolution.
 */

import express from 'express';
import healthRoutes       from '../health.routes.js';
import authRoutes         from '../auth.routes.js';
import customerRoutes     from '../customer.routes.js';
import ticketRoutes       from '../ticket.routes.js';
import dashboardRoutes    from '../dashboard.routes.js';
import analyticsRoutes    from '../analytics.routes.js';
import chatRoutes         from '../chat.routes.js';

const v1Router = express.Router();

v1Router.use('/health',    healthRoutes);
v1Router.use('/auth',      authRoutes);
v1Router.use('/customers', customerRoutes);
v1Router.use('/tickets',   ticketRoutes);
v1Router.use('/dashboard', dashboardRoutes);
v1Router.use('/analytics', analyticsRoutes);
v1Router.use('/chat',      chatRoutes);

export default v1Router;
