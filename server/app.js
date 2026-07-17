const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();

// Middlewares
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check Route
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    message: 'Enterprise CX Guardian AI Server is healthy.',
    timestamp: new Date()
  });
});

// Main routing entry point
// Future routes:
// app.use('/api/auth', require('./routes/auth'));
// app.use('/api/emergencies', require('./routes/emergencies'));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: err.message || 'Internal Server Error'
  });
});

module.exports = app;
