import { logger } from '../config/index.js';

/**
 * HTTP requests logging middleware utilizing Winston loggers.
 */
const requestLogger = (req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms (IP: ${req.ip})`);
  });

  next();
};

export default requestLogger;
