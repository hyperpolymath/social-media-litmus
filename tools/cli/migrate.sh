#!/bin/bash
# Database migration tool

set -e

COMMAND=${1:-up}

case "$COMMAND" in
    up)
        echo "Running database migrations..."
        podman exec -it nuj-postgres psql -U ${POSTGRES_USER:-nuj_admin} -d nuj_monitor -f /docker-entrypoint-initdb.d/schema.sql
        echo "✅ Migrations complete"
        ;;

    down)
        echo "Rolling back last migration..."
        echo "⚠️  Manual rollback required - check schema.sql"
        ;;

    create)
        if [ -z "$2" ]; then
            echo "Usage: $0 create <migration_name>"
            exit 1
        fi

        TIMESTAMP=$(date +%Y%m%d%H%M%S)
        FILENAME="infrastructure/database/migrations/${TIMESTAMP}_$2.sql"

        cat > "$FILENAME" <<EOF
-- Migration: $2
-- Created: $(date)

-- Add your migration SQL here

EOF

        echo "✅ Migration created: $FILENAME"
        ;;

    status)
        echo "Checking migration status..."
        podman exec -it nuj-postgres psql -U ${POSTGRES_USER:-nuj_admin} -d nuj_monitor -c "SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;"
        ;;

    *)
        echo "Usage: $0 {up|down|create <name>|status}"
        exit 1
        ;;
esac
