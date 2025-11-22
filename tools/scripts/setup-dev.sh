#!/bin/bash
# NUJ Social Media Monitor - Development Environment Setup

set -e

echo "🚀 Setting up NUJ Social Media Monitor development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

command -v podman >/dev/null 2>&1 || { echo -e "${RED}Error: podman is required but not installed.${NC}" >&2; exit 1; }
command -v rust >/dev/null 2>&1 || { echo -e "${YELLOW}Warning: Rust not found. Install from https://rustup.rs${NC}"; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Error: Python 3.11+ is required.${NC}" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}Error: Node.js 20+ is required.${NC}" >&2; exit 1; }
command -v elixir >/dev/null 2>&1 || { echo -e "${YELLOW}Warning: Elixir not found. Install from https://elixir-lang.org${NC}"; }

echo -e "${GREEN}✓ Prerequisites check complete${NC}"

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created. Please update with your credentials.${NC}"
fi

# Setup Rust collector
echo -e "\n${YELLOW}Setting up Rust collector service...${NC}"
cd services/collector
if command -v cargo >/dev/null 2>&1; then
    cargo build
    echo -e "${GREEN}✓ Collector service built${NC}"
fi
cd ../..

# Setup Python analyzer
echo -e "\n${YELLOW}Setting up Python analyzer service...${NC}"
cd services/analyzer
python3 -m venv venv || true
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -e ".[dev]"
python -m spacy download en_core_web_lg
echo -e "${GREEN}✓ Analyzer service configured${NC}"
deactivate 2>/dev/null || true
cd ../..

# Setup Node.js publisher
echo -e "\n${YELLOW}Setting up Node.js publisher service...${NC}"
cd services/publisher
npm install
echo -e "${GREEN}✓ Publisher service configured${NC}"
cd ../..

# Setup Elixir dashboard
echo -e "\n${YELLOW}Setting up Elixir dashboard service...${NC}"
cd services/dashboard
if command -v mix >/dev/null 2>&1; then
    mix local.hex --force
    mix local.rebar --force
    mix deps.get
    echo -e "${GREEN}✓ Dashboard service configured${NC}"
fi
cd ../..

# Create log directories
echo -e "\n${YELLOW}Creating log directories...${NC}"
mkdir -p logs/{collector,analyzer,publisher,dashboard}
echo -e "${GREEN}✓ Log directories created${NC}"

# Start infrastructure services
echo -e "\n${YELLOW}Starting infrastructure services (PostgreSQL, Redis)...${NC}"
podman-compose up -d postgres redis
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
podman exec -it nuj-postgres psql -U nuj_admin -d nuj_monitor -f /docker-entrypoint-initdb.d/schema.sql
echo -e "${GREEN}✓ Database initialized${NC}"

echo -e "\n${GREEN}✅ Development environment setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update .env with your API credentials"
echo "2. Start services: ./tools/scripts/dev-start.sh"
echo "3. Access dashboard: http://localhost:4000"
echo "4. View logs: ./tools/scripts/dev-logs.sh"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
