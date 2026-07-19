# Enterprise CX Guardian AI — Environment Setup Guide

This guide walks you through setting up a complete local development environment for Enterprise CX Guardian AI.

---

## 📋 Prerequisites

Ensure you have the following installed on your system:
- **Git** >= 2.30
- **Node.js** >= 20.x & **npm** >= 10.x
- **Python** >= 3.11
- **Docker Desktop** >= 24.0 (Optional, recommended)
- **MongoDB** >= 7.0 (Local instance or free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster)

---

## 🛠️ Step 1: Environment Variables Configuration

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Configure key variables:
```env
ENVIRONMENT=development
GROQ_API_KEY=gsk_your_groq_api_key_here
MONGODB_URI=mongodb://localhost:27017/cx_guardian_db
JWT_SECRET_KEY=dev_secret_key_32_characters_long_minimum
MODEL_NAME=llama3-70b-8192
MAX_HISTORY=10
```

---

## 🐳 Option A: One-Command Docker Setup (Recommended)

To spin up all microservices (Client, Express Gateway, FastAPI AI Microservice, and MongoDB with pre-seeded demo data):

```bash
docker compose up --build
```

Access services:
- **React Frontend**: `http://localhost:80`
- **Node Gateway**: `http://localhost:5000`
- **FastAPI Microservice**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

## 💻 Option B: Standalone Local Setup

### 1. Python AI Microservice (`ai-service/`)

```bash
cd ai-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Node.js Express Backend Gateway (`server/`)

```bash
cd server

# Install dependencies
npm ci

# Seed demo data into MongoDB (Optional)
node seed/seed.js

# Start server in dev mode
npm run dev
```

### 3. React SPA Frontend (`client/`)

```bash
cd client

# Install dependencies
npm ci

# Start Vite dev server
npm run dev
```

---

## 🧪 Step 3: Run Test Suites

```bash
# Test FastAPI AI Microservice
cd ai-service && pytest

# Test Node Express Gateway
cd server && npm test
```
