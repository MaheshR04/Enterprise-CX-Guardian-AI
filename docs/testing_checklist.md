# Enterprise CX Guardian AI — Master Testing Checklist

Coverage across Authentication, Conversation Lifecycle, RAG Retrieval, Tool Calling, Analytics, Dashboard, and Deployment.

---

## 1. 🔑 Authentication & Authorization Test Cases
- [ ] **Registration**: `POST /api/v1/auth/register` creates user record, hashes password with bcrypt, returns JWT token pair.
- [ ] **Password Strength Guard**: Registration fails on weak passwords (< 8 chars, missing uppercase, digit, or special char).
- [ ] **Login**: `POST /api/v1/auth/login` validates credentials and returns access & refresh tokens.
- [ ] **Token Refresh**: `POST /api/v1/auth/refresh` revokes old refresh token hash and issues new token pair.
- [ ] **Logout**: `POST /api/v1/auth/logout` invalidates refresh token hash in database.
- [ ] **RBAC Guard**: Restricted routes return HTTP 403 `Forbidden` when accessed by insufficient roles.

---

## 2. 💬 Conversation Lifecycle & Chat Test Cases
- [ ] **Chat Execution**: `POST /api/v1/chat` runs 10-step flow, returns AI completion, and saves user/assistant messages.
- [ ] **Sliding Window Context**: Prompt assembly bounds history to `MAX_HISTORY` turns to prevent context length overflows.
- [ ] **Prompt Auditing**: Raw prompt payloads are saved into `prompt_logs` collection.
- [ ] **Token Telemetry**: Token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`) is logged into `ai_usage`.
- [ ] **Soft Delete**: `DELETE /api/v1/conversations/{id}` updates status to `DELETED` without deleting MongoDB document.
- [ ] **Archive & Restore**: `PATCH /conversations/{id}/archive` and `/restore` correctly toggle between `ARCHIVED` and `ACTIVE`.

---

## 3. 📚 RAG & Document Analytics Test Cases
- [ ] **Document Indexing**: Uploaded knowledge base documents are chunked and indexed.
- [ ] **Context Injection**: Relevant document chunks are injected into system prompt when similarity threshold > 0.75.
- [ ] **Document Dashboard**: `GET /api/v1/dashboard/documents` returns document counts, chunk counts, and retrieval hit rates.

---

## 4. 🧰 AI Tool Calling Test Cases
- [ ] **Reasoning Engine**: `POST /api/v1/reasoning` analyzes issue description, returns root cause & confidence score.
- [ ] **Sentiment Analyzer**: `POST /api/v1/sentiment` classifies customer text polarity (Positive, Negative, Mixed) & emotions.
- [ ] **Recommendation Tool**: `POST /api/v1/recommendation` evaluates customer tier & tenure to recommend SLA credits.

---

## 5. 📊 Dashboard & Metrics Test Cases
- [ ] `GET /api/v1/dashboard/summary` — Returns top-level aggregated KPIs.
- [ ] `GET /api/v1/dashboard/health` — Returns process CPU %, memory MB, and DB latency.
- [ ] `GET /api/v1/dashboard/model-usage` — Returns total LLM calls, token breakdown, and tok/s throughput.
- [ ] `GET /metrics` — Returns p50, p90, p99 latency percentiles and error rates.
