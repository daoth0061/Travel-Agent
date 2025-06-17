#!/usr/bin/env python3
"""
Debug destination detection to understand why 'Có món ăn gì ngon ở đó?' 
is being detected as 'đà lạt'
"""

from core.utils import detect_destination
from thefuzz import fuzz, process

# Test the problematic query
query = "Có món ăn gì ngon ở đó?"
print(f"🔍 Testing query: '{query}'")

# Import the destinations dictionary
from core.utils import VIETNAMESE_DESTINATIONS

print(f"🎯 Detected destination: {detect_destination(query)}")

# Let's debug the fuzzy matching step by step
query_lower = query.lower()
print(f"📝 Query lowercase: '{query_lower}'")

# Check direct matches first
print("\n=== DIRECT MATCHES ===")
for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
    if canonical in query_lower:
        print(f"✅ Direct match found: {canonical}")
    for alias in aliases:
        if alias in query_lower:
            print(f"✅ Alias match found: {alias} -> {canonical}")

# Check fuzzy matching
print("\n=== FUZZY MATCHING ===")
all_destinations = []
for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
    all_destinations.append(canonical)
    all_destinations.extend(aliases)

words = query_lower.split()
print(f"📄 Words: {words}")

for i in range(len(words)):
    for j in range(i+1, min(i+4, len(words)+1)):  # 1-3 word combinations
        candidate = " ".join(words[i:j])
        if len(candidate) >= 3:  # Minimum length
            match, score = process.extractOne(candidate, all_destinations)
            print(f"🔍 Candidate: '{candidate}' -> Match: '{match}' (Score: {score})")
            if score >= 80:  # High confidence threshold
                print(f"⚠️  HIGH SCORE MATCH FOUND: '{candidate}' -> '{match}' (Score: {score})")
                # Find canonical name
                for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
                    if match == canonical or match in aliases:
                        print(f"🎯 Canonical destination: {canonical}")
                        break
