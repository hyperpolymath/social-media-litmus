/**
 * Graceful shutdown handler
 */

import { logger } from './logger.js';
import { closeDatabase } from '../database/index.js';
import { closeQueue } from '../queue/index.js';

export async function gracefulShutdown(server) {
  logger.info('Received shutdown signal');

  // Stop accepting new connections
  server.close(async () => {
    logger.info('HTTP server closed');

    try {
      // Close queue
      await closeQueue();

      // Close database
      await closeDatabase();

      logger.info('Graceful shutdown complete');
      process.exit(0);

    } catch (error) {
      logger.error('Error during shutdown:', error);
      process.exit(1);
    }
  });

  // Force shutdown after 30 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
}
