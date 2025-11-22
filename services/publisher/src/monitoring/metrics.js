/**
 * Prometheus metrics
 */

import promClient from 'prom-client';

const { Registry, Counter, Histogram, Gauge } = promClient;

export const promRegister = new Registry();

// Default metrics (CPU, memory, etc.)
promClient.collectDefaultMetrics({ register: promRegister });

// Custom metrics
export const emailsSentCounter = new Counter({
  name: 'publisher_emails_sent_total',
  help: 'Total number of emails sent successfully',
  registers: [promRegister],
});

export const emailFailuresCounter = new Counter({
  name: 'publisher_email_failures_total',
  help: 'Total number of email delivery failures',
  registers: [promRegister],
});

export const publicationsCounter = new Counter({
  name: 'publisher_publications_total',
  help: 'Total number of publications processed',
  labelNames: ['status'],
  registers: [promRegister],
});

export const rollbacksCounter = new Counter({
  name: 'publisher_rollbacks_total',
  help: 'Total number of publications rolled back',
  registers: [promRegister],
});

export const deliveryDurationHistogram = new Histogram({
  name: 'publisher_delivery_duration_seconds',
  help: 'Email delivery duration in seconds',
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
  registers: [promRegister],
});

export const queueSizeGauge = new Gauge({
  name: 'publisher_queue_size',
  help: 'Number of jobs in the publishing queue',
  registers: [promRegister],
});

// Middleware to track HTTP metrics
export function metricsMiddleware(req, res, next) {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    // Could add HTTP-specific metrics here
  });

  next();
}
