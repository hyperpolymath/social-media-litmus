/**
 * Configuration management
 */

import dotenv from 'dotenv';

dotenv.config();

export const config = {
  // Service
  port: parseInt(process.env.PUBLISHER_PORT || '3003', 10),
  nodeEnv: process.env.NODE_ENV || 'production',
  logLevel: process.env.LOG_LEVEL || 'info',

  // Database
  database: {
    host: process.env.DB_HOST || 'postgres',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    name: process.env.DB_NAME || 'nuj_monitor',
    user: process.env.DB_USER || process.env.POSTGRES_USER,
    password: process.env.DB_PASSWORD || process.env.POSTGRES_PASSWORD,
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://redis:6379/3',
  },

  // Email (SMTP)
  email: {
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT || '587', 10),
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASSWORD,
    },
    from: process.env.SMTP_FROM || 'monitor@nuj.org.uk',
  },

  // Safety guardrails
  safety: {
    approvalRequired: process.env.APPROVAL_REQUIRED !== 'false',
    gracePeriodMinutes: parseInt(process.env.GRACE_PERIOD_MINUTES || '5', 10),
    testGroupEmails: (process.env.TEST_GROUP_EMAILS || '').split(',').filter(Boolean),
    enableRollback: process.env.ENABLE_ROLLBACK !== 'false',
  },

  // CORS
  corsOrigins: process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(',')
    : ['http://localhost:4000'],
};
