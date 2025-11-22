#!/bin/bash
# Run tests for all services

set -e

echo "🧪 Running tests for all services..."

# Collector (Rust)
echo -e "\n📦 Testing Collector (Rust)..."
cd services/collector
cargo test
cargo clippy -- -D warnings
cargo fmt -- --check
cd ../..

# Analyzer (Python)
echo -e "\n📦 Testing Analyzer (Python)..."
cd services/analyzer
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pytest
black --check .
isort --check-only .
mypy app/
deactivate 2>/dev/null || true
cd ../..

# Publisher (Node.js)
echo -e "\n📦 Testing Publisher (Node.js)..."
cd services/publisher
npm test
npm run lint
cd ../..

# Dashboard (Elixir)
echo -e "\n📦 Testing Dashboard (Elixir)..."
cd services/dashboard
mix test
mix format --check-formatted
cd ../..

echo -e "\n✅ All tests passed!"
