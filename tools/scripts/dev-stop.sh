#!/bin/bash
# Stop all development servers

echo "🛑 Stopping NUJ Monitor services..."

# Kill background processes
pkill -f "cargo run" || true
pkill -f "python main.py" || true
pkill -f "npm run dev" || true
pkill -f "mix phx.server" || true

# Stop containers
podman-compose down

echo "✅ All services stopped"
