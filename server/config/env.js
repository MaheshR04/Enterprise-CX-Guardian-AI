import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

const requiredEnv = ['MONGO_URI', 'JWT_SECRET', 'PYTHON_AI_URL'];
const missingEnv = [];

for (const envName of requiredEnv) {
  if (!process.env[envName]) {
    missingEnv.push(envName);
  }
}

if (missingEnv.length > 0) {
  const errorMessage = `[Config Error] Missing required environment variables: ${missingEnv.join(', ')}`;
  if (process.env.NODE_ENV === 'production') {
    throw new Error(errorMessage);
  } else {
    console.warn(`[WARNING] ${errorMessage}. Applying development fallback configurations.`);
  }
}

export const PORT = process.env.PORT || 5000;
export const NODE_ENV = process.env.NODE_ENV || 'development';
export const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/cx_guardian_db';
export const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkeychangeinproduction';
export const PYTHON_AI_URL = process.env.PYTHON_AI_URL || 'http://localhost:8000';
export const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5173';
