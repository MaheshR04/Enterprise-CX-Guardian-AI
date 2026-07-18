import http from 'http';
import app from './app.js';
import { Server } from 'socket.io';
import * as config from './config/index.js';
import { connectDatabase, disconnectDatabase } from './database/connection.js';

const usesMongoStorage = config.STORAGE_BACKEND.toLowerCase() === 'mongodb';

if (usesMongoStorage) {
  await connectDatabase();
} else {
  console.log(`[Database] Skipping MongoDB connection for storage backend: ${config.STORAGE_BACKEND}`);
}

// Create HTTP server
const server = http.createServer(app);

// Initialize Socket.IO with CORS
const io = new Server(server, {
  cors: {
    origin: config.CLIENT_URL,
    methods: ['GET', 'POST'],
    credentials: true
  }
});

// Socket connection handler
io.on('connection', (socket) => {
  console.log(`[Socket] User connected: ${socket.id}`);
  socket.on('disconnect', () => {
    console.log(`[Socket] User disconnected: ${socket.id}`);
  });
});

// Start Server
server.listen(config.PORT, () => {
  console.log(`[Server] running in ${config.NODE_ENV} mode on port ${config.PORT}`);
});

// GRACEFUL SHUTDOWN HANDLER
const handleShutdown = (signal) => {
  console.log(`[Server] Received ${signal}. Initiating graceful shutdown...`);

  // Close HTTP server
  server.close(async () => {
    console.log('[Server] HTTP and Socket.IO servers closed.');
    
    try {
      if (usesMongoStorage) {
        await disconnectDatabase();
      }
      console.log('[Server] Graceful shutdown completed. Exiting.');
      process.exit(0);
    } catch (err) {
      console.error(`[Shutdown Error] Failed during database closure: ${err.message}`);
      process.exit(1);
    }
  });

  // Force close after 10s timeout
  setTimeout(() => {
    console.error('[Server] Shutdown timed out. Forcing exit.');
    process.exit(1);
  }, 10000);
};

// Listen to system signals
process.on('SIGTERM', () => handleShutdown('SIGTERM'));
process.on('SIGINT', () => handleShutdown('SIGINT'));
