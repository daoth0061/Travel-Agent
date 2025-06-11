"""
Multi-Agent Travel Assistant System
Sophisticated orchestrator with intent classification and context-aware routing
"""
import os
from crewai import Crew, Process
from agents.location_agent import EnhancedLocationAgent
from agents.food_agent import EnhancedFoodAgent
from agents.itinerary_agent import AdvancedItineraryAgent
from agents.booking_agent import BookingAgent
from agents.default_agent import DefaultAgent
from agents.memory_agent import MemoryAgent
from tools.rag_tools import TravelRAGTools
from tools.vector_store import TravelRAGSystem
from data.travel_data import TRAVEL_DATA
from core.config import settings
from core.utils import classify_intent, detect_destination, extract_preferences
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional


class MultiAgentTravelOrchestrator:
    """
    Central coordinator that receives all user queries, classifies intent,
    and delegates tasks to appropriate specialist agents.
    """
    
    def __init__(self):
        # Initialize RAG system
        self.rag_system = TravelRAGSystem(
            settings["rag_config"], 
            settings["chroma_path"], 
            TRAVEL_DATA
        )
        self.rag_system.setup_vectorstore(force_rebuild=False)
        self.rag_tools = TravelRAGTools(self.rag_system)
        
        # Initialize LLMs
        self.llm_gpt35 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.llm_gpt4 = ChatOpenAI(model="gpt-4o-mini", temperature=0.25)
        
        # Initialize Memory Agent
        self.memory_agent = MemoryAgent()
        
        # Initialize specialist agents
        self.food_agent = EnhancedFoodAgent(self.llm_gpt35, self.rag_tools)
        self.location_agent = EnhancedLocationAgent(self.llm_gpt35, self.rag_tools)
        self.itinerary_agent = AdvancedItineraryAgent(
            self.llm_gpt4, self.rag_tools, self.food_agent, self.location_agent
        )
        self.booking_agent = BookingAgent(self.llm_gpt35)
        self.default_agent = DefaultAgent(self.llm_gpt35)
        
        print("🤖 Multi-Agent Travel Assistant System initialized successfully!")
    
    def process_query(self, user_query: str) -> str:
        """
        Main entry point for processing user queries.
        Implements the complete workflow: intent classification → context analysis → agent routing
        """
        print(f"🔍 Processing query: {user_query}")
        
        # Step 1: Get relevant context from memory
        context = self.memory_agent.get_relevant_context(user_query)
        print(f"📚 Context analysis: {'Follow-up' if context.get('is_follow_up') else 'New query'}")
        
        # Step 2: Classify intent
        intent = classify_intent(user_query)
        print(f"🎯 Detected intent: {intent}")
        
        # Step 3: Route to appropriate agent
        response = self._route_to_agent(user_query, intent, context)
        
        # Step 4: Update memory with interaction
        self._update_memory(user_query, intent, response, context)
        
        return response
    
    def _route_to_agent(self, query: str, intent: str, context: Dict[str, Any]) -> str:
        """
        Route query to appropriate agent based on intent and context
        """
        try:
            if intent == "eat":
                return self._handle_food_query(query, context)
            elif intent == "visit":
                return self._handle_location_query(query, context)
            elif intent == "plan":
                return self._handle_itinerary_query(query, context)
            elif intent == "book":
                return self._handle_booking_query(query, context)
            else:  # intent == "other"
                return self._handle_general_query(query, context)
        except Exception as e:
            print(f"❌ Error in agent routing: {e}")
            return f"Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn: {str(e)}"
    
    def _handle_food_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle food-related queries using FoodAgent"""
        print("🍽️ Routing to FoodAgent...")
        
        # Extract or use context destination
        destination = detect_destination(query)
        if not destination and context.get("current_context", {}).get("current_destination"):
            destination = context["current_context"]["current_destination"]
        
        if not destination:
            return ("Để tôi có thể gợi ý món ăn tốt nhất, bạn có thể cho tôi biết "
                   "bạn muốn tìm hiểu ẩm thực ở đâu không?")
        
        # Create and execute food task
        task = self.food_agent.create_task(query, destination)
        crew = Crew(
            agents=[self.food_agent.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        return f"🍜 **GỢI Ý ẨM THỰC TẠI {destination.upper()}**\\n\\n{str(result)}"
    
    def _handle_location_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle location/attraction queries using LocationAgent"""
        print("🏛️ Routing to LocationAgent...")
        
        # Extract or use context destination
        destination = detect_destination(query)
        if not destination and context.get("current_context", {}).get("current_destination"):
            destination = context["current_context"]["current_destination"]
        
        if not destination:
            return ("Để tôi có thể gợi ý địa điểm tham quan phù hợp, bạn có thể "
                   "cho tôi biết bạn muốn đi đâu không?")
        
        # Create and execute location task
        task = self.location_agent.create_task(query, destination)
        crew = Crew(
            agents=[self.location_agent.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        return f"🗺️ **ĐỊA ĐIỂM THAM QUAN TẠI {destination.upper()}**\\n\\n{str(result)}"
    
    def _handle_itinerary_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle itinerary planning using AdvancedItineraryAgent"""
        print("📅 Routing to AdvancedItineraryAgent...")
        
        # The ItineraryAgent handles its own parameter extraction and resource gathering
        task = self.itinerary_agent.create_task(query, context)
        
        # Check if we need to gather resources first
        destination = detect_destination(query)
        if destination:
            print(f"🔄 Complex itinerary planning for {destination}...")
            
            # The ItineraryAgent will internally call FoodAgent and LocationAgent
            # This is handled in its create_task method
            crew = Crew(
                agents=[
                    self.itinerary_agent.agent,
                    self.food_agent.agent,
                    self.location_agent.agent
                ],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
        else:
            # Simple case or need destination clarification
            crew = Crew(
                agents=[self.itinerary_agent.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
        
        result = crew.kickoff()
        return f"📋 **LỊCH TRÌNH DU LỊCH CHI TIẾT**\\n\\n{str(result)}"
    
    def _handle_booking_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle booking requests using BookingAgent"""
        print("🏨 Routing to BookingAgent...")
        
        task = self.booking_agent.create_task(query, context)
        crew = Crew(
            agents=[self.booking_agent.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        return f"🏨 **THÔNG TIN KHÁCH SẠN & ĐẶT PHÒNG**\\n\\n{str(result)}"
    
    def _handle_general_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle general queries using DefaultAgent"""
        print("🤖 Routing to DefaultAgent...")
        
        task = self.default_agent.create_task(query, context)
        crew = Crew(
            agents=[self.default_agent.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        return f"💡 **THÔNG TIN DU LỊCH TỔNG QUÁT**\\n\\n{str(result)}"
    
    def _update_memory(self, query: str, intent: str, response: str, context: Dict[str, Any]):
        """Update memory with current interaction"""
        # Extract key information for context
        destination = detect_destination(query)
        preferences = extract_preferences(query)
        
        interaction_context = {
            "destination": destination,
            "preferences": preferences,
            "query_length": len(query),
            "response_length": len(response)
        }
        
        # Determine which agent was used
        agent_used = {
            "eat": "FoodAgent",
            "visit": "LocationAgent", 
            "plan": "ItineraryAgent",
            "book": "BookingAgent",
            "other": "DefaultAgent"
        }.get(intent, "Unknown")
        
        self.memory_agent.add_interaction(
            user_query=query,
            intent=intent,
            agent_used=agent_used,
            response=response[:500] + "..." if len(response) > 500 else response,  # Truncate for memory
            context=interaction_context
        )
        
        # Update user preferences
        if preferences:
            self.memory_agent.update_user_preferences(preferences)
    
    def get_conversation_history(self) -> str:
        """Get conversation history summary"""
        return self.memory_agent.get_conversation_summary()
    
    def clear_conversation(self):
        """Clear conversation history and context"""
        self.memory_agent.clear_context()
        print("🗑️ Conversation history cleared.")
    
    def run_interactive(self):
        """Run interactive chat mode"""
        print("="*80)
        print("🌟 MULTI-AGENT TRAVEL ASSISTANT SYSTEM 🌟")
        print("="*80)
        print("💡 Bạn có thể hỏi về:")
        print("   🍽️ Ẩm thực: 'Món ăn ngon ở Hà Nội'")
        print("   🏛️ Địa điểm: 'Chỗ nào đẹp ở Sa Pa'")
        print("   📅 Lịch trình: 'Lập lịch đi Hội An 3 ngày'")
        print("   🏨 Đặt phòng: 'Tìm khách sạn ở Đà Nẵng'")
        print("   💬 Chung: 'Tiền tệ Việt Nam là gì?'")
        print("\\n⌨️ Gõ 'quit' để thoát, 'history' để xem lịch sử, 'clear' để xóa lịch sử")
        print("-"*80)
        
        while True:
            try:
                user_input = input("\\n👤 Bạn: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'thoát']:
                    print("👋 Cảm ơn bạn đã sử dụng hệ thống. Chúc bạn có chuyến đi vui vẻ!")
                    break
                elif user_input.lower() in ['history', 'lịch sử']:
                    print("\\n📚", self.get_conversation_history())
                    continue
                elif user_input.lower() in ['clear', 'xóa']:
                    self.clear_conversation()
                    continue
                elif not user_input:
                    print("⚠️ Vui lòng nhập câu hỏi của bạn.")
                    continue
                
                print("\\n🤖 Hệ thống:")
                response = self.process_query(user_input)
                print(f"\\n{response}")
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Tạm biệt!")
                break
            except Exception as e:
                print(f"\\n❌ Đã có lỗi xảy ra: {e}")


# Convenience function for the existing system
def run_simple_query(user_query: str) -> str:
    """
    Simple function for backward compatibility with existing code
    """
    orchestrator = MultiAgentTravelOrchestrator()
    return orchestrator.process_query(user_query)


if __name__ == "__main__":
    # Run interactive mode
    orchestrator = MultiAgentTravelOrchestrator()
    orchestrator.run_interactive()
