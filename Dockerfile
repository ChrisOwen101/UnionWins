# Multi-stage build for Union Wins application
# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the frontend
RUN npm run build

# Stage 2: Python backend with frontend static files
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy backend files
COPY backend/pyproject.toml ./backend/
COPY backend/src ./backend/src/

# Install Python dependencies using uv
WORKDIR /app/backend
RUN uv pip install --system --no-cache .

# Copy built frontend to backend static directory
COPY --from=frontend-builder /app/frontend/dist ./static/

WORKDIR /app/backend

# Expose the application port
EXPOSE 80

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=80

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
