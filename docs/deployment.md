# Enterprise CX Guardian AI — Production Deployment Guide

This document provides step-by-step instructions for deploying Enterprise CX Guardian AI across cloud platforms:
- **Frontend (React/Vite SPA)** → Vercel
- **Node Backend Gateway** → Render
- **Python AI Microservice** → Render
- **Database Layer** → MongoDB Atlas

---

## 1. MongoDB Atlas Setup

1. Create a free/dedicated cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a Database User with `readWrite` permissions.
3. Under **Network Access**, add `0.0.0.0/0` (or Render outbound IPs) to the IP Access List.
4. Copy the connection string:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/cx_guardian_db?retryWrites=true&w=majority
   ```

---

## 2. Python AI Microservice → Render Deployment

1. Sign in to [Render](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository and set Root Directory to `ai-service`.
3. Set the following options:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --loop uvloop --http httptools`
4. Add Environment Variables:
   - `ENVIRONMENT` = `production`
   - `GROQ_API_KEY` = `gsk_your_groq_key`
   - `MONGODB_URI` = `mongodb+srv://...`
   - `JWT_SECRET_KEY` = `your_secure_64_char_key`
   - `DATABASE_NAME` = `cx_guardian_db`
5. Note the deployed URL (e.g. `https://cx-guardian-ai.onrender.com`).

---

## 3. Node.js Backend Gateway → Render Deployment

1. Create a second **Web Service** on Render with Root Directory set to `server`.
2. Options:
   - **Environment**: Node
   - **Build Command**: `npm ci`
   - **Start Command**: `node server.js`
3. Add Environment Variables:
   - `NODE_ENV` = `production`
   - `MONGO_URI` = `mongodb+srv://...`
   - `JWT_SECRET` = `your_secure_64_char_key` (must match AI Microservice)
   - `PYTHON_AI_URL` = `https://cx-guardian-ai.onrender.com`
   - `CLIENT_URL` = `https://cx-guardian.vercel.app`
4. Note the deployed URL (e.g. `https://cx-guardian-server.onrender.com`).

---

## 4. Frontend → Vercel Deployment

1. Sign in to [Vercel](https://vercel.com) and import your repository.
2. Set Framework Preset to **Vite** and Root Directory to `client`.
3. Add Environment Variables (baked at build time):
   - `VITE_API_URL` = `https://cx-guardian-server.onrender.com`
   - `VITE_SOCKET_URL` = `https://cx-guardian-server.onrender.com`
4. Deploy. Vercel will process `client/vercel.json` for SPA routing and asset caching.

---

## 5. Deployment Verification Checklist

- [ ] `GET /health` on Python AI service returns `200` with `healthy` status.
- [ ] `GET /api/v1/health` on Node backend returns `200`.
- [ ] `GET /api/versions` returns supported versions list.
- [ ] Chat interface successfully sends messages and renders Groq LLM responses.
- [ ] CORS policies accept requests from Vercel domain.
