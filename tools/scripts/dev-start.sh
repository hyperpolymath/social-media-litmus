#!/bin/bash
# Start all development servers

set -e

echo "🚀 Starting NUJ Monitor development servers..."

# Start infrastructure
podman-compose up -d postgres redis prometheus grafana loki

# Wait for services to be ready
echo "Waiting for infrastructure to be ready..."
sleep 5

# Start collector (Rust)
echo "Starting Collector service..."
cd services/collector
cargo run &
COLLECTOR_PID=$!
cd ../..

# Start analyzer (Python)
echo "Starting Analyzer service..."
cd services/analyzer
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
python main.py &
ANALYZER_PID=$!
deactivate 2>/dev/null || true
cd ../..

# Start publisher (Node.js)
echo "Starting Publisher service..."
cd services/publisher
npm run dev &
PUBLISHER_PID=$!
cd ../..

# Start dashboard (Elixir)
echo "Starting Dashboard service..."
cd services/dashboard
mix phx.server &
DASHBOARD_PID=$!
cd ../..

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Services:"
echo "  - Collector:  http://localhost:3001"
echo "  - Analyzer:   http://localhost:3002"
echo "  - Publisher:  http://localhost:3003"
echo "  - Dashboard:  http://localhost:4000"
echo ""
echo "📈 Monitoring:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:    http://localhost:3000 (admin/changeme)"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C to kill all processes
trap "echo 'Stopping services...'; kill $COLLECTOR_PID $ANALYZER_PID $PUBLISHER_PID $DASHBOARD_PID; podman-compose down; exit" INT

# Wait for any process to exit
wait
