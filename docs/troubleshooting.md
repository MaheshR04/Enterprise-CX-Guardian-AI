# Enterprise CX Guardian AI — Troubleshooting Guide

Common issues and resolution steps for development and production environments.

---

## 🔍 Issue 1: MongoDB Connection Refused / Timeout

### Symptoms
- FastAPI logs: `[MongoDB Warning] Connection to MongoDB unavailable`
- HTTP 503 `DB_UNAVAILABLE` error on conversation or user profile endpoints.

### Solution
1. **Local MongoDB**: Verify MongoDB service is running:
   ```bash
   # Windows Services or Docker
   docker ps | grep mongo
   ```
2. **MongoDB Atlas Connection String**: Ensure `MONGODB_URI` includes URL encoding for special characters in your password:
   ```env
   MONGODB_URI=mongodb+srv://user:pass%40word@cluster.mongodb.net/cx_guardian_db?retryWrites=true&w=majority
   ```
3. **Atlas Network Access**: Verify `0.0.0.0/0` is added to Atlas IP Access List.

---

## 🔍 Issue 2: Groq LLM API Key Error / Fallback Mode

### Symptoms
- Chat responses contain: `Groq AI Engine Response (Fallback): Evaluated message...`
- Log output: `Authentication failed: Invalid API Key`

### Solution
1. Verify `GROQ_API_KEY` is set in `.env` without extra quotes or spaces:
   ```env
   GROQ_API_KEY=gsk_abcdef1234567890...
   ```
2. Test your key with a direct curl request:
   ```bash
   curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer $GROQ_API_KEY"
   ```

---

## 🔍 Issue 3: CORS Policy Errors

### Symptoms
- Browser console error: `Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy.`

### Solution
1. In `development` mode (`ENVIRONMENT=development`), CORS permits all origins (`*`).
2. In `production` mode, ensure `CLIENT_URL` matches your deployed domain exactly:
   ```env
   CLIENT_URL=https://your-app.vercel.app
   ```

---

## 🔍 Issue 4: Docker Container Port Conflicts

### Symptoms
- Docker error: `Bind for 0.0.0.0:8000 failed: port is already allocated`.

### Solution
1. Identify and terminate the process occupying port 8000 or 5000:
   ```bash
   # Windows PowerShell
   Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
   ```
2. Or change port mapping in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"
   ```
