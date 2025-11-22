# Database Infrastructure

## Overview

PostgreSQL 15+ database with TimescaleDB extension for time-series policy tracking.

## Schema Components

### Core Tables
- **platforms**: Social media platforms being monitored
- **platform_credentials**: Encrypted API credentials
- **policy_documents**: Tracked policy documents per platform
- **policy_snapshots**: Time-series snapshots (TimescaleDB hypertable)
- **policy_changes**: Detected changes with NLP analysis

### Communication Tables
- **guidance_drafts**: Member guidance documents
- **member_segments**: Targeted communication groups
- **guidance_publications**: Published guidance with delivery tracking
- **delivery_events**: Individual email delivery events

### Safety & Audit
- **approval_requests**: Human approval workflow
- **audit_log**: Complete system action audit trail
- **system_metrics**: Service health metrics
- **system_config**: System-wide configuration

### User Management
- **users**: System users with role-based access
- **user_sessions**: Active user sessions

## TimescaleDB Hypertables

Optimized for time-series queries:
- `policy_snapshots` - 1 month chunks
- `policy_changes` - 1 month chunks
- `delivery_events` - 1 month chunks
- `audit_log` - 1 month chunks
- `system_metrics` - 1 day chunks

## Migrations

Located in `migrations/` directory:
- `001_initial_schema.sql` - Initial schema creation

Run migrations:
```bash
./tools/cli/migrate.sh up
```

## Initial Data

Default configuration includes:
- 7 major platforms (X, Facebook, Instagram, LinkedIn, TikTok, YouTube, Bluesky)
- Default system configuration
- Default admin user (change password!)
- Default member segments

## Security Features

1. **Encryption**: Platform credentials encrypted with pgcrypto
2. **Audit Logging**: All sensitive actions logged
3. **Row-Level Security**: Can be enabled per deployment
4. **Hashed Emails**: Delivery tracking uses hashed recipient IDs

## Performance Optimizations

1. **Indexes**: Strategic indexes on frequently queried columns
2. **Partial Indexes**: For filtered queries (e.g., active records only)
3. **GIN Indexes**: For JSONB and full-text search
4. **TimescaleDB**: Automatic chunk management and compression

## Views

Pre-built views for common queries:
- `recent_unreviewed_changes` - Changes needing review
- `pending_approvals` - Actions awaiting approval
- `platform_status` - Current monitoring status
- `guidance_metrics` - Publication performance metrics

## Backup & Recovery

See `../monitoring/backup/` for automated backup scripts.

Retention policy:
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

## Monitoring

Metrics exposed:
- Table sizes
- Query performance
- Connection pool usage
- Replication lag (if applicable)

See `../monitoring/` for Prometheus exporters.
