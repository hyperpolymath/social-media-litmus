/**
 * Structured logging with Winston
 */

import winston from 'winston';
import { config } from '../config/index.js';

const { combine, timestamp, json, errors } = winston.format;

export const logger = winston.createLogger({
  level: config.logLevel,
  format: combine(
    errors({ stack: true }),
    timestamp(),
    json()
  ),
  defaultMeta: {
    service: 'publisher',
  },
  transports: [
    new winston.transports.Console(),
  ],
});

// In development, also log to file
if (config.nodeEnv === 'development') {
  logger.add(
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
    })
  );
  logger.add(
    new winston.transports.File({
      filename: 'logs/combined.log',
    })
  );
}
