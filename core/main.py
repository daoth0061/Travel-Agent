import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

def main():
    """
    Main entry point for the Multi-Agent Travel Assistant System
    """
    print("🚀 Starting Multi-Agent Travel Assistant System...")
    
    # Initialize the sophisticated orchestrator
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Test queries for different intents
    test_queries = [
        "Tôi muốn đi Sa Pa 3 ngày từ ngày 15/6/2025, thích trekking và cảnh đẹp núi rừng.",
        "Món ăn ngon ở Hà Nội có gì?",
        "Chỗ nào đẹp ở Hội An để chụp ảnh?",
        "Tìm khách sạn tốt ở Đà Nẵng cho 2 người.",
        "Tiền tệ ở Việt Nam là gì?"
    ]
    
    print("\n" + "="*80)
    print("🧪 TESTING MULTI-AGENT SYSTEM WITH SAMPLE QUERIES")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: {query}")
        print("-" * 60)
        try:
            response = orchestrator.process_query(query)
            print(f"Response: {response[:200]}..." if len(response) > 200 else response)
        except Exception as e:
            print(f"Error: {e}")
        print("\n" + "="*60)
    
    # Run interactive mode
    print("\n🎯 Starting interactive mode...")
    orchestrator.run_interactive()

if __name__ == "__main__":
    main()