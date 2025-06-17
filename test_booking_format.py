#!/usr/bin/env python3
"""
Test to check if the BookingAgent output format is fixed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

def test_booking_output_format():
    """Test if the BookingAgent shows clean output without internal reasoning"""
    
    print("="*60)
    print("TESTING BOOKING AGENT OUTPUT FORMAT")
    print("="*60)
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    query = "tôi muốn đặt phòng ở đà nẵng"
    print(f"Query: {query}")
    print("Processing...")
    
    try:
        response = orchestrator.process_query(query)
        
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(response)
        
        # Check if response contains unwanted thinking process
        problematic_keywords = [
            "Thought:", "Action:", "Action Input:", "Observation:", 
            "I now know the final answer", "Final Answer:"
        ]
        
        issues_found = []
        for keyword in problematic_keywords:
            if keyword in response:
                issues_found.append(keyword)
        
        if issues_found:
            print("\n❌ ISSUES FOUND:")
            for issue in issues_found:
                print(f"  - Response contains: {issue}")
            print("  🔧 The BookingAgent is still showing internal reasoning")
        else:
            print("\n✅ BOOKING OUTPUT FORMAT LOOKS CLEAN!")
            print("  🎉 No internal reasoning keywords found")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_booking_output_format()
