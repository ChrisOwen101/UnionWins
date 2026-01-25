#!/usr/bin/env python3
"""
Test that UK_UNIONS import works correctly in research_service.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.models import UK_UNIONS
from src.services.research_service import create_research_input

print("=" * 80)
print("Testing UK_UNIONS Import")
print("=" * 80)
print()

print(f"✅ UK_UNIONS imported from models: {len(UK_UNIONS)} unions")
print()

# Test creating a research prompt
prompt = create_research_input("January 2026")
print(f"✅ Research prompt generated: {len(prompt)} characters")
print()

# Verify union list is in the prompt
union_lines = [line for line in prompt.split('\n') if line.strip().startswith('-')]
print(f"✅ Prompt includes {len(union_lines)} union entries")
print()

# Verify specific unions are present
test_unions = ["Unite the Union", "GMB", "Unison", "National Union of Rail, Maritime and Transport Workers (RMT)"]
for union in test_unions:
    if union in prompt:
        print(f"  ✅ Found: {union}")
    else:
        print(f"  ❌ Missing: {union}")

print()
print("=" * 80)
print("All tests passed!")
print("=" * 80)
