# ══════════════════════════════════════════════════════════════════
# Dockerfile — React + Vite Frontend (client/)
# Multi-stage: build → nginx production server
# ══════════════════════════════════════════════════════════════════

# ── Stage 1: Build ────────────────────────────────────────────────
FROM node:20-alpine AS builder

LABEL stage="builder"
LABEL app="cx-guardian-client"

WORKDIR /app

# Install dependencies first (cached layer)
COPY package.json package-lock.json* ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY . .

# Pass build-time env vars from Docker build args
ARG VITE_API_URL=http://localhost:5000
ARG VITE_SOCKET_URL=http://localhost:5000
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SOCKET_URL=$VITE_SOCKET_URL

RUN npm run build

# ── Stage 2: Production nginx server ─────────────────────────────
FROM nginx:1.27-alpine AS production

LABEL app="cx-guardian-client"
LABEL version="1.0.0"

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config for SPA routing (React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
