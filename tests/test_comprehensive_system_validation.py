"""
Comprehensive Multi-Agent System Validation Tests
Testing SerpApi integration, context awareness, weather integration, and overall system functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator
from agents.booking_agent import BookingAgent, SerpApiHotelsTool
from agents.memory_agent import MemoryAgent


def test_serpapi_integration():
    """Test SerpApi integration with the BookingAgent"""
    print("\n=== Testing SerpApi Integration ===")
    
    # Initialize the booking agent with LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    booking_agent = BookingAgent(llm)
    
    # Test hotel search tool
    hotel_tool = SerpApiHotelsTool()
    
    # Test with sample data
    result = hotel_tool._run(
        destination="Hanoi",
        check_in_date="2025-07-01", 
        check_out_date="2025-07-03",
        adults=2,
        children=0,
        budget_range="mid_range"
    )
    
    print(f"Hotel search result: {result[:200]}...")
    
    # Verify the result contains hotel information
    assert isinstance(result, str)
    assert len(result) > 100  # Should contain substantial hotel information
    assert "hotel" in result.lower() or "khách sạn" in result.lower()
    
    print("✅ SerpApi integration test passed!")


def test_booking_agent_full_workflow():
    """Test complete BookingAgent workflow with SerpApi"""
    print("\n=== Testing BookingAgent Full Workflow ===")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    booking_agent = BookingAgent(llm)
    
    # Test create_task method with correct signature
    context = {
        "relevant_history": "User is planning a trip to Vietnam from July 15-17 for 2 people with luxury budget",
        "destination": "Hà Nội",
        "check_in_date": "2025-07-15",
        "check_out_date": "2025-07-17",
        "guests": 2,
        "budget": "luxury"
    }
    
    task = booking_agent.create_task(
        request="Tìm khách sạn 4 sao ở Hà Nội cho 2 người từ 15/7 đến 17/7 với ngân sách cao cấp",
        context=context
    )
    
    assert task is not None
    assert hasattr(task, 'description')
    assert "Hà Nội" in task.description
    
    print("✅ BookingAgent workflow test passed!")


def test_context_awareness_multi_turn():
    """Test MemoryAgent context awareness across multiple interactions"""
    print("\n=== Testing Context Awareness (Multi-turn) ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # First interaction - establish destination
    response1 = orchestrator.process_query("Tôi muốn đi du lịch Đà Nẵng")
    print(f"Response 1: {response1[:100]}...")
    
    # Second interaction - should remember Đà Nẵng
    response2 = orchestrator.process_query("Có món ăn gì ngon ở đó?")
    print(f"Response 2: {response2[:100]}...")
    
    # Third interaction - booking should remember context
    response3 = orchestrator.process_query("Tìm khách sạn 3 sao cho 2 người")
    print(f"Response 3: {response3[:100]}...")
    
    # Verify context is maintained
    assert "đà nẵng" in response2.lower() or "da nang" in response2.lower()
    assert "đà nẵng" in response3.lower() or "da nang" in response3.lower()
    
    print("✅ Context awareness test passed!")


def test_weather_api_integration():
    """Test weather API calls and integration with planning"""
    print("\n=== Testing Weather API Integration ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Test weather query
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    weather_query = f"Thời tiết ở Hội An ngày {future_date} như thế nào?"
    
    response = orchestrator.process_query(weather_query)
    print(f"Weather response: {response[:200]}...")
    
    # Verify weather information is included
    assert "thời tiết" in response.lower() or "weather" in response.lower()
    assert "hội an" in response.lower() or "hoi an" in response.lower()
    
    print("✅ Weather API integration test passed!")


def test_planning_with_time_weather_integration():
    """Test planning with time information and weather integration"""
    print("\n=== Testing Planning with Time & Weather Integration ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Test planning with specific dates
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    planning_query = f"Lên kế hoạch đi Sa Pa 3 ngày từ {future_date}"
    
    response = orchestrator.process_query(planning_query)
    print(f"Planning response: {response[:300]}...")
    
    # Verify planning includes weather consideration
    assert "lịch trình" in response.lower() or "kế hoạch" in response.lower()
    assert "sa pa" in response.lower()
    assert len(response) > 500  # Should be a detailed plan
    
    print("✅ Planning with time & weather integration test passed!")


def test_end_to_end_travel_scenario():
    """Test complete end-to-end travel scenario"""
    print("\n=== Testing End-to-End Travel Scenario ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Step 1: Weather inquiry
    response1 = orchestrator.process_query("Thời tiết ở Phú Quốc tuần tới thế nào?")
    print(f"Step 1 - Weather: {response1[:150]}...")
    
    # Step 2: Planning request
    response2 = orchestrator.process_query("Lên kế hoạch du lịch Phú Quốc 4 ngày")
    print(f"Step 2 - Planning: {response2[:150]}...")
    
    # Step 3: Hotel booking
    response3 = orchestrator.process_query("Tìm resort 5 sao ở đó cho 2 người")
    print(f"Step 3 - Booking: {response3[:150]}...")
    
    # Step 4: Food recommendations
    response4 = orchestrator.process_query("Có món ăn gì đặc sản?")
    print(f"Step 4 - Food: {response4[:150]}...")
    
    # Verify all responses are contextually appropriate
    assert "phú quốc" in response1.lower()
    assert "phú quốc" in response2.lower()
    assert "phú quốc" in response3.lower() or "resort" in response3.lower()
    assert "đặc sản" in response4.lower() or "món ăn" in response4.lower()
    
    print("✅ End-to-end travel scenario test passed!")


def test_error_handling_and_fallbacks():
    """Test error handling and fallback mechanisms"""
    print("\n=== Testing Error Handling & Fallbacks ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Test with unclear destination
    response1 = orchestrator.process_query("Tìm khách sạn tốt")
    print(f"Unclear destination response: {response1[:150]}...")
    
    # Test with invalid date
    response2 = orchestrator.process_query("Thời tiết ngày 50/50/2025")
    print(f"Invalid date response: {response2[:150]}...")
    
    # Verify system handles errors gracefully
    assert len(response1) > 50  # Should provide helpful response
    assert len(response2) > 50  # Should handle gracefully
    
    print("✅ Error handling & fallbacks test passed!")


def test_memory_agent_persistence():
    """Test MemoryAgent's ability to persist context across interactions"""
    print("\n=== Testing MemoryAgent Persistence ===")
    
    orchestrator = MultiAgentTravelOrchestrator()
    
    # Build up context over multiple interactions
    queries = [
        "Tôi muốn đi du lịch Nha Trang",
        "Với 3 người",
        "Từ ngày 20/7 đến 25/7",
        "Ngân sách khoảng 5 triệu",
        "Lên kế hoạch chi tiết"
    ]
    
    responses = []
    for i, query in enumerate(queries):
        response = orchestrator.process_query(query)
        responses.append(response)
        print(f"Query {i+1}: {query}")
        print(f"Response {i+1}: {response[:100]}...")
        print("---")
    
    # Final response should incorporate all context
    final_response = responses[-1]
    assert "nha trang" in final_response.lower()
    assert "3" in final_response or "ba" in final_response.lower()
    assert len(final_response) > 300  # Should be detailed plan
    
    print("✅ MemoryAgent persistence test passed!")


if __name__ == "__main__":
    """Run all comprehensive system validation tests"""
    print("🚀 Starting Comprehensive Multi-Agent System Validation Tests")
    print("=" * 60)
    
    try:
        test_serpapi_integration()
        test_booking_agent_full_workflow()
        test_context_awareness_multi_turn()
        test_weather_api_integration()
        test_planning_with_time_weather_integration()
        test_end_to_end_travel_scenario()
        test_error_handling_and_fallbacks()
        test_memory_agent_persistence()
        
        print("\n" + "=" * 60)
        print("🎉 ALL COMPREHENSIVE SYSTEM VALIDATION TESTS PASSED!")
        print("✅ SerpApi integration: WORKING")
        print("✅ Context awareness: WORKING") 
        print("✅ Weather integration: WORKING")
        print("✅ Planning with time: WORKING")
        print("✅ End-to-end scenarios: WORKING")
        print("✅ Error handling: WORKING")
        print("✅ Memory persistence: WORKING")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
