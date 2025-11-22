/**
 * NUJ Social Media Ethics Monitor - Publisher Service
 * Purpose: Email delivery with safety guardrails and rollback capability
 * Tech: Node.js + Express + Nodemailer + Bull
 */

import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { createServer } from 'http';
import { promRegister, metricsMiddleware } from './monitoring/metrics.js';
import { logger } from './utils/logger.js';
import { config } from './config/index.js';
import { initDatabase } from './database/index.js';
import { initQueue } from './queue/index.js';
import routes from './routes/index.js';
import { gracefulShutdown } from './utils/shutdown.js';

const app = express();
const server = createServer(app);

// Middleware
app.use(helmet());
app.use(cors({
  origin: config.corsOrigins,
  credentials: true,
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(metricsMiddleware);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'publisher',
    timestamp: new Date().toISOString(),
  });
});

// Metrics
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promRegister.contentType);
  res.end(await promRegister.metrics());
});

// Routes
app.use('/api', routes);

// Error handler
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined,
  });
});

// Initialize
async function start() {
  try {
    logger.info('Starting NUJ Publisher Service');

    // Initialize database
    await initDatabase();
    logger.info('Database initialized');

    // Initialize queue
    await initQueue();
    logger.info('Queue initialized');

    // Start server
    server.listen(config.port, '0.0.0.0', () => {
      logger.info(`Publisher service listening on port ${config.port}`);
    });

    // Graceful shutdown
    process.on('SIGTERM', () => gracefulShutdown(server));
    process.on('SIGINT', () => gracefulShutdown(server));

  } catch (error) {
    logger.error('Failed to start service:', error);
    process.exit(1);
  }
}

start();
