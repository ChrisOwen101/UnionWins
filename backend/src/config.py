"""
Configuration settings and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from root .env file
root_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(root_env_path)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://chrisowen@localhost:5432/unionwins"
)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# CORS configuration
# In production (Docker), allow same-origin only; in development, allow localhost
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
ALLOWED_ORIGINS = CORS_ORIGINS  # Alias for compatibility

# Background polling configuration
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))

# Default image for wins
DEFAULT_WIN_IMAGE_URL = "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&h=400&fit=crop&q=80"
