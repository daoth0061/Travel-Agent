#!/usr/bin/env python3
"""
Test script to validate destination detection and context handling fixes
"""

from core.utils import detect_destination, classify_intent
from agents.memory_agent import MemoryAgent

def test_destination_detection_edge_cases():
    """Test edge cases for destination detection"""
    print("="*60)
    print("TESTING DESTINATION DETECTION EDGE CASES")
    print("="*60)
    
    test_cases = [
        # Valid destination queries
        ("lên lịch đi sapa 2 ngày", "sa pa"),
        ("du lịch Hà Nội", "hà nội"),
        ("đi Đà Lạt cuối tuần", "đà lạt"),
        ("tham quan Hội An", "hội an"),
        
        # Follow-up queries that should NOT detect destinations
        ("chuyến đi 3 ngày thì sao", None),
        ("thì 2 ngày có đủ không", None),
        ("đi 4 ngày được không", None),
        ("sao không đi 5 ngày", None),
        ("thế còn 1 tuần thì sao", None),
        
        # Edge cases with common words
        ("đi thì đi", None),
        ("sao lại thế", None),
        ("như thế nào", None),
        ("có gì hay không", None),
        
        # Misspellings that should still work
        ("du lịch sapa", "sa pa"),  # sapa instead of sa pa
        ("đi danang", "đà nẵng"),  # danang instead of đà nẵng
    ]
    
    for query, expected in test_cases:
        result = detect_destination(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} '{query}' -> Expected: {expected}, Got: {result}")
    
    print()

def test_full_context_scenario():
    """Test the full scenario that was problematic"""
    print("="*60)
    print("TESTING FULL CONTEXT SCENARIO")
    print("="*60)
    
    memory_agent = MemoryAgent()
    
    # First query: Planning a trip to Sa Pa
    query1 = "lên lịch đi sapa 2 ngày"
    dest1 = detect_destination(query1)
    intent1 = classify_intent(query1)
    
    print(f"1. Query: '{query1}'")
    print(f"   Destination: {dest1}")
    print(f"   Intent: {intent1}")
    
    # Add to memory
    extracted_info = {"destination": dest1, "duration": 2, "intent": intent1}
    memory_agent.add_interaction(query1, intent1, "ItineraryAgent", "Sa Pa 2-day itinerary", extracted_info)
    
    # Second query: Follow-up about duration
    query2 = "chuyến đi 3 ngày thì sao"
    dest2 = detect_destination(query2)
    intent2 = classify_intent(query2)
    context = memory_agent.get_relevant_context(query2, intent2)
    
    print(f"\n2. Query: '{query2}'")
    print(f"   Destination: {dest2}")
    print(f"   Intent: {intent2}")
    print(f"   Context destination: {context.get('current_context', {}).get('current_destination')}")
    
    # The key test: destination should be None but context should have Sa Pa
    if dest2 is None and context.get('current_context', {}).get('current_destination') == 'sa pa':
        print("   ✅ PERFECT! Follow-up query correctly uses context instead of false destination match")
    else:
        print("   ❌ ISSUE: Context handling not working as expected")
    
    print()

if __name__ == "__main__":
    test_destination_detection_edge_cases()
    test_full_context_scenario()
    print("Test completed!")
