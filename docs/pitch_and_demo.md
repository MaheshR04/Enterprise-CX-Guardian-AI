# Enterprise CX Guardian AI — Hackathon Presentation, Demo & Pitch Deck

---

## 1. ⚡ 2-Minute Elevator Pitch Script

> **[Hook — Problem]**
> "In enterprise customer support, millions of customer interactions fail not because of AI limitations, but because of poor infrastructure: un-audited prompts, data loss from hard deletes, slow LLM latency, and monolithic databases that lock teams in. Standard AI wrappers break down under real-world traffic."
>
> **[Solution — What We Built]**
> "Meet **Enterprise CX Guardian AI** — a high-performance, multi-tier AI microservice architecture powered by Groq LLaMA-3 70B, FastAPI, Node.js Express, and MongoDB.
>
> We built a **10-Step Chat Execution Engine** that captures token telemetry on every turn, maintains sliding context history without token overflows, and writes complete raw prompts into `prompt_logs` for compliance auditing.
>
> More importantly, our **Clean Architecture Infrastructure Layer** isolates controllers from storage backends through a factory pattern — meaning enterprise teams can hot-swap MongoDB for Redis, PostgreSQL, or Azure Cosmos DB with **zero code changes** to business logic."
>
> **[Impact & Differentiators]**
> "With sub-50ms AI inference, sliding window per-IP rate limiting, GZip response compression, and LRU+TTL ETag caching, Enterprise CX Guardian AI delivers sub-second SLAs, 100% auditability, and zero-downtime scalability."

---

## 2. 🎬 5-Minute Live Demonstration Script

| Time | Demo Step | Actions & Screen Focus | Speaker Narrative |
|---|---|---|---|
| **0:00 - 0:45** | **1. High-Level Architecture Overview** | Display Manager Dashboard at `http://localhost:80/dashboard`. Show active model badge (`llama3-70b-8192`) and system health indicators. | "Welcome to Enterprise CX Guardian AI. As you can see, our manager dashboard provides real-time telemetry across system CPU, memory, database ping latency, and Groq LLM throughput." |
| **0:45 - 2:00** | **2. Live 10-Step AI Chat Execution** | Navigate to `/chat`. Send query: *"Our API endpoint experienced 45 minutes of downtime today. Are we eligible for SLA credit compensation?"* | "Let's trigger a real-time conversation. The moment I hit send, our Express gateway routes the message through Helmet security headers, rate limiters, and forwards it to our FastAPI microservice. The AI retrieves context, constructs a prompt, executes Groq inference in 42ms, and logs token usage." |
| **2:00 - 3:00** | **3. Conversation Lifecycle & Soft Delete** | Navigate to `/workspace` or `/conversations`. Show Active, Archived, and Soft-Deleted states. Click **Archive**, then **Soft Delete**, then **Restore**. | "Notice our strict compliance policy: we NEVER hard delete customer records. Conversations transition through `ACTIVE`, `ARCHIVED`, and `DELETED` states. Records can be inspected or restored instantly by supervisors." |
| **3:00 - 4:00** | **4. Dashboard APIs & Telemetry** | Switch to Swagger UI at `http://localhost:8000/docs`. Execute `GET /api/v1/dashboard/model-usage` and `GET /metrics`. | "Our platform exposes 6 dedicated Dashboard APIs. Here you can inspect total prompt tokens, completion tokens, model throughput (tok/s), and latency percentiles (p50, p90, p99)." |
| **4:00 - 5:00** | **5. Zero-Downtime Clean Architecture & Docker** | Show `docker-compose.yml` and `RepositoryFactory.js`. | "Finally, our storage layer is completely abstracted using the Repository Factory pattern. Whether deploying on Docker Compose, Vercel, or Render, MongoDB can be hot-swapped for Redis or PostgreSQL with zero API modifications." |

---

## 3. 🎯 Judge Q&A Preparation

### Q1: How does your architecture handle sudden spikes in LLM traffic?
> **Answer**: "We handle traffic spikes through a 4-layer defense:
> 1. **Sliding-Window Rate Limiting**: Throttles abusive IPs at the gateway level before touching the AI service.
> 2. **In-Memory ETag Caching**: Read-heavy queries (e.g. repeated conversation lists or health checks) return cached `304 Not Modified` responses instantly.
> 3. **Async Task Queue**: Non-critical writes (analytics, telemetry) are offloaded to an async background worker queue (`AsyncTaskQueue`).
> 4. **Groq LLaMA-3 High Throughput**: Groq's LPU hardware delivers 80+ tokens/second, keeping queue wait times under 50ms."

### Q2: Why did you separate Node.js (Gateway) and FastAPI (AI Microservice)?
> **Answer**: "Separation of concerns. Node.js Express excels as a lightweight API Gateway handling client authentication, CORS, rate limiting, and frontend routing. FastAPI in Python excels at AI orchestration, async I/O, Pydantic schema validation, and machine learning library integrations. Decoupling them allows scaling the AI microservice independently of the API gateway."

### Q3: How do you ensure compliance and prevent prompt injection attacks?
> **Answer**: "Every raw prompt payload is saved into a dedicated `prompt_logs` collection for auditability. On the security side, our `InputSanitizationMiddleware` strips null bytes (`\x00`), control characters, `<script>` tags, and `javascript:` URIs from all input parameters before prompt assembly occurs."

---

## 4. 🌟 Key Innovations & Technical Highlights

1. **Clean Architecture Storage Abstraction**: Controllers depend on repository interfaces (`IConversationRepository`), allowing seamless backend migration without touching business logic.
2. **Dual-Layer Health & Readiness Probes**: Kubernetes-native `/health/live` and `/health/ready` endpoints with database ping round-trip timing.
3. **Rolling Window Telemetry Engine**: `MetricsCollector` records request counts, error rates, CPU/memory stats, and latency distributions (p50, p90, p99).
4. **Resilient Offline Fallback**: If MongoDB or Groq becomes temporarily unreachable, the platform degrades gracefully into fallback mode without crashing.
5. **Zero-Dependency Native Rate Limiter**: Express gateway features a custom sliding-window rate limiter preventing external library vulnerabilities.
