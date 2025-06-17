#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

def debug_context():
    print("=== DEBUGGING CONTEXT AWARENESS ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # First query - should establish destination
    print("1. User query: 'Tôi muốn đi du lịch Đà Nẵng'")
    response1 = orchestrator.process_query('Tôi muốn đi du lịch Đà Nẵng')
    print('=== MEMORY AFTER FIRST QUERY ===')
    print('Current context:', orchestrator.memory_agent.user_context)
    print('Conversation history length:', len(orchestrator.memory_agent.conversation_history))
    if orchestrator.memory_agent.conversation_history:
        print('Last interaction:', orchestrator.memory_agent.conversation_history[-1])
    print()
    
    # Second query - should use context
    print("2. User query: 'Có món ăn gì ngon ở đó?'")
    # Let's manually check what context will be provided
    context = orchestrator.memory_agent.get_relevant_context('Có món ăn gì ngon ở đó?', 'eat')
    print('Context to be provided:', context)
    
    response2 = orchestrator.process_query('Có món ăn gì ngon ở đó?')
    print('=== MEMORY AFTER SECOND QUERY ===')
    print('Current context:', orchestrator.memory_agent.user_context)
    print('Response:', response2[:200])

if __name__ == "__main__":
    debug_context()
