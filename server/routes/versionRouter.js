/**
 * Enterprise CX Guardian AI — Node.js API Version Router
 * =======================================================
 *
 * Mounts versioned sub-routers and exposes version discovery:
 *   GET /api/versions   — Version discovery endpoint
 *   /api/v1/*           — Current stable routes
 *   /api/v2/*           — Future stub (uncomment to activate)
 *
 * To add v2:
 *   1. Create routes/v2/index.js with your v2 routes
 *   2. Uncomment the v2 block below
 *   3. Update CURRENT_VERSION = 'v2' when stable
 */

import express from 'express';
import logger from '../config/logger.js';

const versionRouter = express.Router();

// ── Version metadata ───────────────────────────────────────────────
const CURRENT_VERSION    = 'v1';
const SUPPORTED_VERSIONS = ['v1'];
const DEPRECATED_VERSIONS = [];

// ── v1 routes ──────────────────────────────────────────────────────
const { default: v1Router } = await import('./v1/index.js');
versionRouter.use('/v1', v1Router);
logger.info('[API Version] Registered: /api/v1 — stable');

// ── v2 routes (stub — uncomment when ready) ────────────────────────
// const { default: v2Router } = await import('./v2/index.js');
// versionRouter.use('/v2', v2Router);
// logger.info('[API Version] Registered: /api/v2 — beta');

logger.info(`[API Version] Current: ${CURRENT_VERSION} | Supported: [${SUPPORTED_VERSIONS}] | Deprecated: [${DEPRECATED_VERSIONS}]`);

// ── Version discovery endpoint — GET /api/versions ─────────────────
versionRouter.get('/versions', (req, res) => {
  res.json({
    success:         true,
    current_version: CURRENT_VERSION,
    supported:       SUPPORTED_VERSIONS,
    deprecated:      DEPRECATED_VERSIONS,
    base_url:        '/api',
    versions: {
      v1: {
        status:      'stable',
        prefix:      '/api/v1',
        released:    '2026-07-01',
        deprecated:  false,
        sunset_date: null,
        endpoints: {
          health:       '/api/v1/health',
          auth:         '/api/v1/auth',
          chat:         '/api/v1/chat',
          customers:    '/api/v1/customers',
          tickets:      '/api/v1/tickets',
          dashboard:    '/api/v1/dashboard',
          analytics:    '/api/v1/analytics'
        }
      },
      v2: {
        status:     'planned',
        prefix:     '/api/v2',
        released:   null,
        deprecated: false,
        note:       'v2 is under development. Not available yet.'
      }
    },
    timestamp: new Date().toISOString()
  });
});

export default versionRouter;
