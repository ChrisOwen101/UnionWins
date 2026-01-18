# Union Wins

A full-stack TypeScript application with React frontend and Python backend.

## Project Structure

```
union-wins/
├── frontend/          # React + TypeScript frontend
├── backend/    # Python backend
├── dev.sh            # Script to run both services
└── package.json      # Root package.json for monorepo
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- Python 3.11 or higher
- uv (Python package manager)

### Installation

Install all dependencies for both frontend and backend:

```bash
npm run install:all
```

Or install them individually:

```bash
# Root dependencies
npm install

# Frontend dependencies
cd frontend && npm install

# Backend -python && uv sync
cd backend && npm install
```

### Development

Run both frontend and backend simultaneously:

```bash
./dev.sh
```

Or use the npm script:

```bash
npm run dev
```

Or run them separately:

```bash
# Frontend only (http://localhost:3000)
npm run frontend

# Backend only (http://localhost:3001)
npm run backend
```

### Services

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:3001

The frontend is configured to proxy API requests to the backend automatically.

## Tech Stack

### Frontend

- React 18
- TypeScript 5
- Vite
- ESLint
- Tailwind CSS

### Backend

- FastAPI
- Python 3.11+
- Uvicorn (ASGI server)
- Pydantic for data validation

## Building for Production

### Frontend

```bash
cd frontend
npm run build
```

### Backend

```bash
cd backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 3001
```
