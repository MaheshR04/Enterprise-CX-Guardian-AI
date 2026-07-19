/**
 * Enterprise CX Guardian AI — Node.js Centralized Logger
 * =======================================================
 *
 * 7 Logging Categories (matches FastAPI service):
 *   1. auth       — login, logout, token events, failures
 *   2. ai         — AI proxy requests, model, tokens, latency
 *   3. db         — MongoDB queries, connections, CRUD timing
 *   4. rag        — RAG retrieval calls (future)
 *   5. tool       — Sentiment, reasoning, recommendation tool calls
 *   6. error      — Domain errors, validation, unexpected exceptions
 *   7. http       — Response time, per-route latency, slow request alerts
 *
 * Transports:
 *   - Console (colored, dev-friendly)
 *   - logs/error.log (error-level only, JSON)
 *   - logs/combined.log (all levels, JSON, structured)
 *   - logs/audit.log (auth events only, JSON — for compliance)
 */

import winston from 'winston';
import path from 'path';
import { fileURLToPath } from 'url';
import * as env from './env.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const LOG_DIR    = path.join(__dirname, '../logs');

// ── Latency thresholds ─────────────────────────────────────────────
const LATENCY_WARN_MS  = 1000;   // 1 second  → WARN
const LATENCY_ERROR_MS = 5000;   // 5 seconds → ERROR

// ══════════════════════════════════════════════════════════════════
// Winston Setup
// ══════════════════════════════════════════════════════════════════

const levels = { error: 0, warn: 1, info: 2, http: 3, debug: 4 };
const colors = { error: 'red', warn: 'yellow', info: 'green', http: 'magenta', debug: 'white' };
winston.addColors(colors);

const getLevel = () => env.NODE_ENV === 'development' ? 'debug' : 'info';

const fileFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

const consoleFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message }) =>
    `[${timestamp}] [${level}]: ${message}`
  )
);

const _base = winston.createLogger({
  level: getLevel(),
  levels,
  transports: [
    new winston.transports.Console({ format: consoleFormat }),
    new winston.transports.File({ filename: `${LOG_DIR}/error.log`,    level: 'error', format: fileFormat }),
    new winston.transports.File({ filename: `${LOG_DIR}/combined.log`, level: 'debug', format: fileFormat }),
  ]
});

// Separate audit transport for auth events (compliance trail)
const _audit = winston.createLogger({
  level: 'info',
  levels,
  transports: [
    new winston.transports.File({ filename: `${LOG_DIR}/audit.log`, format: fileFormat }),
    new winston.transports.Console({ format: consoleFormat })
  ]
});

// ══════════════════════════════════════════════════════════════════
// Private Helpers
// ══════════════════════════════════════════════════════════════════

const _maskEmail = (email = '') => {
  if (!email || !email.includes('@')) return '***';
  const [local, domain] = email.split('@');
  return `${local[0]}***@${domain}`;
};

const _truncate = (text = '', max = 80) => {
  const s = String(text).replace(/\n/g, ' ').trim();
  return s.length > max ? s.slice(0, max) + '…' : s;
};

const _ts = () => new Date().toISOString();

// ══════════════════════════════════════════════════════════════════
// 1. Authentication Logging
// ══════════════════════════════════════════════════════════════════

const auth = {
  attempt:      (email, method = 'password') =>
    _audit.info(`[Auth] LOGIN ATTEMPT | email: ${_maskEmail(email)} | method: ${method}`),

  success:      (userId, email, tokenType = 'access') =>
    _audit.info(`[Auth] ✓ LOGIN SUCCESS | user_id: ${userId} | email: ${_maskEmail(email)} | token: ${tokenType}`),

  failure:      (email, reason, ip = 'unknown') =>
    _audit.warn(`[Auth] ✗ LOGIN FAILED | email: ${_maskEmail(email)} | reason: ${reason} | ip: ${ip}`),

  logout:       (userId) =>
    _audit.info(`[Auth] LOGOUT | user_id: ${userId}`),

  register:     (email, userId) =>
    _audit.info(`[Auth] REGISTER | user_id: ${userId} | email: ${_maskEmail(email)}`),

  tokenRefresh: (userId, success, reason = '') =>
    _audit.info(`[Auth] TOKEN REFRESH | user_id: ${userId} | ${success ? '✓ SUCCESS' : `✗ FAILED (${reason})`}`),

  tokenInvalid: (reason, ip = 'unknown') =>
    _audit.warn(`[Auth] INVALID TOKEN | reason: ${reason} | ip: ${ip}`),
};

// ══════════════════════════════════════════════════════════════════
// 2. AI Request Logging
// ══════════════════════════════════════════════════════════════════

const ai = {
  requestStart: (convId, model, historyTurns, promptChars) =>
    _base.info(`[AI Request] → PROXY | conv_id: ${convId} | model: ${model} | history: ${historyTurns} turns | prompt: ${promptChars} chars`),

  requestSuccess: (convId, model, tokens = {}, latencyMs) => {
    const { prompt = 0, completion = 0, total = 0 } = tokens;
    const throughput = latencyMs > 0 ? ((total / latencyMs) * 1000).toFixed(0) : 0;
    const level = latencyMs >= LATENCY_ERROR_MS ? 'error' : latencyMs >= LATENCY_WARN_MS ? 'warn' : 'info';
    _base[level](`[AI Request] ← OK | conv_id: ${convId} | model: ${model} | tokens: prompt=${prompt} completion=${completion} total=${total} | latency: ${latencyMs.toFixed(0)}ms | throughput: ${throughput} tok/s`);
  },

  requestError: (convId, model, error, latencyMs) =>
    _base.error(`[AI Request] ← ERROR | conv_id: ${convId} | model: ${model} | latency: ${latencyMs?.toFixed(0)}ms | ${error?.message || error}`),

  proxyCall: (endpoint, method, latencyMs, status) =>
    _base.info(`[AI Proxy] ${method} ${endpoint} → ${status} | latency: ${latencyMs?.toFixed(0)}ms`),
};

// ══════════════════════════════════════════════════════════════════
// 3. Database Logging
// ══════════════════════════════════════════════════════════════════

const db = {
  connecting:   (uri, dbName) =>
    _base.info(`[DB] CONNECTING | db: '${dbName}' | uri: ${uri}`),

  connected:    (dbName, latencyMs) =>
    _base.info(`[DB] ✓ CONNECTED | db: '${dbName}' | ping: ${latencyMs?.toFixed(2)}ms`),

  disconnected: (dbName) =>
    _base.info(`[DB] DISCONNECTED | db: '${dbName}'`),

  error:        (operation, err) =>
    _base.error(`[DB] ERROR | op: '${operation}' | ${err?.message || err}`),

  health:       (dbName, healthy, latencyMs, err) =>
    healthy
      ? _base.info(`[DB] HEALTH ✓ | db: '${dbName}' | ping: ${latencyMs?.toFixed(2)}ms`)
      : _base.warn(`[DB] HEALTH ✗ | db: '${dbName}' | error: ${err}`),

  query:        (collection, operation, filter, latencyMs) =>
    _base.debug(`[DB CRUD] ${operation.toUpperCase()} | collection: '${collection}' | filter: ${JSON.stringify(filter)} | latency: ${latencyMs?.toFixed(2)}ms`),

  insert:       (collection, id, latencyMs) =>
    _base.info(`[DB CRUD] INSERT | collection: '${collection}' | id: ${id} | latency: ${latencyMs?.toFixed(2)}ms`),

  update:       (collection, id, field, latencyMs) =>
    _base.info(`[DB CRUD] UPDATE | collection: '${collection}' | id: ${id} | field: ${field} | latency: ${latencyMs?.toFixed(2)}ms`),

  delete:       (collection, id, soft, latencyMs) =>
    _base.info(`[DB CRUD] DELETE ${soft ? 'SOFT' : 'HARD'} | collection: '${collection}' | id: ${id} | latency: ${latencyMs?.toFixed(2)}ms`),

  find:         (collection, key, found, latencyMs) =>
    _base.info(`[DB CRUD] FIND ${found ? 'HIT' : 'MISS'} | collection: '${collection}' | key: ${key} | latency: ${latencyMs?.toFixed(2)}ms`),
};

// ══════════════════════════════════════════════════════════════════
// 4. RAG Retrieval Logging
// ══════════════════════════════════════════════════════════════════

const rag = {
  query:   (query, collection, topK) =>
    _base.info(`[RAG] QUERY | collection: '${collection}' | top_k: ${topK} | query: '${_truncate(query, 60)}'`),

  results: (collection, count, topScore, latencyMs) =>
    _base.info(`[RAG] RETRIEVED | collection: '${collection}' | docs: ${count} | top_score: ${topScore?.toFixed(3)} | latency: ${latencyMs?.toFixed(2)}ms`),

  miss:    (query, collection, reason = 'no results') =>
    _base.warn(`[RAG] MISS | collection: '${collection}' | reason: ${reason} | query: '${_truncate(query, 60)}'`),

  error:   (collection, err, latencyMs) =>
    _base.error(`[RAG] ERROR | collection: '${collection}' | latency: ${latencyMs?.toFixed(2)}ms | ${err?.message || err}`),
};

// ══════════════════════════════════════════════════════════════════
// 5. Tool Call Logging
// ══════════════════════════════════════════════════════════════════

const tool = {
  call:   (toolName, inputPreview, convId) =>
    _base.info(`[Tool] CALL | tool: '${toolName}'${convId ? ` | conv_id: ${convId}` : ''} | input: '${_truncate(inputPreview, 80)}'`),

  result: (toolName, success, latencyMs, resultPreview = '', convId) => {
    const status  = success ? '✓ OK' : '✗ FAILED';
    const preview = resultPreview ? ` | result: '${_truncate(resultPreview, 60)}'` : '';
    const conv    = convId ? ` | conv_id: ${convId}` : '';
    _base[success ? 'info' : 'warn'](`[Tool] ${status} | tool: '${toolName}'${conv} | latency: ${latencyMs?.toFixed(2)}ms${preview}`);
  },

  error:  (toolName, err, latencyMs, convId) =>
    _base.error(`[Tool] ERROR | tool: '${toolName}'${convId ? ` | conv_id: ${convId}` : ''} | latency: ${latencyMs?.toFixed(2)}ms | ${err?.message || err}`),
};

// ══════════════════════════════════════════════════════════════════
// 6. Error Logging
// ══════════════════════════════════════════════════════════════════

const error = {
  domain:      (errorCode, message, statusCode, path) => {
    const level = statusCode >= 500 ? 'error' : 'warn';
    _base[level](`[Error] DOMAIN | code: ${errorCode} | status: ${statusCode} | path: ${path} | msg: ${message}`);
  },

  validation:  (field, value, reason) =>
    _base.warn(`[Error] VALIDATION | field: '${field}' | value: '${value}' | reason: ${reason}`),

  notFound:    (resource, id) =>
    _base.warn(`[Error] NOT FOUND | resource: '${resource}' | id: '${id}'`),

  unexpected:  (context, err) =>
    _base.error(`[Error] UNEXPECTED | context: ${context} | ${err?.stack || err}`),

  middleware:  (path, method, err) =>
    _base.error(`[Error] MIDDLEWARE | ${method} ${path} | ${err?.message || err}`),
};

// ══════════════════════════════════════════════════════════════════
// 7. HTTP / Response Time Logging
// ══════════════════════════════════════════════════════════════════

const http = {
  request: (method, path, statusCode, latencyMs) => {
    let level, perf;
    if      (latencyMs >= LATENCY_ERROR_MS) { level = 'error'; perf = '🔴 SLOW'; }
    else if (latencyMs >= LATENCY_WARN_MS)  { level = 'warn';  perf = '🟡 SLOW'; }
    else if (statusCode >= 500)             { level = 'error'; perf = '⚠';      }
    else if (statusCode >= 400)             { level = 'warn';  perf = '⚠';      }
    else                                    { level = 'info';  perf = '✓';      }
    _base[level](`[HTTP] ${perf} ${method} ${path} → ${statusCode} | latency: ${latencyMs?.toFixed(2)}ms`);
  },

  slow: (method, path, latencyMs, thresholdMs) =>
    _base.warn(`[HTTP] SLOW REQUEST | ${method} ${path} | latency: ${latencyMs?.toFixed(0)}ms > threshold: ${thresholdMs}ms`),
};

// ══════════════════════════════════════════════════════════════════
// Exports
// ══════════════════════════════════════════════════════════════════

const logger = {
  // Category namespaces
  auth,
  ai,
  db,
  rag,
  tool,
  error,
  http,

  // Direct winston pass-through for generic logging
  info:  (...args) => _base.info(...args),
  warn:  (...args) => _base.warn(...args),
  debug: (...args) => _base.debug(...args),
  error: (...args) => _base.error(...args),
  http:  (...args) => _base.http(...args),
};

export default logger;
