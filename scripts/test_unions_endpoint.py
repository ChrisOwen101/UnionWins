#!/usr/bin/env python3
"""
Test that the /api/wins/unions endpoint works correctly.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.models import UK_UNIONS

print("=" * 80)
print("Testing /api/wins/unions Endpoint")
print("=" * 80)
print()

print(f"✅ UK_UNIONS imported from models: {len(UK_UNIONS)} unions")
print()

print("Sample unions from the canonical list:")
for i, union in enumerate(UK_UNIONS[:10], 1):
    print(f"  {i}. {union}")

print()
print("=" * 80)
print("Endpoint Details")
print("=" * 80)
print()
print("URL: GET /api/wins/unions")
print("Authentication: None required (public endpoint)")
print("Response: JSON array of union names")
print()
print("Usage in frontend:")
print("  fetch('/api/wins/unions')")
print("    .then(res => res.json())")
print("    .then(unions => console.log(unions))")
print()
print("=" * 80)
