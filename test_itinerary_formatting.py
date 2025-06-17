#!/usr/bin/env python3
"""
Test to check if the itinerary formatting issue is fixed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

def test_itinerary_formatting():
    """Test if the itinerary response is properly formatted without markdown code blocks"""
    
    print("="*60)
    print("TESTING ITINERARY FORMATTING")
    print("="*60)
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    query = "lên kế hoạch đi chơi đà nẵng 4 ngày"
    print(f"Query: {query}")
    print("Processing...")
    
    try:
        response = orchestrator.process_query(query)
        
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(response)
        
        # Check for formatting issues
        issues = []
        
        # Check for markdown code blocks
        if "```" in response:
            issues.append("Contains markdown code blocks (```)")
        
        # Check for internal reasoning
        reasoning_keywords = ["Thought:", "Action:", "Observation:", "Final Answer:"]
        for keyword in reasoning_keywords:
            if keyword in response:
                issues.append(f"Contains internal reasoning: {keyword}")
        
        # Check for good formatting indicators
        good_indicators = ["📅", "🌅", "🍽️", "🌆", "🌃", "**NGÀY"]
        has_good_format = any(indicator in response for indicator in good_indicators)
        
        print("\n" + "="*60)
        print("FORMATTING ANALYSIS:")
        print("="*60)
        
        if issues:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ NO FORMATTING ISSUES DETECTED!")
        
        if has_good_format:
            print("✅ Good formatting indicators found (emojis, day headers)")
        else:
            print("❌ Missing expected formatting indicators")
            
        print(f"\nResponse starts with: '{response[:50]}...'")
        print(f"Contains emoji day markers: {'📅' in response}")
        print(f"Contains code blocks: {'```' in response}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_itinerary_formatting()
