/**
 * API routes
 */

import express from 'express';
import { body, param, validationResult } from 'express-validator';
import { publishQueue } from '../queue/index.js';
import { db } from '../database/index.js';
import { logger } from '../utils/logger.js';
import { SafetyGuardrails } from '../services/guardrails.js';

const router = express.Router();

// Validation middleware
const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

/**
 * Schedule publication
 */
router.post(
  '/publications/schedule',
  [
    body('guidance_draft_id').isUUID(),
    body('segment_id').optional().isUUID(),
    body('scheduled_for').isISO8601(),
    body('test_mode').optional().isBoolean(),
  ],
  validate,
  async (req, res) => {
    try {
      const { guidance_draft_id, segment_id, scheduled_for, test_mode } = req.body;

      // Create publication record
      const result = await db.query(
        `INSERT INTO guidance_publications (
          guidance_draft_id,
          segment_id,
          publication_channel,
          scheduled_for,
          metadata
        ) VALUES ($1, $2, 'email', $3, $4)
        RETURNING *`,
        [
          guidance_draft_id,
          segment_id || null,
          scheduled_for,
          JSON.stringify({ test_mode: test_mode || false }),
        ]
      );

      const publication = result.rows[0];

      // Queue for delivery
      await publishQueue.add({
        publicationId: publication.id,
        testMode: test_mode || false,
      }, {
        delay: new Date(scheduled_for).getTime() - Date.now(),
      });

      logger.info(`Publication scheduled: ${publication.id}`);

      res.json({
        message: 'Publication scheduled',
        publication: {
          id: publication.id,
          scheduled_for: publication.scheduled_for,
          test_mode: test_mode || false,
        },
      });

    } catch (error) {
      logger.error('Schedule publication failed:', error);
      res.status(500).json({ error: 'Failed to schedule publication' });
    }
  }
);

/**
 * Rollback publication (within grace period)
 */
router.post(
  '/publications/:id/rollback',
  [
    param('id').isUUID(),
    body('reason').isString().notEmpty(),
  ],
  validate,
  async (req, res) => {
    try {
      const { id } = req.params;
      const { reason } = req.body;

      // Fetch publication
      const result = await db.query(
        `SELECT * FROM guidance_publications
         WHERE id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Publication not found' });
      }

      const publication = result.rows[0];

      // Check if within grace period
      const now = new Date();
      const gracePeriodEnds = new Date(publication.grace_period_ends_at);

      if (now > gracePeriodEnds) {
        return res.status(400).json({
          error: 'Grace period expired',
          grace_period_ended: gracePeriodEnds.toISOString(),
        });
      }

      // Perform rollback
      await db.query(
        `UPDATE guidance_publications
         SET rolled_back_at = NOW(),
             rollback_reason = $1,
             can_rollback = false
         WHERE id = $2`,
        [reason, id]
      );

      logger.info(`Publication ${id} rolled back: ${reason}`);

      // TODO: Send rollback notification to recipients

      res.json({
        message: 'Publication rolled back successfully',
        publication_id: id,
      });

    } catch (error) {
      logger.error('Rollback failed:', error);
      res.status(500).json({ error: 'Failed to rollback publication' });
    }
  }
);

/**
 * Get publication status
 */
router.get(
  '/publications/:id',
  [param('id').isUUID()],
  validate,
  async (req, res) => {
    try {
      const { id } = req.params;

      const result = await db.query(
        `SELECT gp.*, gd.title
         FROM guidance_publications gp
         JOIN guidance_drafts gd ON gp.guidance_draft_id = gd.id
         WHERE gp.id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Publication not found' });
      }

      const publication = result.rows[0];

      // Get delivery events
      const eventsResult = await db.query(
        `SELECT event_type, COUNT(*) as count
         FROM delivery_events
         WHERE publication_id = $1
         GROUP BY event_type`,
        [id]
      );

      const events = {};
      for (const row of eventsResult.rows) {
        events[row.event_type] = parseInt(row.count, 10);
      }

      res.json({
        publication: {
          id: publication.id,
          title: publication.title,
          scheduled_for: publication.scheduled_for,
          published_at: publication.published_at,
          recipients_count: publication.recipients_count,
          successful_deliveries: publication.successful_deliveries,
          failed_deliveries: publication.failed_deliveries,
          can_rollback: publication.can_rollback,
          grace_period_ends_at: publication.grace_period_ends_at,
          rolled_back_at: publication.rolled_back_at,
          events,
        },
      });

    } catch (error) {
      logger.error('Get publication failed:', error);
      res.status(500).json({ error: 'Failed to fetch publication' });
    }
  }
);

/**
 * Check safety guardrails
 */
router.post(
  '/publications/:id/safety-check',
  [param('id').isUUID()],
  validate,
  async (req, res) => {
    try {
      const { id } = req.params;

      const result = await db.query(
        `SELECT * FROM guidance_publications WHERE id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Publication not found' });
      }

      const publication = result.rows[0];
      const safetyCheck = await SafetyGuardrails.checkBeforePublish(publication);

      res.json(safetyCheck);

    } catch (error) {
      logger.error('Safety check failed:', error);
      res.status(500).json({ error: 'Failed to perform safety check' });
    }
  }
);

export default router;
