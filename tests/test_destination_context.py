"""
Test for destination detection context issue
Testing the specific case: "lên lịch đi sapa 2 ngày" followed by "chuyến đi 3 ngày thì sao"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import detect_destination, classify_intent
from agents.memory_agent import MemoryAgent

def test_destination_context_issue():
    """Test the specific issue with destination context"""
    
    print("="*60)
    print("TESTING DESTINATION CONTEXT ISSUE")
    print("="*60)
    
    # Initialize memory agent
    memory_agent = MemoryAgent()
    
    # First query
    query1 = "lên lịch đi sapa 2 ngày"
    print(f"\n1. First query: '{query1}'")
    
    # Test destination detection
    dest1 = detect_destination(query1)
    print(f"   Detected destination: {dest1}")
    
    # Test intent classification
    intent1 = classify_intent(query1)
    print(f"   Detected intent: {intent1}")
    
    # Get context from memory agent
    context1 = memory_agent.get_relevant_context(query1, intent1)
    print(f"   Memory context: {context1}")
    
    # Simulate memory update (what would happen after processing)    # This simulates what _update_memory would do
    extracted_info = {
        "destination": dest1,
        "duration": 2,
        "intent": intent1
    }
    memory_agent.add_interaction(query1, intent1, "ItineraryAgent", "Mock response for Sa Pa 2 days", extracted_info)
    print(f"   Updated memory context: {memory_agent.user_context}")
    
    print("\n" + "-"*50)
    
    # Second query (follow-up)
    query2 = "chuyến đi 3 ngày thì sao"
    print(f"\n2. Second query: '{query2}'")
    
    # Test destination detection
    dest2 = detect_destination(query2)
    print(f"   Detected destination: {dest2}")
    
    # Test intent classification
    intent2 = classify_intent(query2)
    print(f"   Detected intent: {intent2}")
    
    # Get context from memory agent
    context2 = memory_agent.get_relevant_context(query2, intent2)
    print(f"   Memory context: {context2}")
    print(f"   Current destination from memory: {memory_agent.user_context.get('current_destination')}")
    
    # Test individual components
    print("\n" + "-"*50)
    print("DETAILED ANALYSIS:")
    
    # Test fuzzy matching directly
    from thefuzz import process
    from core.utils import VIETNAMESE_DESTINATIONS
    
    # Check what "chuyến đi" might match
    all_destinations = []
    for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
        all_destinations.append(canonical)
        all_destinations.extend(aliases)
    
    words2 = query2.lower().split()
    print(f"\nWords in query2: {words2}")
    
    for i in range(len(words2)):
        for j in range(i+1, min(i+4, len(words2)+1)):
            candidate = " ".join(words2[i:j])
            if len(candidate) >= 3:
                match, score = process.extractOne(candidate, all_destinations)
                print(f"   Candidate: '{candidate}' -> Match: '{match}' (score: {score})")
                if score >= 99:
                    print(f"      ⚠️  HIGH SCORE MATCH FOUND!")
    
    print("\n" + "="*60)
    return dest1, dest2, context1, context2

def test_fuzzy_matching_thresholds():
    """Test different fuzzy matching thresholds"""
    print("\nTESTING FUZZY MATCHING THRESHOLDS:")
    print("-"*40)
    
    test_phrases = [
        "chuyến đi",
        "đi",
        "3 ngày",
        "ngày",
        "thì sao",
        "sao"
    ]
    
    from thefuzz import process
    from core.utils import VIETNAMESE_DESTINATIONS
    
    all_destinations = []
    for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
        all_destinations.append(canonical)
        all_destinations.extend(aliases)
    
    for phrase in test_phrases:
        match, score = process.extractOne(phrase, all_destinations)
        print(f"'{phrase}' -> '{match}' (score: {score})")
        if score >= 80:
            print(f"   ⚠️  Would match at threshold 80")
        if score >= 90:
            print(f"   ⚠️  Would match at threshold 90") 
        if score >= 95:
            print(f"   ⚠️  Would match at threshold 95")
        if score >= 99:
            print(f"   🚨 Would match at threshold 99")

if __name__ == "__main__":
    test_destination_context_issue()
    test_fuzzy_matching_thresholds()
