#  AI MicroService

Enterprise CX Guardian AI is a state-of-the-art real-time safety navigation and emergency response platform.

## Repository Structure
```text
 AI MicroService/
│
├── client/              # React frontend (Vite-powered)
├── server/              # Express backend (Modular MVC, Socket.IO & MongoDB)
├── ai-service/          # Python AI / ML service for safety insights
├── docs/                # Architecture diagrams, pitch deck, and design documents
├── docker-compose.yml   # Multi-container orchestration (Later)
├── README.md            # This file
└── .gitignore           # Root gitignore rules
```

## Features

### 🛡️ Real-time Location Tracking & Safety Navigation
- Browser geolocation with high accuracy fallback.
- Integration with Leaflet and OpenStreetMap.
- Real-time danger-zone analysis and warning alerts.
- Live navigation options sorted by Safety Score, ETA, and distance.

### 🚨 Emergency SOS & Guardian System
- One-tap SOS triggering.
- Auto-notifies trusted guardians via Twilio SMS.
- Integrated WebSocket rooms using Socket.IO for active guardian live tracking.
- DB logging of resolved and active emergencies.

### 👤 Secure Enterprise-grade Authentication
- JSON Web Token (JWT) stateless auth.
- Password hashing using bcrypt.
- Session persistence and secure client state context.

## Get Started

### Prerequisites
- Node.js >= 20
- MongoDB connection URI (Atlas or Local)
- Twilio account credentials (optional, for SMS notifications)

### Installation
1. Install dependencies for all workspaces from the root:
   ```bash
   npm install
   ```
2. Configure local environment variables:
   - Create `server/.env` (see `server/.env.example` for required variables).
   - Create `client/.env` (see `client/.env.example` for required variables).

### Running in Development
Start both the React client and Express server concurrently:
```bash
npm run dev
```

Or run them individually:
- Client only: `npm run dev:client`
- Server only: `npm run dev:server`
