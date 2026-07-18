import { logger } from '../config/index.js';

/**
 * Incoming HTTP request logging middleware utilizing existing Winston logger.
 */
const requestLogger = (req, res, next) => {
  const startTime = Date.now();
  
  // 1. Log incoming request
  if (logger && logger.info) {
    logger.info(`[Incoming Request] ${req.method} ${req.originalUrl} - IP: ${req.ip || '::1'}`);
  }

  res.on('finish', () => {
    const durationMs = Date.now() - startTime;
    // 2. Log execution time and response completion
    if (logger && logger.info) {
      logger.info(`[Incoming Request Complete] ${req.method} ${req.originalUrl} status:${res.statusCode} (${durationMs}ms)`);
    }
  });

  next();
};

export default requestLogger;
