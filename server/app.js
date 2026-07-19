import express      from 'express';
import cookieParser  from 'cookie-parser';

// ── Security middleware ────────────────────────────────────────────
import {
  helmetConfig,
  corsConfig,
  generalLimiter,
  sanitizeInputs,
  validateEnvironment,
  REQUEST_SIZE_LIMITS
} from './middleware/security.js';

// ── Performance middleware ─────────────────────────────────────────
import {
  compressionConfig,
  cacheMiddleware,
  ensureIndexes,
  taskQueue
} from './middleware/performance.js';

// ── Core middleware ────────────────────────────────────────────────
import requestLogger    from './middleware/requestLogger.js';
import errorHandler     from './middleware/errorHandler.js';
import notFound         from './middleware/notFound.js';
import responseFormatter from './middleware/responseFormatter.js';

import logger           from './config/logger.js';
import repositoryFactory from './repositories/repositoryFactory.js';

// ── Validate required environment variables at boot ────────────────
validateEnvironment();

// ── Initialize repository factory ─────────────────────────────────
await repositoryFactory.initialize();

// ── Versioned API router ───────────────────────────────────────────
const { default: versionRouter } = await import('./routes/versionRouter.js');

// ══════════════════════════════════════════════════════════════════
// Express App
// ══════════════════════════════════════════════════════════════════
const app = express();

// ── 1. Security: Helmet (secure headers) ─────────────────────────
app.use(helmetConfig);

// ── 2. Security: CORS ────────────────────────────────────────────
app.use(corsConfig);

// ── 3. Performance: Compression (gzip/deflate) ───────────────────
app.use(compressionConfig);

// ── 4. Parsing with size limits ──────────────────────────────────
app.use(express.json({ limit: REQUEST_SIZE_LIMITS.json }));
app.use(express.urlencoded({ extended: true, limit: REQUEST_SIZE_LIMITS.urlencoded }));
app.use(cookieParser());

// ── 5. Security: Input sanitization ─────────────────────────────
app.use(sanitizeInputs);

// ── 6. Security: Global rate limiting ───────────────────────────
app.use(generalLimiter);

// ── 7. Performance: HTTP cache (ETag + conditional) ─────────────
app.use(cacheMiddleware);

// ── 8. Response helpers & logging ────────────────────────────────
app.use(responseFormatter);

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const ms = Date.now() - start;
    res.setHeader('X-Response-Time', `${ms}ms`);
    logger.http.request(req.method, req.originalUrl, res.statusCode, ms);
  });
  next();
});

app.use(requestLogger);

// ── 9. Route dispatching ─────────────────────────────────────────
// /api/v1/*, /api/v2/*, /api/versions
app.use('/api', versionRouter);

// ── 10. Error handlers ───────────────────────────────────────────
app.use(notFound);
app.use(errorHandler);

logger.info('[App] Express application configured with security + performance stack');

export default app;
export { ensureIndexes, taskQueue };
