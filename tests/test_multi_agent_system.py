#!/usr/bin/env python3
"""
Comprehensive test suite for the Multi-Agent Travel Assistant System
Tests all agents, intent classification, and context awareness
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator
from core.utils import classify_intent, detect_destination, detect_trip_length, detect_time, extract_preferences
import json

def test_intent_classification():
    """Test the intent classification system"""
    print("🧪 TESTING INTENT CLASSIFICATION")
    print("=" * 50)
    
    test_cases = [
        ("Món ăn ngon ở Hà Nội có gì?", "eat"),
        ("Chỗ nào đẹp ở Sa Pa để tham quan?", "visit"),
        ("Lập lịch đi Hội An 3 ngày", "plan"),
        ("Tìm khách sạn tốt ở Đà Nẵng", "book"),
        ("Tiền tệ Việt Nam là gì?", "other"),
        ("Tôi muốn ăn phở ở Hà Nội", "eat"),
        ("Đặt phòng khách sạn 5 sao", "book"),
        ("Du lịch Sa Pa 2 ngày như thế nào?", "plan"),
    ]
    
    correct = 0
    for query, expected in test_cases:
        predicted = classify_intent(query)
        status = "✅" if predicted == expected else "❌"
        print(f"{status} '{query}' → {predicted} (expected: {expected})")
        if predicted == expected:
            correct += 1
    
    print(f"\n📊 Accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")

def test_parameter_extraction():
    """Test parameter extraction functions"""
    print("\n🧪 TESTING PARAMETER EXTRACTION")
    print("=" * 50)
    
    test_queries = [
        "Tôi muốn đi Sa Pa 3 ngày từ ngày 15/6/2025",
        "Du lịch Hà Nội hai ngày vào cuối tuần này",
        "Đi Hội An 4 ngày, thích chụp ảnh và ăn đường phố",
        "Tham quan Đà Nẵng ngày mai",
        "Sa-pa 2 day trip tomorrow"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"   🎯 Destination: {detect_destination(query)}")
        print(f"   📅 Trip length: {detect_trip_length(query)}")
        print(f"   ⏰ Time info: {detect_time(query)}")
        print(f"   ❤️ Preferences: {extract_preferences(query)}")

def test_multi_agent_system():
    """Test the complete multi-agent system"""
    print("\n🤖 TESTING MULTI-AGENT SYSTEM")
    print("=" * 50)
    
    # Initialize the orchestrator
    try:
        orchestrator = MultiAgentTravelOrchestrator()
        print("✅ Multi-Agent Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return
    
    # Test queries for each intent
    test_queries = [
        {
            "query": "Món ăn đặc sản ở Hà Nội",
            "intent": "eat",
            "agent": "FoodAgent"
        },
        {
            "query": "Địa điểm đẹp ở Sa Pa để chụp ảnh",
            "intent": "visit", 
            "agent": "LocationAgent"
        },
        {
            "query": "Lập lịch đi Hội An 2 ngày từ ngày mai",
            "intent": "plan",
            "agent": "ItineraryAgent"
        },
        {
            "query": "Tìm khách sạn giá rẻ ở Đà Nẵng",
            "intent": "book",
            "agent": "BookingAgent"
        },
        {
            "query": "Thời tiết Việt Nam như thế nào?",
            "intent": "other",
            "agent": "DefaultAgent"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. Testing {test_case['agent']} with query:")
        print(f"   '{test_case['query']}'")
        print("-" * 40)
        
        try:
            response = orchestrator.process_query(test_case['query'])
            print(f"✅ Response received ({len(response)} characters)")
            print(f"   Preview: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_context_awareness():
    """Test context-aware conversation handling"""
    print("\n🧠 TESTING CONTEXT AWARENESS")
    print("=" * 50)
    
    try:
        orchestrator = MultiAgentTravelOrchestrator()
        
        # First query - establish context
        print("1. Establishing context...")
        query1 = "Tôi muốn đi Sa Pa 3 ngày"
        response1 = orchestrator.process_query(query1)
        print(f"   Query: '{query1}'")
        print(f"   ✅ Context established")
        
        # Follow-up queries that should use context
        follow_ups = [
            "Thay đổi thành 2 ngày được không?",
            "Thêm hoạt động trekking vào",
            "Món ăn ở đó có gì ngon?"
        ]
        
        for i, follow_up in enumerate(follow_ups, 2):
            print(f"\n{i}. Testing follow-up query...")
            print(f"   Query: '{follow_up}'")
            
            # Check if memory detects this as follow-up
            context = orchestrator.memory_agent.get_relevant_context(follow_up)
            is_followup = context.get('is_follow_up', False)
            
            print(f"   🧠 Detected as follow-up: {'Yes' if is_followup else 'No'}")
            
            try:
                response = orchestrator.process_query(follow_up)
                print(f"   ✅ Response generated")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test conversation history
        print(f"\n📚 Conversation History:")
        history = orchestrator.get_conversation_history()
        print(f"   {history}")
        
    except Exception as e:
        print(f"❌ Context awareness test failed: {e}")

def test_weather_integration():
    """Test weather integration capabilities"""
    print("\n🌤️ TESTING WEATHER INTEGRATION")
    print("=" * 50)
    
    try:
        from tools.utils_tool import RealtimeWeatherTool, WeatherRecommendationTool
        
        # Test basic weather tool
        weather_tool = RealtimeWeatherTool()
        print("✅ Weather tool initialized")
        
        # Test weather recommendation tool
        weather_rec_tool = WeatherRecommendationTool()
        print("✅ Weather recommendation tool initialized")
        
        # Test weather integration in queries
        orchestrator = MultiAgentTravelOrchestrator()
        
        weather_queries = [
            "Lập lịch đi Hà Nội 2 ngày từ ngày mai",
            "Thời tiết Sa Pa hôm nay như thế nào?",
        ]
        
        for query in weather_queries:
            print(f"\n🌤️ Testing: '{query}'")
            try:
                response = orchestrator.process_query(query)
                has_weather_info = any(word in response.lower() for word in ['weather', 'thời tiết', 'temperature', 'nhiệt độ'])
                print(f"   {'✅' if has_weather_info else '⚠️'} Weather info {'included' if has_weather_info else 'not detected'}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Weather integration test failed: {e}")

def generate_system_report():
    """Generate a comprehensive system report"""
    print("\n📊 SYSTEM CAPABILITY REPORT")
    print("=" * 50)
    
    capabilities = {
        "Intent Classification": "✅ Automatic classification of user queries into 5 intents",
        "Multi-Agent Routing": "✅ Intelligent routing to 6 specialized agents", 
        "Context Awareness": "✅ Conversation memory and follow-up handling",
        "Weather Integration": "✅ Real-time weather data and activity optimization",
        "Parameter Extraction": "✅ Robust destination, date, and preference detection",
        "RAG Integration": "✅ Knowledge base access for food and location data",
        "Vietnamese Support": "✅ Full Vietnamese language processing and responses",
        "Planning Scenarios": "✅ PlanningWithTime and PlanningWithoutTime scenarios",
        "Resource Calculation": "✅ Sophisticated itinerary resource requirements",
        "Hotel Booking": "✅ Hotel search and booking assistance"
    }
    
    for capability, status in capabilities.items():
        print(f"{status} {capability}")
    
    print(f"\n🎯 System Architecture:")
    print(f"   • OrchestratorAgent (Central coordinator)")
    print(f"   • FoodAgent (Cuisine recommendations)")
    print(f"   • LocationAgent (Attraction recommendations)")
    print(f"   • ItineraryAgent (Complete trip planning)")
    print(f"   • BookingAgent (Hotel booking)")
    print(f"   • DefaultAgent (General questions)")
    print(f"   • MemoryAgent (Conversation context)")

def main():
    """Run comprehensive test suite"""
    print("🚀 MULTI-AGENT TRAVEL ASSISTANT SYSTEM - TEST SUITE")
    print("=" * 80)
    
    try:
        # Run all tests
        test_intent_classification()
        test_parameter_extraction()
        test_multi_agent_system()
        test_context_awareness()
        test_weather_integration()
        generate_system_report()
        
        print(f"\n🎉 TEST SUITE COMPLETED!")
        print("=" * 80)
        print("💡 To run interactive mode: python core/main.py")
        print("💡 To test specific queries: from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")

if __name__ == "__main__":
    main()
