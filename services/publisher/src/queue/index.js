/**
 * Queue management using Bull
 */

import Bull from 'bull';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';
import { emailService } from '../services/email.js';
import { SafetyGuardrails } from '../services/guardrails.js';
import { db } from '../database/index.js';

export let publishQueue;

export async function initQueue() {
  logger.info('Initializing job queue');

  publishQueue = new Bull('email-publishing', config.redis.url, {
    defaultJobOptions: {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000,
      },
      removeOnComplete: 100,
      removeOnFail: false,
    },
  });

  // Initialize email service
  await emailService.initialize();

  // Process jobs
  publishQueue.process(async (job) => {
    const { publicationId, testMode } = job.data;

    logger.info(`Processing publication job: ${publicationId}`);

    try {
      // Fetch publication
      const pubResult = await db.query(
        `SELECT gp.*, gd.title, gd.summary, gd.content_markdown
         FROM guidance_publications gp
         JOIN guidance_drafts gd ON gp.guidance_draft_id = gd.id
         WHERE gp.id = $1`,
        [publicationId]
      );

      if (pubResult.rows.length === 0) {
        throw new Error(`Publication ${publicationId} not found`);
      }

      const publication = pubResult.rows[0];

      // Safety guardrails check
      const safetyCheck = await SafetyGuardrails.checkBeforePublish(publication);

      if (!safetyCheck.safe) {
        logger.warn(`Safety check failed for ${publicationId}:`, safetyCheck.checks.failed);
        throw new Error(`Safety checks failed: ${JSON.stringify(safetyCheck.checks.failed)}`);
      }

      logger.info(`Safety checks passed (${safetyCheck.checks.passed.length} layers)`);

      // Get recipients
      const recipients = testMode
        ? config.safety.testGroupEmails.map((email, i) => ({ id: `test-${i}`, email }))
        : await getRecipients(publication);

      // Send emails
      const results = await emailService.sendGuidance({
        id: publicationId,
        guidance: {
          title: publication.title,
          summary: publication.summary,
          content_markdown: publication.content_markdown,
        },
        recipients,
      });

      // Update publication record
      await db.query(
        `UPDATE guidance_publications
         SET published_at = NOW(),
             successful_deliveries = $1,
             failed_deliveries = $2,
             recipients_count = $3,
             grace_period_ends_at = NOW() + INTERVAL '${config.safety.gracePeriodMinutes} minutes'
         WHERE id = $4`,
        [results.sent, results.failed, recipients.length, publicationId]
      );

      // Log delivery events
      for (const recipient of recipients) {
        await db.query(
          `INSERT INTO delivery_events (publication_id, event_type, recipient_hash, metadata)
           VALUES ($1, $2, $3, $4)`,
          [
            publicationId,
            'sent',
            hashEmail(recipient.email),
            JSON.stringify({ test_mode: testMode }),
          ]
        );
      }

      logger.info(`Publication ${publicationId} completed: ${results.sent}/${recipients.length} sent`);

      return {
        publicationId,
        sent: results.sent,
        failed: results.failed,
        total: recipients.length,
      };

    } catch (error) {
      logger.error(`Publication job failed:`, error);
      throw error;
    }
  });

  // Event handlers
  publishQueue.on('completed', (job, result) => {
    logger.info(`Job ${job.id} completed:`, result);
  });

  publishQueue.on('failed', (job, err) => {
    logger.error(`Job ${job.id} failed:`, err);
  });

  logger.info('Queue initialized');
}

async function getRecipients(publication) {
  // Fetch recipients based on segment
  if (!publication.segment_id) {
    return [];
  }

  const result = await db.query(
    `SELECT id, email FROM members
     WHERE segment_id = $1
     AND email_verified = true
     AND subscribed = true`,
    [publication.segment_id]
  );

  return result.rows;
}

function hashEmail(email) {
  // Simple hash for privacy
  const crypto = await import('crypto');
  return crypto.createHash('sha256').update(email).digest('hex');
}

export async function closeQueue() {
  if (publishQueue) {
    await publishQueue.close();
    logger.info('Queue closed');
  }
}
