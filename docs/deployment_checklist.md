# Enterprise CX Guardian AI — Production Deployment Checklist

Verify all items prior to launching or demonstrating the platform in production environments.

---

## 1. 🖥️ Frontend Verification (React SPA / Vercel)
- [ ] Vercel deployment configuration (`client/vercel.json`) is present and valid.
- [ ] `VITE_API_URL` environment variable is set to the production Express Node Gateway URL.
- [ ] Build script (`npm run build`) compiles cleanly without bundle warnings.
- [ ] SPA routing fallback (`index.html`) functions on hard reloads across nested routes (`/dashboard`, `/chat`, `/workspace`).
- [ ] Theme toggle (Light / Dark mode) persists choice in `localStorage`.

---

## 2. ⚡ Backend Gateway Verification (Express / Render)
- [ ] Render configuration (`server/render.yaml`) is present and valid.
- [ ] Security headers (Helmet) return `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY`.
- [ ] CORS allowlist restricts credentials to trusted `CLIENT_URL`.
- [ ] Sliding-window rate limiter blocks abusive requests on `/api/v1/auth/*` and `/api/v1/chat`.
- [ ] Route versioning correctly serves `/api/v1/*` and exposes `/api/versions`.

---

## 3. 🐍 AI Microservice Verification (FastAPI / Render)
- [ ] Render configuration (`ai-service/render.yaml`) is present and valid.
- [ ] Uvicorn server launches with `uvloop` and `httptools` event loops.
- [ ] Environment validation (`validate_environment()`) confirms `GROQ_API_KEY` and `MONGODB_URI`.
- [ ] Swagger documentation loads interactively at `/docs` with example payloads.
- [ ] Health endpoints (`/health/live`, `/health/ready`, `/metrics`) return HTTP 200.

---

## 4. 🗄️ Database Verification (MongoDB Atlas)
- [ ] Database user credentials are configured with `readWrite` access to `cx_guardian_db`.
- [ ] Network Access IP allowlist permits connection from hosting platforms (`0.0.0.0/0`).
- [ ] Compound and unique indexes are verified (`conversation_id`, `message_id`, `email`).
- [ ] TTL index on `refresh_tokens.expires_at` is active for auto-expiration.

---

## 5. 🐳 Docker & Environment Verification
- [ ] `docker-compose.yml` builds all 4 containers (`client`, `server`, `ai-service`, `mongodb`) via `docker compose up --build`.
- [ ] Container healthchecks pass (`HEALTHCHECK` status: healthy).
- [ ] `.env.example` contains all required configuration keys without sensitive secrets.
