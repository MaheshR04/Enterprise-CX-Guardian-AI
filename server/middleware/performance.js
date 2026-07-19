/**
 * Enterprise CX Guardian AI — Node.js Performance Layer
 * ======================================================
 *
 * Implements all 5 performance features:
 *   1. Response Compression  — compression middleware (gzip/deflate/br)
 *   2. In-Memory Cache       — LRU+TTL with ETag support
 *   3. Database Indexes      — Index definitions for MongoDB queries
 *   4. Lazy Loading          — Deferred singleton factory
 *   5. Async Processing      — Non-blocking background job queue
 */

import compression from 'compression';
import logger from '../config/logger.js';

// ══════════════════════════════════════════════════════════════════
// 1. Response Compression
// ══════════════════════════════════════════════════════════════════

export const compressionConfig = compression({
  // Only compress if response > 1 KB
  threshold: 1024,
  // Compression level 6 — balanced (1=fast, 9=smallest)
  level: 6,
  // Skip compression for SSE streams (text/event-stream)
  filter: (req, res) => {
    if (req.headers['x-no-compression']) return false;
    const contentType = res.getHeader('Content-Type') || '';
    if (String(contentType).includes('text/event-stream')) return false;
    return compression.filter(req, res);
  }
});

// ══════════════════════════════════════════════════════════════════
// 2. In-Memory LRU+TTL Cache
// ══════════════════════════════════════════════════════════════════

class CacheEntry {
  constructor(value, ttl) {
    this.value     = value;
    this.expiresAt = Date.now() + ttl * 1000;
    this.etag      = this._hash(value);
  }
  isExpired()  { return Date.now() > this.expiresAt; }
  _hash(value) {
    const s = JSON.stringify(value, null, 0);
    let h = 0;
    for (let i = 0; i < s.length; i++) {
      h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
    }
    return Math.abs(h).toString(16).padStart(8, '0');
  }
}

class InMemoryCache {
  constructor(maxSize = 1000) {
    this._store   = new Map();
    this._maxSize = maxSize;
    this._hits    = 0;
    this._misses  = 0;
  }

  get(key) {
    const entry = this._store.get(key);
    if (!entry || entry.isExpired()) {
      this._store.delete(key);
      this._misses++;
      return { value: null, etag: null, hit: false };
    }
    // LRU: re-insert to move to end
    this._store.delete(key);
    this._store.set(key, entry);
    this._hits++;
    return { value: entry.value, etag: entry.etag, hit: true };
  }

  set(key, value, ttl = 30) {
    if (this._store.size >= this._maxSize) {
      // Evict oldest (LRU — Map preserves insertion order)
      this._store.delete(this._store.keys().next().value);
    }
    const entry = new CacheEntry(value, ttl);
    this._store.set(key, entry);
    return entry.etag;
  }

  delete(key) { this._store.delete(key); }

  invalidatePrefix(prefix) {
    let count = 0;
    for (const key of this._store.keys()) {
      if (key.startsWith(prefix)) { this._store.delete(key); count++; }
    }
    return count;
  }

  clear() { this._store.clear(); }

  get stats() {
    const total = this._hits + this._misses;
    return {
      size:     this._store.size,
      maxSize:  this._maxSize,
      hits:     this._hits,
      misses:   this._misses,
      hitRate:  total ? `${((this._hits / total) * 100).toFixed(1)}%` : '0%'
    };
  }
}

// Global cache singleton
export const cache = new InMemoryCache(1000);

// TTL configuration
export const CACHE_TTL = {
  conversationsList:   30,    // seconds
  conversationDetail:  60,
  health:              10,
  analytics:           120,
};

// ── Express cache middleware ──────────────────────────────────────

const _CACHEABLE_PREFIXES = [
  '/api/v1/conversations',
  '/api/v1/analytics',
  '/api/v1/health',
];

const _MUTATION_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export const cacheMiddleware = (req, res, next) => {
  // Skip mutations
  if (_MUTATION_METHODS.has(req.method)) {
    res.setHeader('Cache-Control', 'no-store');
    return next();
  }

  // Only cache matching GET routes
  const cacheable = _CACHEABLE_PREFIXES.some(p => req.path.startsWith(p));
  if (req.method !== 'GET' || !cacheable) return next();

  const key = `${req.path}|${JSON.stringify(req.query)}`;
  const { value, etag, hit } = cache.get(key);

  if (hit) {
    // Conditional request — 304
    if (req.headers['if-none-match'] === `"${etag}"`) {
      return res.status(304).set('ETag', `"${etag}"`).end();
    }
    logger.debug(`[Cache] HIT | ${req.path}`);
    return res.set({
      'ETag':          `"${etag}"`,
      'X-Cache':       'HIT',
      'Cache-Control': 'private, max-age=30'
    }).json(value);
  }

  // Intercept response to populate cache
  const _json = res.json.bind(res);
  res.json = (body) => {
    if (res.statusCode === 200) {
      const ttl  = req.path.includes('/conversations/')
        ? CACHE_TTL.conversationDetail
        : req.path.includes('/conversations')
        ? CACHE_TTL.conversationsList
        : req.path.includes('/analytics')
        ? CACHE_TTL.analytics
        : CACHE_TTL.health;

      const newEtag = cache.set(key, body, ttl);
      res.set({
        'ETag':          `"${newEtag}"`,
        'X-Cache':       'MISS',
        'Cache-Control': `private, max-age=${ttl}`
      });
      logger.debug(`[Cache] SET | ${req.path} | ttl: ${ttl}s`);
    }
    return _json(body);
  };

  next();
};

// ══════════════════════════════════════════════════════════════════
// 3. Database Index Definitions
// ══════════════════════════════════════════════════════════════════

/**
 * Ensures all MongoDB indexes are created at startup.
 * Idempotent — safe to call on every server restart.
 * Complements the docker/mongo-init.js indexes.
 */
export const ensureIndexes = async (db) => {
  if (!db) {
    logger.warn('[Indexes] No DB connection — skipping index creation');
    return;
  }

  const indexes = [
    // Conversations
    { collection: 'conversations', spec: { conversation_id: 1 }, opts: { unique: true, background: true } },
    { collection: 'conversations', spec: { status: 1 },           opts: { background: true } },
    { collection: 'conversations', spec: { created_at: -1 },      opts: { background: true } },
    { collection: 'conversations', spec: { status: 1, created_at: -1 }, opts: { background: true } },

    // Messages
    { collection: 'messages', spec: { conversation_id: 1, timestamp: 1 }, opts: { background: true } },
    { collection: 'messages', spec: { message_id: 1 },                    opts: { unique: true, background: true } },

    // Prompt logs
    { collection: 'prompt_logs', spec: { conversation_id: 1, created_at: -1 }, opts: { background: true } },

    // AI usage
    { collection: 'ai_usage', spec: { conversation_id: 1, timestamp: -1 }, opts: { background: true } },

    // Users
    { collection: 'users', spec: { email: 1 }, opts: { unique: true, background: true } },

    // Refresh tokens — TTL index (auto-delete expired tokens)
    { collection: 'refresh_tokens', spec: { token: 1 },      opts: { unique: true, background: true } },
    { collection: 'refresh_tokens', spec: { expires_at: 1 }, opts: { expireAfterSeconds: 0, background: true } },
  ];

  for (const { collection, spec, opts } of indexes) {
    try {
      await db.collection(collection).createIndex(spec, opts);
      logger.debug(`[Indexes] ✓ ${collection} ${JSON.stringify(spec)}`);
    } catch (err) {
      // Code 85 = index already exists with different options (non-fatal in dev)
      if (err.code !== 85 && err.code !== 86) {
        logger.warn(`[Indexes] ⚠ ${collection} — ${err.message}`);
      }
    }
  }
  logger.info(`[Indexes] ✓ All ${indexes.length} indexes verified`);
};

// ══════════════════════════════════════════════════════════════════
// 4. Lazy Loading — Deferred Singleton Registry
// ══════════════════════════════════════════════════════════════════

class LazyRegistry {
  constructor() {
    this._factories   = new Map();
    this._instances   = new Map();
    this._initTimes   = new Map();
  }

  /**
   * Register a factory function for lazy instantiation.
   * factory can be sync or async.
   */
  register(name, factory) {
    this._factories.set(name, factory);
    return this;
  }

  /**
   * Get or create a singleton instance.
   * Awaits async factories automatically.
   */
  async get(name) {
    if (!this._instances.has(name)) {
      const factory = this._factories.get(name);
      if (!factory) throw new Error(`[LazyRegistry] No factory for '${name}'`);
      const start = Date.now();
      const instance = await factory();
      const elapsed = Date.now() - start;
      this._instances.set(name, instance);
      this._initTimes.set(name, elapsed);
      logger.info(`[LazyLoad] Initialized '${name}' | ${elapsed}ms`);
    }
    return this._instances.get(name);
  }

  get loaded() {
    return Object.fromEntries(this._initTimes);
  }
}

export const lazyRegistry = new LazyRegistry();

// ══════════════════════════════════════════════════════════════════
// 5. Async Background Task Queue
// ══════════════════════════════════════════════════════════════════

class AsyncTaskQueue {
  constructor() {
    this._queue     = [];
    this._running   = false;
    this._processed = 0;
    this._failed    = 0;
  }

  /**
   * Enqueue an async function to run in the background.
   * Returns immediately — never blocks the request handler.
   *
   * Usage:
   *   taskQueue.enqueue(() => saveAnalytics(conversationId, data));
   */
  enqueue(asyncFn, label = 'task') {
    this._queue.push({ fn: asyncFn, label });
    if (!this._running) this._drain();
  }

  _drain() {
    if (this._queue.length === 0) {
      this._running = false;
      return;
    }
    this._running = true;
    setImmediate(async () => {
      const item = this._queue.shift();
      if (!item) { this._running = false; return; }
      try {
        await item.fn();
        this._processed++;
        logger.debug(`[AsyncQueue] ✓ ${item.label}`);
      } catch (err) {
        this._failed++;
        logger.error(`[AsyncQueue] ✗ ${item.label} | ${err.message}`);
      }
      this._drain();
    });
  }

  get stats() {
    return {
      queueSize:  this._queue.length,
      processed:  this._processed,
      failed:     this._failed,
      running:    this._running
    };
  }
}

export const taskQueue = new AsyncTaskQueue();
