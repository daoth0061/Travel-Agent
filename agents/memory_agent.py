"""
Memory Agent for tracking conversation history and providing context
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class MemoryAgent:
    """
    Persistent component that tracks the entire conversation history.
    Provides relevant context to the OrchestratorAgent for follow-up questions.
    """
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_context: Dict[str, Any] = {
            "current_destination": None,
            "current_trip_length": None,
            "current_dates": None,
            "preferences": {},
            "last_intent": None,
            "last_results": {}
        }
    
    def add_interaction(self, user_query: str, intent: str, agent_used: str, 
                       result: str, extracted_info: Dict[str, Any] = None):
        """Add a new interaction to the conversation history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "intent": intent,
            "agent_used": agent_used,
            "result": result,
            "extracted_info": extracted_info or {}
        }
        
        self.conversation_history.append(interaction)
        
        # Update current context
        if extracted_info:
            if "destination" in extracted_info:
                self.user_context["current_destination"] = extracted_info["destination"]
            if "trip_length" in extracted_info:
                self.user_context["current_trip_length"] = extracted_info["trip_length"]
            if "dates" in extracted_info:
                self.user_context["current_dates"] = extracted_info["dates"]
            if "preferences" in extracted_info:
                self.user_context["preferences"].update(extracted_info["preferences"])
        
        self.user_context["last_intent"] = intent
        self.user_context["last_results"][agent_used] = result
    
    def get_relevant_context(self, current_query: str, intent: str) -> Dict[str, Any]:
        """Get relevant context for the current query"""
        context = {
            "current_context": self.user_context.copy(),
            "is_follow_up": self._is_follow_up_question(current_query, intent),
            "recent_interactions": self.conversation_history[-3:] if self.conversation_history else [],
            "relevant_history": self._find_relevant_history(current_query, intent)
        }
        
        return context
    
    def _is_follow_up_question(self, query: str, intent: str) -> bool:
        """Determine if this is a follow-up question"""
        follow_up_indicators = [
            "còn", "thêm", "khác", "nữa", "other", "more", "also", "additionally",
            "what about", "how about", "còn gì", "và", "or", "hoặc"
        ]
        
        query_lower = query.lower()
        has_follow_up_words = any(indicator in query_lower for indicator in follow_up_indicators)
        
        # If no specific destination mentioned but we have current context
        has_contextual_reference = (
            self.user_context["current_destination"] and 
            self.user_context["current_destination"].lower() not in query_lower
        )
        
        # Recent interaction exists
        has_recent_context = len(self.conversation_history) > 0
        
        return (has_follow_up_words or has_contextual_reference) and has_recent_context
    
    def _find_relevant_history(self, query: str, intent: str) -> List[Dict[str, Any]]:
        """Find relevant historical interactions"""
        relevant = []
        
        # Get interactions with same intent
        for interaction in self.conversation_history:
            if interaction["intent"] == intent:
                relevant.append(interaction)
        
        # Limit to most recent 2 relevant interactions
        return relevant[-2:] if relevant else []
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation state"""
        if not self.conversation_history:
            return "Chưa có lịch sử trò chuyện."
        
        context = self.user_context
        summary = f"""
📝 Tóm tắt cuộc trò chuyện:
🎯 Điểm đến hiện tại: {context['current_destination'] or 'Chưa xác định'}
📅 Thời gian dự kiến: {context['current_trip_length'] or 'Chưa xác định'} ngày
📆 Ngày khởi hành: {context['current_dates'] or 'Chưa xác định'}
🎨 Sở thích đã biết: {', '.join(context['preferences'].keys()) if context['preferences'] else 'Chưa có'}
🔄 Yêu cầu gần nhất: {context['last_intent'] or 'Chưa có'}
💬 Tổng số tương tác: {len(self.conversation_history)}
"""
        return summary.strip()
    
    def clear_context(self):
        """Clear current context while keeping history"""
        self.user_context = {
            "current_destination": None,
            "current_trip_length": None,
            "current_dates": None,
            "preferences": {},
            "last_intent": None,
            "last_results": {}
        }
    
    def save_to_file(self, filepath: str):
        """Save conversation history to file"""
        data = {
            "conversation_history": self.conversation_history,
            "user_context": self.user_context
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load conversation history from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.conversation_history = data.get("conversation_history", [])
            self.user_context = data.get("user_context", {
                "current_destination": None,
                "current_trip_length": None,
                "current_dates": None,
                "preferences": {},
                "last_intent": None,
                "last_results": {}
            })
        except FileNotFoundError:
            pass  # Keep empty history if file doesn't exist
