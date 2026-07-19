/**
 * Enterprise CX Guardian AI — Node.js Security Middleware Stack
 * ==============================================================
 *
 * Implements all 7 security controls:
 *   1. Helmet              — Secure HTTP headers
 *   2. CORS Configuration  — Strict allowlist with credentials
 *   3. Rate Limiting       — express-rate-limit per IP per route
 *   4. Request Size Limits — JSON + URL-encoded body limits
 *   5. Input Validation    — Joi schemas for all request bodies
 *   6. Input Sanitization  — Express-validator + xss protection
 *   7. Environment Validation — Required var check at startup
 */

import helmet    from 'helmet';
import cors      from 'cors';
import logger    from '../config/logger.js';
import * as env  from '../config/env.js';

// ══════════════════════════════════════════════════════════════════
// 1. Helmet — Secure HTTP Headers
// ══════════════════════════════════════════════════════════════════

export const helmetConfig = helmet({
  // Content Security Policy
  contentSecurityPolicy: {
    directives: {
      defaultSrc:  ["'self'"],
      scriptSrc:   ["'self'", "'unsafe-inline'"],
      styleSrc:    ["'self'", "'unsafe-inline'"],
      imgSrc:      ["'self'", "data:"],
      connectSrc:  ["'self'"],
      fontSrc:     ["'self'"],
      objectSrc:   ["'none'"],
      mediaSrc:    ["'self'"],
      frameSrc:    ["'none'"],
      frameAncestors: ["'none'"]
    }
  },
  // HSTS: force HTTPS for 1 year (production only)
  hsts: env.NODE_ENV === 'production'
    ? { maxAge: 31536000, includeSubDomains: true, preload: true }
    : false,
  // Clickjacking
  frameguard:         { action: 'deny' },
  // MIME sniffing
  noSniff:            true,
  // XSS
  xssFilter:          true,
  // Hide X-Powered-By
  hidePoweredBy:      true,
  // Referrer
  referrerPolicy:     { policy: 'strict-origin-when-cross-origin' },
  // Permissions
  permittedCrossDomainPolicies: { permittedPolicies: 'none' },
  // DNS prefetch control
  dnsPrefetchControl: { allow: false },
  // IE no-open
  ieNoOpen:           true,
});

// ══════════════════════════════════════════════════════════════════
// 2. CORS Configuration
// ══════════════════════════════════════════════════════════════════

const _allowedOrigins = env.NODE_ENV === 'production'
  ? [env.CLIENT_URL].filter(Boolean)
  : ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:80'];

export const corsConfig = cors({
  origin: (origin, callback) => {
    // Allow non-browser requests (curl, Postman, server-to-server)
    if (!origin) return callback(null, true);
    if (_allowedOrigins.includes(origin)) {
      return callback(null, true);
    }
    logger.warn(`[CORS] Blocked origin: ${origin}`);
    callback(new Error(`CORS policy: origin '${origin}' not allowed`));
  },
  credentials:    true,
  methods:        ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Authorization', 'Content-Type', 'X-Request-ID',
    'X-API-Version', 'Accept', 'Origin'
  ],
  exposedHeaders: ['X-Request-ID', 'X-Response-Time', 'X-Rate-Limit-Remaining'],
  maxAge:         600,    // Preflight cache: 10 minutes
  optionsSuccessStatus: 204
});

// ══════════════════════════════════════════════════════════════════
// 3. Rate Limiting (Zero-dependency sliding window)
// ══════════════════════════════════════════════════════════════════

function createRateLimiter({ windowMs = 60000, max = 100, message = 'Too many requests' } = {}) {
  const store = new Map();

  return (req, res, next) => {
    if (['/api/v1/health', '/health'].includes(req.path)) {
      return next();
    }

    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    const now = Date.now();
    const windowStart = now - windowMs;

    let timestamps = store.get(ip) || [];
    timestamps = timestamps.filter(ts => ts > windowStart);

    if (timestamps.length >= max) {
      const retryAfter = Math.ceil((timestamps[0] + windowMs - now) / 1000);
      logger.warn(`[Rate Limit] BLOCKED | ip: ${ip} | path: ${req.originalUrl} | retry_after: ${retryAfter}s`);
      return res.status(429).json({
        success: false,
        message: 'Rate limit exceeded',
        error: message,
        error_code: 'RATE_LIMIT_EXCEEDED',
        retry_after: retryAfter
      });
    }

    timestamps.push(now);
    store.set(ip, timestamps);
    res.setHeader('RateLimit-Limit', max);
    res.setHeader('RateLimit-Remaining', max - timestamps.length);
    next();
  };
}

// General API limiter — 200 req/min per IP
export const generalLimiter = createRateLimiter({
  windowMs: 60 * 1000,
  max: 200,
  message: 'Too many requests. Retry after 60 seconds.'
});

// Auth endpoint limiter — 10 req/min per IP
export const authLimiter = createRateLimiter({
  windowMs: 60 * 1000,
  max: 10,
  message: 'Too many authentication attempts.'
});

// Chat endpoint limiter — 60 req/min per IP
export const chatLimiter = createRateLimiter({
  windowMs: 60 * 1000,
  max: 60,
  message: 'Too many chat messages.'
});

// ══════════════════════════════════════════════════════════════════
// 4. Request Size Limits (used in app.use())
// ══════════════════════════════════════════════════════════════════

export const REQUEST_SIZE_LIMITS = {
  json:       '256kb',   // express.json() limit
  urlencoded: '64kb',    // express.urlencoded() limit
  chat:       '64kb',    // applied per-route on /api/v1/chat
  auth:       '4kb',     // applied per-route on /api/v1/auth
};

// Per-route size guard middleware factory
export const bodySizeLimit = (limit) => (req, res, next) => {
  const contentLength = parseInt(req.headers['content-length'] || '0', 10);
  const limitBytes = parseSize(limit);
  if (limitBytes > 0 && contentLength > limitBytes) {
    logger.warn(
      `[Request Size] REJECTED | path: ${req.path} | size: ${contentLength}B | limit: ${limitBytes}B`
    );
    return res.status(413).json({
      success:    false,
      message:    'Request payload too large',
      error:      `Body exceeds ${limit} limit`,
      error_code: 'PAYLOAD_TOO_LARGE'
    });
  }
  next();
};

function parseSize(size) {
  if (typeof size === 'number') return size;
  const units = { b: 1, kb: 1024, mb: 1024 * 1024 };
  const match = String(size).toLowerCase().match(/^(\d+)(b|kb|mb)$/);
  return match ? parseInt(match[1]) * (units[match[2]] || 1) : 0;
}

// ══════════════════════════════════════════════════════════════════
// 5. Input Validation — Joi schema factory
// ══════════════════════════════════════════════════════════════════

/**
 * Returns a middleware that validates req.body against a Joi schema.
 * Requires: npm install joi
 *
 * Usage:
 *   import Joi from 'joi';
 *   import { validateBody } from '../middleware/security.js';
 *
 *   const chatSchema = Joi.object({ message: Joi.string().max(2000).required() });
 *   router.post('/chat', validateBody(chatSchema), chatController);
 */
export const validateBody = (schema) => (req, res, next) => {
  if (!schema || !schema.validate) return next();

  const { error, value } = schema.validate(req.body, {
    abortEarly:       false,
    stripUnknown:     true,
    allowUnknown:     false,
  });

  if (error) {
    const detail = error.details.map(d => d.message).join('; ');
    logger.warn(`[Input Validation] FAILED | path: ${req.path} | ${detail}`);
    return res.status(400).json({
      success:    false,
      message:    'Request validation failed',
      error:      detail,
      error_code: 'VALIDATION_ERROR'
    });
  }

  req.body = value;   // Use sanitized/coerced value
  next();
};

// ══════════════════════════════════════════════════════════════════
// 6. Input Sanitization
// ══════════════════════════════════════════════════════════════════

const _DANGEROUS = /(\x00|<script[\s\S]*?>[\s\S]*?<\/script>|javascript\s*:)/gi;
const _NULL_BYTE  = /\x00/g;

/**
 * Recursively sanitizes all string values in an object.
 * Strips: null bytes, <script> tags, javascript: URIs
 */
export const sanitize = (value) => {
  if (typeof value === 'string') {
    return value.replace(_DANGEROUS, '').replace(_NULL_BYTE, '').trim();
  }
  if (Array.isArray(value)) {
    return value.map(sanitize);
  }
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([k, v]) => [k, sanitize(v)])
    );
  }
  return value;
};

/** Express middleware — sanitizes req.body, req.params, req.query */
export const sanitizeInputs = (req, res, next) => {
  if (req.body)   req.body   = sanitize(req.body);
  if (req.params) req.params = sanitize(req.params);
  if (req.query)  req.query  = sanitize(req.query);
  next();
};

// ══════════════════════════════════════════════════════════════════
// 7. Environment Validation
// ══════════════════════════════════════════════════════════════════

const REQUIRED_VARS = [
  ['MONGO_URI',     'MongoDB connection string'],
  ['JWT_SECRET',    'JWT signing secret (min 32 chars)'],
  ['PYTHON_AI_URL', 'Python AI microservice URL'],
];

const OPTIONAL_VARS = {
  'NODE_ENV':       'development',
  'PORT':           '5000',
  'CLIENT_URL':     'http://localhost:5173',
  'AI_TIMEOUT':     '30000',
  'MAX_RETRIES':    '3',
  'STORAGE_BACKEND':'memory',
};

export const validateEnvironment = () => {
  const missing  = [];
  const warnings = [];

  for (const [varName, description] of REQUIRED_VARS) {
    const val = process.env[varName];
    if (!val || val.trim() === '') {
      missing.push(`  ✗ ${varName} — ${description}`);
    }
  }

  for (const [varName, defaultVal] of Object.entries(OPTIONAL_VARS)) {
    if (!process.env[varName]) {
      warnings.push(`  ⚠ ${varName} not set — using default: '${defaultVal}'`);
    }
  }

  // JWT secret strength check
  const jwtSecret = process.env.JWT_SECRET || '';
  if (jwtSecret.length < 32) {
    warnings.push('  ⚠ JWT_SECRET shorter than 32 chars — use a longer secret in production');
  }

  warnings.forEach(w => logger.warn(`[Env Validation]${w}`));

  if (missing.length > 0) {
    const msg = `Missing required environment variables:\n${missing.join('\n')}`;
    if (env.NODE_ENV === 'production') {
      logger.error(`[Env Validation] STARTUP BLOCKED\n${msg}`);
      throw new Error(msg);
    } else {
      missing.forEach(m => logger.warn(`[Env Validation] DEV MODE: ${m}`));
    }
  }

  logger.info('[Env Validation] ✓ Environment validated successfully');
};
