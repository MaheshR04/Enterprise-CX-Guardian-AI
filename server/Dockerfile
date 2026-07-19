# ══════════════════════════════════════════════════════════════════
# Dockerfile — Node.js / Express Backend (server/)
# Multi-stage: dependencies → lean production image
# ══════════════════════════════════════════════════════════════════

# ── Stage 1: Install dependencies ────────────────────────────────
FROM node:20-alpine AS deps

LABEL stage="deps"

WORKDIR /app

COPY package.json package-lock.json* ./
# Install production dependencies only
RUN npm ci --omit=dev --frozen-lockfile

# ── Stage 2: Production image ─────────────────────────────────────
FROM node:20-alpine AS production

LABEL app="cx-guardian-server"
LABEL version="1.0.0"

# Security: run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser  -S nodeapp -u 1001 -G nodejs

WORKDIR /app

# Copy installed node_modules from deps stage
COPY --from=deps --chown=nodeapp:nodejs /app/node_modules ./node_modules

# Copy application source
COPY --chown=nodeapp:nodejs . .

# Create log directory
RUN mkdir -p /app/logs && chown nodeapp:nodejs /app/logs

# Switch to non-root user
USER nodeapp

# Expose Express port
EXPOSE 5000

# Healthcheck — calls GET /api/v1/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:5000/api/v1/health || exit 1

# Start Node server
CMD ["node", "server.js"]
