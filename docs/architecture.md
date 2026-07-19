# Enterprise CX Guardian AI — System Architecture & Design Documentation

## 1. High-Level System Architecture Diagram

```mermaid
flowchart TB
    subgraph ClientLayer ["Client Layer (Edge)"]
        UI["React + Vite Single Page App\n(Port 80 / nginx)"]
    end

    subgraph GatewayLayer ["Gateway & Node.js Backend"]
        NodeServer["Node.js Express Server\n(Port 5000)\n- Auth Guard\n- Rate Limiter\n- Repository Factory"]
    end

    subgraph AIServiceLayer ["Python AI Microservice"]
        FastAPI["FastAPI App\n(Port 8000)\n- Groq AI Engine\n- Sliding Context Window\n- Metrics & Health Collector"]
        RepoFactory["Repository Factory\n(Clean Architecture Interface)"]
    end

    subgraph ExternalServices ["AI Model Infrastructure"]
        Groq["Groq Cloud API\n(llama3-70b-8192)"]
    end

    subgraph DataStore ["Persistence Layer"]
        MongoDB[("MongoDB 7.0 Cluster\n- conversations\n- messages\n- prompt_logs\n- ai_usage")]
    end

    UI -->|HTTPS / REST API| NodeServer
    NodeServer -->|Internal HTTP Proxy| FastAPI
    FastAPI -->|Motor Async Driver| MongoDB
    NodeServer -->|Mongoose / Driver| MongoDB
    FastAPI -->|Async HTTPS| Groq
    FastAPI --- RepoFactory
```

---

## 2. End-to-End Chat Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client as React SPA (Client)
    participant Server as Node.js Backend (:5000)
    participant AISvc as FastAPI AI Microservice (:8000)
    participant Repo as Repository Layer
    participant Mongo as MongoDB Atlas
    participant Groq as Groq AI (LLaMA-3)

    User->>Client: Submit message ("How do I reset my password?")
    Client->>Server: POST /api/v1/chat { conversationId, message }
    Note over Server: Security Check: Rate Limit, Cors & Body Validation
    Server->>AISvc: Proxy POST /api/v1/chat with JWT & Payload
    Note over AISvc: Middleware: Sanitize input & record request start
    AISvc->>Repo: Get Conversation History (Last N turns)
    Repo->>Mongo: find({ conversation_id, status: "ACTIVE" })
    Mongo-->>Repo: Return message history
    Repo-->>AISvc: Formatted context messages
    AISvc->>AISvc: Build System Prompt & Append History
    AISvc->>Groq: POST /chat/completions (llama3-70b-8192)
    Groq-->>AISvc: Return AI Response + Token Usage
    AISvc->>Repo: Persist User Msg, Assistant Msg & AI Usage Telemetry
    Repo->>Mongo: bulkWrite([insert user, insert assistant, insert usage])
    Mongo-->>Repo: Acknowledge Write
    AISvc-->>Server: JSON { reply, model, usage, processingTime }
    Server-->>Client: HTTP 200 { success: true, data: {...} }
    Client-->>User: Render AI Response in Chat UI
```

---

## 3. Monorepo Folder Structure Diagram

```mermaid
graph TD
    Root["AI-MicroService (Root)"]
    
    subgraph ClientDir ["client/ (React + Vite SPA)"]
        ClientSrc["src/ (Components, Hooks, Services)"]
        ClientDocker["Dockerfile & nginx.conf"]
    end

    subgraph ServerDir ["server/ (Node.js Express Backend)"]
        ServerRoutes["routes/ (v1/, versionRouter.js)"]
        ServerControllers["controllers/"]
        ServerServices["services/"]
        ServerRepos["repositories/ (interfaces.js, inMemory/, mongodb/)"]
        ServerMiddleware["middleware/ (security.js, performance.js)"]
    end

    subgraph AIServiceDir ["ai-service/ (FastAPI Python AI Service)"]
        AppMain["app/main.py (Lifespan & Middleware)"]
        AppRouters["app/routers/ (health, chat, conversation, dashboard, versions/)"]
        AppServices["app/services/ (ai_service.py, memory_service.py)"]
        AppRepos["app/repositories/ (interfaces.py, factory.py, mongodb.py)"]
        AppMiddleware["app/middleware/ (security.py, performance.py, logging.py)"]
        AppCore["app/core/ (config.py, logger.py, metrics.py)"]
    end

    subgraph DeployDir ["Deployment & Ops"]
        DockerCompose["docker-compose.yml"]
        GithubCI[".github/workflows/ci.yml"]
        EnvExample[".env.example"]
    end

    Root --> ClientDir
    Root --> ServerDir
    Root --> AIServiceDir
    Root --> DeployDir
```

---

## 4. Database ER Diagram (MongoDB Collections)

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
        string role "Admin | Supervisor | Agent"
        string status "ACTIVE | INACTIVE"
        date created_at
    }

    REFRESH_TOKEN {
        string _id PK
        string token UK
        string user_id FK
        date expires_at "TTL Index: Auto-expiring"
    }
```

---

## 5. Microservice Flow Architecture

```mermaid
flowchart LR
    subgraph Client ["Frontend Edge"]
        SPA["React SPA"]
    end

    subgraph Backend ["Express Node Gateway"]
        Auth["JWT Auth Middleware"]
        VRouter["Version Router (/api/v1)"]
        Cache["LRU Cache Layer"]
        Proxy["Axios AI Proxy"]
    end

    subgraph AIService ["FastAPI Microservice"]
        SecMw["Security & Rate Limiter"]
        PerfMw["GZip & ETag Middleware"]
        LLMEngine["Groq AIServiceManager"]
        Factory["RepositoryFactory"]
    end

    subgraph DB ["MongoDB Cluster"]
        Colls[("Conversations\nMessages\nPrompt Logs\nUsage")]
    end

    SPA -->|1. Request| Auth
    Auth --> VRouter
    VRouter --> Cache
    Cache -->|Miss| Proxy
    Proxy -->|2. HTTP Proxy| SecMw
    SecMw --> PerfMw
    PerfMw --> LLMEngine
    LLMEngine --> Factory
    Factory -->|3. Persist / Fetch| DB
    LLMEngine -->|4. Groq Inference| Groq[Groq LLaMA-3]
    Groq -->|5. Token Stream| LLMEngine
    LLMEngine -->|6. JSON Response| SPA
```
