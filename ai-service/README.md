# Enterprise CX Guardian AI - Microservice

> **"An AI-powered Autonomous Customer Experience Agent."**

This service is a completely independent microservice running on Python FastAPI. It communicates with the Node.js backend exclusively through REST APIs.

---

## 🛠️ Technology Stack

- **Python 3.12+**
- **FastAPI**: Modern, fast web framework for building APIs with Python.
- **Uvicorn**: Lightning-fast ASGI server implementation.
- **Pydantic**: Data validation and settings management using Python type hints.
- **Python-dotenv**: Environment configuration parser.
- **HTTPX**: Next-generation HTTP client for async requests.
- **Groq SDK**: High-performance LLM inference platform integration.
- **Logging**: Structured logger for tracking operational metrics.

---

## 🚀 Running the Microservice

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. **Launch Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Verify API Health**:
   Navigate to `http://localhost:8000/` or inspect the interactive Swagger documentation at `http://localhost:8000/docs`.
