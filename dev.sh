#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Union Wins Development Environment${NC}"
echo ""

# Clean up any processes using our ports
echo -e "${BLUE}Cleaning up ports 3000 and 3001...${NC}"
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
echo -e "${GREEN}Ports cleaned${NC}"
echo ""

# Track if we started PostgreSQL
POSTGRES_STARTED=false

# Function to cleanup background processes on script exit
cleanup() {
  echo ""
  echo -e "${GREEN}Shutting down services...${NC}"
  
  # Stop background processes
  kill $(jobs -p) 2>/dev/null
  
  # Stop PostgreSQL if we started it
  if [ "$POSTGRES_STARTED" = true ]; then
    echo -e "${BLUE}Stopping PostgreSQL...${NC}"
    brew services stop postgresql@15 2>/dev/null || brew services stop postgresql 2>/dev/null
  fi
  
  exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Check if PostgreSQL is running, start if not
echo -e "${BLUE}Checking PostgreSQL...${NC}"
if ! pgrep -x postgres > /dev/null; then
  echo -e "${YELLOW}PostgreSQL not running. Starting PostgreSQL...${NC}"
  if command -v brew &> /dev/null; then
    brew services start postgresql@15 2>/dev/null || brew services start postgresql 2>/dev/null
    POSTGRES_STARTED=true
    echo -e "${GREEN}PostgreSQL started${NC}"
    sleep 2
  else
    echo -e "${YELLOW}Warning: brew not found. Please start PostgreSQL manually.${NC}"
  fi
else
  echo -e "${GREEN}PostgreSQL is already running${NC}"
fi

# Start backend (Python)
echo -e "${BLUE}Starting backend on port 3001...${NC}"
cd backend && .venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 3001 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}Starting frontend on port 3000...${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}Development servers are running!${NC}"
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "Backend:  ${BLUE}http://localhost:3001${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for any process to exit
wait
