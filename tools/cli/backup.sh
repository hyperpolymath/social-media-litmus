#!/bin/bash
# Database backup tool

set -e

BACKUP_DIR=${BACKUP_DIR:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nuj_monitor_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "📦 Creating database backup..."

podman exec nuj-postgres pg_dump -U ${POSTGRES_USER:-nuj_admin} nuj_monitor | gzip > "$BACKUP_FILE"

echo "✅ Backup created: $BACKUP_FILE"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned up"
