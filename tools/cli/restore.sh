#!/bin/bash
# Database restore tool

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will REPLACE the current database!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo "📥 Restoring database from: $BACKUP_FILE"

gunzip -c "$BACKUP_FILE" | podman exec -i nuj-postgres psql -U ${POSTGRES_USER:-nuj_admin} nuj_monitor

echo "✅ Database restored successfully"
