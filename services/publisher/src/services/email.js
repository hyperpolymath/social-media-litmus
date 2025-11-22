/**
 * Email delivery service
 */

import nodemailer from 'nodemailer';
import { marked } from 'marked';
import Handlebars from 'handlebars';
import { logger } from '../utils/logger.js';
import { config } from '../config/index.js';
import { emailsSentCounter, emailFailuresCounter } from '../monitoring/metrics.js';

class EmailService {
  constructor() {
    this.transporter = null;
  }

  async initialize() {
    logger.info('Initializing email service');

    this.transporter = nodemailer.createTransport({
      host: config.email.host,
      port: config.email.port,
      secure: config.email.secure,
      auth: config.email.auth,
    });

    // Verify connection
    try {
      await this.transporter.verify();
      logger.info('SMTP connection verified');
    } catch (error) {
      logger.error('SMTP verification failed:', error);
      throw error;
    }
  }

  async sendGuidance(publication) {
    const {
      id,
      guidance,
      recipients,
      segment,
    } = publication;

    logger.info(`Sending guidance ${id} to ${recipients.length} recipients`);

    const results = {
      sent: 0,
      failed: 0,
      errors: [],
    };

    // Convert markdown to HTML
    const htmlContent = marked.parse(guidance.content_markdown);

    // Prepare email template
    const template = this.getEmailTemplate();
    const compiledTemplate = Handlebars.compile(template);

    for (const recipient of recipients) {
      try {
        const html = compiledTemplate({
          title: guidance.title,
          summary: guidance.summary,
          content: htmlContent,
          unsubscribeUrl: `https://nuj.org.uk/unsubscribe/${recipient.id}`,
        });

        await this.transporter.sendMail({
          from: config.email.from,
          to: recipient.email,
          subject: guidance.title,
          html,
          text: guidance.content_markdown,
          headers: {
            'X-Publication-ID': id,
            'X-Recipient-ID': recipient.id,
          },
        });

        results.sent++;
        emailsSentCounter.inc();

      } catch (error) {
        logger.error(`Failed to send to ${recipient.email}:`, error);
        results.failed++;
        results.errors.push({
          email: recipient.email,
          error: error.message,
        });
        emailFailuresCounter.inc();
      }
    }

    logger.info(`Delivery complete: ${results.sent} sent, ${results.failed} failed`);
    return results;
  }

  async sendTestEmail(guidance, testEmails) {
    logger.info(`Sending test email to ${testEmails.length} addresses`);

    const htmlContent = marked.parse(guidance.content_markdown);
    const template = this.getEmailTemplate();
    const compiledTemplate = Handlebars.compile(template);

    const results = [];

    for (const email of testEmails) {
      try {
        const html = compiledTemplate({
          title: `[TEST] ${guidance.title}`,
          summary: guidance.summary,
          content: htmlContent,
          unsubscribeUrl: 'https://nuj.org.uk/unsubscribe/test',
        });

        await this.transporter.sendMail({
          from: config.email.from,
          to: email,
          subject: `[TEST] ${guidance.title}`,
          html,
          text: guidance.content_markdown,
        });

        results.push({ email, success: true });
      } catch (error) {
        logger.error(`Failed to send test email to ${email}:`, error);
        results.push({ email, success: false, error: error.message });
      }
    }

    return results;
  }

  getEmailTemplate() {
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
    }
    .header {
      background-color: #1a1a1a;
      color: #fff;
      padding: 20px;
      text-align: center;
    }
    .content {
      padding: 20px;
      background-color: #fff;
    }
    .summary {
      background-color: #f5f5f5;
      border-left: 4px solid #1a1a1a;
      padding: 15px;
      margin: 20px 0;
    }
    .footer {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #ddd;
      font-size: 12px;
      color: #666;
      text-align: center;
    }
    a {
      color: #1a1a1a;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>NUJ Social Media Monitor</h1>
  </div>
  <div class="content">
    <h2>{{title}}</h2>
    {{#if summary}}
    <div class="summary">
      <strong>Summary:</strong> {{summary}}
    </div>
    {{/if}}
    <div>
      {{{content}}}
    </div>
  </div>
  <div class="footer">
    <p>This guidance is provided by the National Union of Journalists</p>
    <p><a href="{{unsubscribeUrl}}">Unsubscribe</a> | <a href="https://nuj.org.uk">NUJ Website</a></p>
  </div>
</body>
</html>
    `;
  }
}

export const emailService = new EmailService();
