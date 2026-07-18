import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import cookieParser from 'cookie-parser';
import requestLogger from './middleware/requestLogger.js';
import errorHandler from './middleware/errorHandler.js';
import notFound from './middleware/notFound.js';
import responseFormatter from './middleware/responseFormatter.js';
import { CLIENT_URL } from './config/index.js';
import repositoryFactory from './repositories/repositoryFactory.js';

await repositoryFactory.initialize();
const { default: apiRouter } = await import('./routes/index.js');

const app = express();

// Security Middlewares
app.use(helmet());
app.use(cors({
  origin: CLIENT_URL,
  credentials: true
}));

// Performance & Parsing Middlewares
app.use(compression());
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(responseFormatter);

// Loggers
app.use(morgan('dev'));
app.use(requestLogger);

// Route Gateway Dispatcher
app.use('/api/v1', apiRouter);

// 404 Route Handler
app.use(notFound);

// Centralized Error Handler
app.use(errorHandler);

export default app;
