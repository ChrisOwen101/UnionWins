#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Union Wins - Lint & Build ===${NC}"
echo ""

# Track overall success
ERRORS=0

# =============================================================================
# FRONTEND LINTING & BUILD
# =============================================================================

echo -e "${BLUE}📋 Step 1: Frontend - ESLint${NC}"
if cd frontend && npm run lint; then
  echo -e "${GREEN}✓ Frontend ESLint passed${NC}"
else
  echo -e "${RED}✗ Frontend ESLint failed${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

echo -e "${BLUE}📋 Step 2: Frontend - TypeScript Check${NC}"
if npx tsc --noEmit; then
  echo -e "${GREEN}✓ Frontend TypeScript check passed${NC}"
else
  echo -e "${RED}✗ Frontend TypeScript check failed${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

echo -e "${BLUE}🏗️  Step 3: Frontend - Build${NC}"
if npm run build; then
  echo -e "${GREEN}✓ Frontend build succeeded${NC}"
else
  echo -e "${RED}✗ Frontend build failed${NC}"
  ERRORS=$((ERRORS + 1))
fi
cd ..
echo ""

# =============================================================================
# BACKEND LINTING & BUILD
# =============================================================================

echo -e "${BLUE}📋 Step 4: Backend - Ruff Linting${NC}"
if cd backend && uv run ruff check src/; then
  echo -e "${GREEN}✓ Backend ruff linting passed${NC}"
else
  echo -e "${RED}✗ Backend ruff linting failed${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

echo -e "${BLUE}📋 Step 5: Backend - Python Syntax Check${NC}"
if python3 -m py_compile src/**/*.py src/*.py 2>/dev/null; then
  echo -e "${GREEN}✓ Backend Python syntax check passed${NC}"
else
  # Try alternative approach for syntax checking
  if find src -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | tee /tmp/python_compile.log; then
    if [ ! -s /tmp/python_compile.log ]; then
      echo -e "${GREEN}✓ Backend Python syntax check passed${NC}"
    else
      echo -e "${RED}✗ Backend Python syntax check failed${NC}"
      cat /tmp/python_compile.log
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo -e "${RED}✗ Backend Python syntax check failed${NC}"
    ERRORS=$((ERRORS + 1))
  fi
fi
echo ""

echo -e "${BLUE}📋 Step 6: Backend - Import Validation${NC}"
# Check if virtual environment exists
if [ ! -d ".venv" ]; then
  echo -e "${YELLOW}⚠ Virtual environment not found. Run 'cd backend && uv sync' first${NC}"
  echo -e "${YELLOW}Skipping import validation${NC}"
else
  if .venv/bin/python -c "import sys; sys.path.insert(0, 'src'); import main; print('All imports successful')"; then
    echo -e "${GREEN}✓ Backend import validation passed${NC}"
  else
    echo -e "${RED}✗ Backend import validation failed${NC}"
    ERRORS=$((ERRORS + 1))
  fi
fi
cd ..
echo ""

# =============================================================================
# SUMMARY
# =============================================================================

echo -e "${GREEN}=== Summary ===${NC}"
if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed successfully!${NC}"
  exit 0
else
  echo -e "${RED}✗ $ERRORS check(s) failed${NC}"
  exit 1
fi
