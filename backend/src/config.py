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

# CORS configuration - hardcoded to allow all origins
ALLOWED_ORIGINS = ["*"]

# Background polling configuration
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))

# Server configuration
PORT = int(os.getenv("PORT", "3001"))

# Admin configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")

# Resend API configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Union Wins <updates@unionwins.com>")

# TikTok API configuration
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
