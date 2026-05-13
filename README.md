# GuardianPath AI

GuardianPath AI is an AI-powered real-time safety navigation and emergency response MVP. This repository is organized as a two-app workspace:

- `frontend`: React + Vite + Tailwind CSS client
- `server`: Node.js + Express + MongoDB + Socket.IO API

## Step 1 Features

- React + Vite frontend scaffold
- Express backend scaffold using MVC-style folders
- MongoDB Atlas connection helper
- Environment variable examples for frontend and backend
- API health route for frontend/backend connectivity
- Socket.IO server bootstrap for later live tracking features
- Tailwind CSS and responsive starter UI
- Root scripts for running frontend and backend together

## Step 2 Features

- User signup and login
- Password hashing with bcrypt
- JWT token creation and validation
- Protected `/dashboard` route
- Authenticated `/api/auth/me` endpoint
- Trusted guardian contact storage
- Logout from the frontend session

## Step 3 Features

- Leaflet + OpenStreetMap dashboard map
- Browser geolocation with `watchPosition`
- Current-location marker with auto-center
- Live latitude, longitude, accuracy, and timestamp updates
- Manual pause/start tracking control
- Responsive map and coordinate panel

## Step 4 Features

- JWT-authenticated Socket.IO connections
- Live coordinate emit every few seconds from the dashboard
- Backend `location-update` handling and MongoDB `currentLocation` updates
- Connected users snapshot
- Private user and guardian rooms
- Socket handlers for `danger-alert`, `sos-alert`, `guardian-joined`, and user disconnects

## Installation

```bash
npm install
```

On this Windows machine, if PowerShell blocks `npm`, use:

```bash
npm.cmd install
npm.cmd run dev
```

## Environment Setup

Create local env files from the examples:

```bash
copy server\.env.example server\.env
copy frontend\.env.example frontend\.env
```

The local `server/.env` file stores your MongoDB Atlas URI and development secrets. Do not commit `.env` files.

The map uses OpenStreetMap tiles through Leaflet, so no billing account or map token is required.
Location access works on `localhost` during development. In production, browser geolocation requires HTTPS.

## Run Commands

Run both apps in development mode:

```bash
npm run dev
```

Use this while building the MVP. `npm run build` is only for creating the production frontend bundle.

Run only the backend:

```bash
npm run dev:backend
```

Run only the frontend:

```bash
npm run dev:frontend
```

Default URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- Health API: `http://localhost:5000/api/health`

## API Routes

```text
POST /api/auth/signup
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
PUT  /api/auth/guardian-contacts
GET  /api/health
```

## Socket Events

```text
user-connected
connected-users
location-update
guardian-joined
danger-alert
sos-alert
user-disconnected
disconnect
```

## Project Structure

```text
GuardianPath-AI/
  frontend/
    src/
      components/
      context/
      hooks/
      pages/
      services/
      sockets/
      utils/
  server/
    config/
    controllers/
    middleware/
    models/
    routes/
    services/
    sockets/
    utils/
```

## Next Step

Step 5 will add safe route generation and safety scoring.
"# GuardianPath-AI" 
