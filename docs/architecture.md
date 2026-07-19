# Enterprise CX Guardian AI — Comprehensive System Architecture & Design Specification

This document contains full Mermaid architectural diagrams illustrating system topology, microservice communication, security authentication workflows, AI chat execution, RAG knowledge retrieval, database schemas, and monorepo structure.

---

## 1. System Architecture Diagram

```mermaid
flowchart TB
    subgraph ClientLayer ["Client Layer (Edge)"]
        UI["React 18 + Vite SPA\n(Port 80 / nginx)\n- Theme Provider\n- Toast Notifications\n- Skeleton Loaders"]
    end

    subgraph GatewayLayer ["Gateway & Node.js Backend"]
        NodeServer["Node.js Express Server\n(Port 5000)\n- Helmet & CORS Security\n- Sliding-Window Rate Limiter\n- Version Router (/api/v1, /api/v2)\n- Repository Factory"]
    end

    subgraph AIServiceLayer ["Python AI Microservice"]
        FastAPI["FastAPI App\n(Port 8000)\n- Groq AI LLM Engine\n- Sliding History Window\n- In-Memory ETag Cache\n- Metrics & System Health Collector"]
        RepoFactory["Repository Factory\n(Clean Architecture Storage Layer)"]
    end

    subgraph ExternalServices ["AI Model Infrastructure"]
        Groq["Groq Cloud API\n(llama3-70b-8192)\n- Sub-100ms Inference"]
    end

    subgraph PersistenceLayer ["Database & Caching"]
        MongoDB[("MongoDB 7.0 Cluster\n- conversations\n- messages\n- prompt_logs\n- ai_usage\n- users\n- refresh_tokens")]
    end

    UI -->|HTTPS / REST API| NodeServer
    NodeServer -->|Internal HTTP Proxy| FastAPI
    FastAPI -->|Motor Async Driver| MongoDB
    NodeServer -->|Mongoose / Native Driver| MongoDB
    FastAPI -->|Async HTTPS| Groq
    FastAPI --- RepoFactory
```

---

## 2. Microservice Flow Diagram

```mermaid
flowchart LR
    subgraph Frontend ["Edge Frontend"]
        SPA["React SPA"]
    end

    subgraph BackendGateway ["Express Node Gateway"]
        AuthMw["JWT Guard"]
        VRouter["Version Router (/api/v1)"]
        CacheMw["LRU ETag Cache"]
        ProxyModule["Axios AI Proxy"]
    end

    subgraph AIMicroservice ["FastAPI AI Service"]
        SecMw["Security & Rate Limiter"]
        PerfMw["GZip & ETag Middleware"]
        LLMEngine["Groq AIServiceManager"]
        RepoFactory["RepositoryFactory"]
    end

    subgraph Persistence ["MongoDB Storage"]
        Colls[("Conversations\nMessages\nPrompt Logs\nUsage Telemetry")]
    end

    SPA -->|1. Request| AuthMw
    AuthMw --> VRouter
    VRouter --> CacheMw
    CacheMw -->|Miss| ProxyModule
    ProxyModule -->|2. HTTP Proxy| SecMw
    SecMw --> PerfMw
    PerfMw --> LLMEngine
    LLMEngine --> RepoFactory
    RepoFactory -->|3. Persist / Fetch| Colls
    LLMEngine -->|4. Groq Inference| Groq[Groq LLaMA-3]
    Groq -->|5. Token Stream| LLMEngine
    LLMEngine -->|6. JSON Response| SPA
```

---

## 3. Authentication & JWT Authorization Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Client
    participant Express as Node Gateway (:5000)
    participant AuthService as AuthService
    participant UserRepo as UserRepository
    participant TokenRepo as RefreshTokenRepository
    participant DB as MongoDB

    Client->>Express: POST /api/v1/auth/login { email, password }
    Express->>AuthService: login_user(email, password)
    AuthService->>UserRepo: find_by_email(email)
    UserRepo->>DB: findOne({ email })
    DB-->>UserRepo: Return UserRecord
    AuthService->>AuthService: Verify bcrypt password hash
    AuthService->>AuthService: Issue Access JWT (60m) & Refresh JWT (7d)
    AuthService->>TokenRepo: save_refresh_token(hashedToken, userId)
    TokenRepo->>DB: insertOne({ token_hash, user_id, expires_at })
    AuthService-->>Express: Return { accessToken, refreshToken, user }
    Express-->>Client: HTTP 200 { success: true, tokens, user }

    Note over Client, Express: Subsequent Protected API Request
    Client->>Express: GET /api/v1/conversations (Header: Bearer <accessToken>)
    Express->>Express: Verify JWT Signature & Expiration
    Express-->>Client: Return Authorized Resource Payload
```

---

## 4. 10-Step AI Request & Chat Execution Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client as React Client
    participant Gateway as Express Gateway (:5000)
    participant FastAPI as FastAPI AI Microservice (:8000)
    participant ConvRepo as ConversationRepository
    participant MsgRepo as MessageRepository
    participant Groq as Groq AI (LLaMA-3)
    participant UsageRepo as UsageRepository

    Client->>Gateway: Step 1: Send User Message POST /api/v1/chat
    Gateway->>FastAPI: Step 2: Proxy Request to AI Microservice
    Note over FastAPI: Step 3: Security & Rate Limit Validation
    FastAPI->>ConvRepo: Step 4: Verify or Create Active Conversation
    ConvRepo-->>FastAPI: Conversation Header Object
    FastAPI->>MsgRepo: Step 5: Save Incoming User Message
    MsgRepo-->>FastAPI: Saved User Message ID
    FastAPI->>MsgRepo: Step 6: Fetch Last N Context Turns (MAX_HISTORY)
    MsgRepo-->>FastAPI: Conversation Context History
    FastAPI->>FastAPI: Step 7: Build System Prompt & Append History
    FastAPI->>Groq: Step 8: Call Groq LLM API (llama3-70b-8192)
    Groq-->>FastAPI: Return AI Reply + Token Usage (Prompt & Completion)
    FastAPI->>MsgRepo: Step 9: Save Assistant AI Response Message
    FastAPI->>UsageRepo: Step 10: Log Token Telemetry & Latency
    FastAPI-->>Gateway: HTTP 200 { reply, model, usage, processingTime }
    Gateway-->>Client: HTTP 200 { success: true, data: {...} }
```

---

## 5. RAG (Retrieval-Augmented Generation) Knowledge Flow Diagram

```mermaid
flowchart TD
    subgraph Ingestion ["1. Document Ingestion"]
        Doc["Uploaded Policy PDF / DOCX"] -->|Text Extraction| Chunks["Text Chunks\n(500 char windows)"]
        Chunks -->|Embeddings Engine| Vectors["Vector Embeddings\n(1536-dim)"]
        Vectors -->|Index| VectorStore[("In-Memory LRU Vector Store / MongoDB")]
    end

    subgraph QueryExecution ["2. Query Retrieval & Context Injection"]
        UserMsg["User Message"] -->|Query Vectorizer| QueryVec["Query Embedding"]
        QueryVec -->|Cosine Similarity Search| TopK["Top-K Matching Chunks\n(Threshold > 0.75)"]
        TopK --> ContextBlock["Formatted Context Block"]
        ContextBlock --> PromptBuilder["System Prompt Builder"]
        PromptBuilder --> LLM["Groq LLaMA-3 Inference"]
        LLM --> Response["Ground Truth AI Response"]
    end
```

---

## 6. Database ER Diagram (MongoDB Collections & Relationships)

```mermaid
erDiagram
    CONVERSATION ||--o{ MESSAGE : contains
    CONVERSATION ||--o{ PROMPT_LOG : audit_trail
    CONVERSATION ||--o{ AI_USAGE : tracks_telemetry
    USER ||--o{ REFRESH_TOKEN : owns

    CONVERSATION {
        string _id PK
        string conversation_id UK "Unique Session Identifier"
        string status "ACTIVE | ARCHIVED | DELETED"
        date created_at
        date updated_at
    }

    MESSAGE {
        string _id PK
        string message_id UK
        string conversation_id FK
        string sender "user | assistant | system"
        string text "Message content payload"
        date timestamp
    }

    PROMPT_LOG {
        string _id PK
        string conversation_id FK
        string system_prompt
        string full_prompt_text
        date created_at
    }

    AI_USAGE {
        string _id PK
        string conversation_id FK
        string model "llama3-70b-8192"
        int prompt_tokens
        int completion_tokens
        int total_tokens
        float latency_ms
        date timestamp
    }

    USER {
        string _id PK
        string email UK
        string password_hash
        string role "ADMIN | SUPERVISOR | AGENT"
        string status "ACTIVE | INACTIVE"
        date created_at
    }

    REFRESH_TOKEN {
        string _id PK
        string token_hash UK
        string user_id FK
        date expires_at "TTL Index: Auto-expiring"
    }
```

---

## 7. Monorepo Folder Structure Diagram

```mermaid
graph TD
    Root["AI-MicroService (Root)"]

    subgraph ClientDir ["client/ (React 18 + Vite SPA)"]
        ClientSrc["src/ (Components, Context, Pages, Hooks)"]
        ClientDocker["Dockerfile & nginx.conf"]
    end

    subgraph ServerDir ["server/ (Node.js Express Backend)"]
        ServerRoutes["routes/ (v1/, versionRouter.js)"]
        ServerControllers["controllers/"]
        ServerServices["services/"]
        ServerRepos["repositories/ (interfaces.js, inMemory/, mongodb/)"]
        ServerMiddleware["middleware/ (security.js, performance.js)"]
        ServerSeed["seed/ (seed.js)"]
    end

    subgraph AIServiceDir ["ai-service/ (FastAPI Python AI Service)"]
        AppMain["app/main.py (Lifespan & Middleware Stack)"]
        AppRouters["app/routers/ (health, chat, conversation, dashboard, versions/)"]
        AppServices["app/services/ (ai_service.py, auth_service.py)"]
        AppRepos["app/repositories/ (interfaces.py, factory.py, mongodb.py)"]
        AppMiddleware["app/middleware/ (security.py, performance.py, logging.py)"]
        AppCore["app/core/ (config.py, logger.py, metrics.py)"]
    end

    subgraph OpsDir ["Deployment & Ops"]
        DockerCompose["docker-compose.yml"]
        MongoInit["docker/mongo-init.js"]
        GithubCI[".github/workflows/ci.yml"]
        Docs["docs/ (architecture.md, deployment.md)"]
    end

    Root --> ClientDir
    Root --> ServerDir
    Root --> AIServiceDir
    Root --> OpsDir
```
