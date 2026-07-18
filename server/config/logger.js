import winston from 'winston';
import path from 'path';
import { fileURLToPath } from 'url';
import * as env from './env.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white'
};

winston.addColors(colors);

const getLogLevel = () => {
  if (env.NODE_ENV === 'development') return 'debug';
  return 'info';
};

// Standardized file logging format
const fileLogFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// Standard console log format with colors
const consoleLogFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(
    (info) => `[${info.timestamp}] [${info.level}]: ${info.message}`
  )
);

const transports = [
  // Console transport
  new winston.transports.Console({
    level: getLogLevel(),
    format: consoleLogFormat
  }),
  
  // Error File transport (logs/error.log)
  new winston.transports.File({
    filename: path.join(__dirname, '../logs/error.log'),
    level: 'error',
    format: fileLogFormat
  }),
  
  // Combined File transport (logs/combined.log)
  new winston.transports.File({
    filename: path.join(__dirname, '../logs/combined.log'),
    level: 'debug',
    format: fileLogFormat
  })
];

const logger = winston.createLogger({
  level: getLogLevel(),
  levels,
  transports
});

export default logger;
