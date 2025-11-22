/**
 * Database connection using node-postgres
 */

import pg from 'pg';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';

const { Pool } = pg;

export let db;

export async function initDatabase() {
  logger.info('Initializing database connection');

  db = new Pool({
    host: config.database.host,
    port: config.database.port,
    database: config.database.name,
    user: config.database.user,
    password: config.database.password,
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  });

  // Test connection
  try {
    const client = await db.connect();
    await client.query('SELECT NOW()');
    client.release();
    logger.info('Database connection established');
  } catch (error) {
    logger.error('Database connection failed:', error);
    throw error;
  }

  // Handle errors
  db.on('error', (err) => {
    logger.error('Unexpected database error:', err);
  });
}

export async function closeDatabase() {
  if (db) {
    await db.end();
    logger.info('Database connection closed');
  }
}
