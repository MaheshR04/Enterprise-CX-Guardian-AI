import mongoose from 'mongoose';
import { MONGO_URI, NODE_ENV } from '../config/index.js';

/**
 * Connect to MongoDB Atlas cluster with auto-reconnection settings.
 */
export const connectDatabase = async () => {
  try {
    const options = {
      autoIndex: NODE_ENV !== 'production',
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    };

    const conn = await mongoose.connect(MONGO_URI, options);
    console.log(`[Database] Connected successfully to host: ${conn.connection.host}`);
    return conn;
  } catch (error) {
    console.error(`[Database Error] Connection failed: ${error.message}`);
    if (NODE_ENV === 'production') {
      process.exit(1);
    }
  }
};

/**
 * Disconnect from MongoDB Atlas and release connection pool hooks.
 */
export const disconnectDatabase = async () => {
  try {
    if (mongoose.connection.readyState !== 0) {
      await mongoose.connection.close();
      console.log('[Database] MongoDB connection closed successfully.');
    }
  } catch (error) {
    console.error(`[Database Error] Disconnection failed: ${error.message}`);
    throw error;
  }
};
