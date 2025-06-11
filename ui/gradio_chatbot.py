"""
Gradio Chatbot UI for Multi-Agent Travel Assistant System
Beautiful, user-friendly interface with advanced features
"""
import gradio as gr
import sys
import os
import json
import time
from datetime import datetime
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator
    from core.utils import classify_intent
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all dependencies are installed and the project structure is correct.")
    sys.exit(1)

class TravelChatbotUI:
    """
    Gradio-based chatbot interface for the travel assistant system
    """
    
    def __init__(self):
        self.orchestrator = None
        self.chat_history = []
        self.system_stats = {
            "total_queries": 0,
            "queries_by_intent": {},
            "session_start": datetime.now()
        }
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the multi-agent orchestrator"""
        try:
            print("🚀 Initializing Multi-Agent Travel Assistant System...")
            self.orchestrator = MultiAgentTravelOrchestrator()
            print("✅ System initialized successfully!")
            return "✅ System Ready"
        except Exception as e:
            error_msg = f"❌ Failed to initialize system: {str(e)}"
            print(error_msg)
            return error_msg
    
    def process_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Process user message and return response with updated history
        """
        if not self.orchestrator:
            error_response = "❌ System not initialized. Please restart the application."
            history.append((message, error_response))
            return "", history
        
        if not message.strip():
            return "", history
        
        try:
            # Show typing indicator
            typing_response = "🤖 Đang suy nghĩ..."
            history.append((message, typing_response))
            
            # Process the query
            start_time = time.time()
            response = self.orchestrator.process_query(message)
            processing_time = time.time() - start_time
            
            # Update statistics
            self.update_stats(message, processing_time)
            
            # Update history with actual response
            history[-1] = (message, response)
            
            return "", history
            
        except Exception as e:
            error_response = f"❌ Đã có lỗi xảy ra: {str(e)}"
            history[-1] = (message, error_response)
            return "", history
    
    def update_stats(self, message: str, processing_time: float):
        """Update system statistics"""
        self.system_stats["total_queries"] += 1
        
        try:
            intent = classify_intent(message)
            if intent in self.system_stats["queries_by_intent"]:
                self.system_stats["queries_by_intent"][intent] += 1
            else:
                self.system_stats["queries_by_intent"][intent] = 1
        except:
            pass
    
    def clear_conversation(self):
        """Clear conversation history"""
        if self.orchestrator:
            self.orchestrator.clear_conversation()
        return []
    
    def get_conversation_history(self):
        """Get conversation history summary"""
        if self.orchestrator:
            return self.orchestrator.get_conversation_history()
        return "No conversation history available."
    
    def get_system_stats(self):
        """Get system statistics"""
        uptime = datetime.now() - self.system_stats["session_start"]
        
        stats_text = f"""
📊 **System Statistics**
⏱️ Uptime: {str(uptime).split('.')[0]}
📝 Total Queries: {self.system_stats['total_queries']}

📈 **Queries by Intent:**
"""
        for intent, count in self.system_stats["queries_by_intent"].items():
            intent_emoji = {
                "eat": "🍽️",
                "visit": "🏛️", 
                "plan": "📅",
                "book": "🏨",
                "other": "💬"
            }.get(intent, "❓")
            stats_text += f"{intent_emoji} {intent}: {count}\n"
        
        return stats_text
    
    def get_example_queries(self):
        """Get example queries for different intents"""
        examples = {
            "🍽️ Ẩm thực": [
                "Món ăn ngon ở Hà Nội có gì?",
                "Đặc sản Sa Pa nổi tiếng",
                "Quán ăn đường phố Hội An"
            ],
            "🏛️ Địa điểm": [
                "Chỗ nào đẹp ở Đà Nẵng để chụp ảnh?",
                "Điểm tham quan nổi tiếng ở Sa Pa",
                "Bảo tàng ở Hà Nội"
            ],
            "📅 Lịch trình": [
                "Lập lịch đi Hội An 3 ngày từ 15/6/2025",
                "Du lịch Sa Pa 2 ngày cuối tuần này",
                "Kế hoạch đi Hà Nội 4 ngày"
            ],
            "🏨 Khách sạn": [
                "Tìm khách sạn tốt ở Đà Nẵng",
                "Đặt phòng resort Phú Quốc cho 2 người",
                "Homestay giá rẻ ở Sa Pa"
            ],
            "💬 Thông tin chung": [
                "Tiền tệ Việt Nam là gì?",
                "Thời tiết Việt Nam như thế nào?",
                "Cần giấy tờ gì để đi du lịch?"
            ]
        }
        
        example_text = "## 💡 Câu hỏi mẫu:\n\n"
        for category, queries in examples.items():
            example_text += f"### {category}\n"
            for query in queries:
                example_text += f"• {query}\n"
            example_text += "\n"
        
        return example_text

def create_chatbot_interface():
    """Create the main Gradio interface"""
    
    # Initialize the chatbot
    chatbot_ui = TravelChatbotUI()
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: auto !important;
    }
    .chat-message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .header-title {
        text-align: center;
        color: #1976d2;
        margin-bottom: 20px;
    }
    .stats-panel {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    """
    
    # Create the interface
    with gr.Blocks(
        css=custom_css,
        title="🌟 AI Travel Assistant",
        theme=gr.themes.Soft()
    ) as demo:
        
        # Header
        gr.HTML("""
        <div class="header-title">
            <h1>🌟 Multi-Agent Travel Assistant System</h1>
            <p>Hệ thống AI tư vấn du lịch thông minh với nhiều chuyên gia ảo</p>
        </div>
        """)
        
        # Main chat interface
        with gr.Row():
            with gr.Column(scale=3):
                # Chatbot
                chatbot = gr.Chatbot(
                    label="💬 Chat với AI Travel Assistant",
                    placeholder="Chào bạn! Tôi là trợ lý du lịch AI. Hãy hỏi tôi về ẩm thực, địa điểm, lịch trình hoặc đặt phòng!",
                    height=500,
                    show_copy_button=True
                )
                
                # Input area
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Nhập câu hỏi của bạn... (VD: 'Món ăn ngon ở Hà Nội')",
                        scale=4,
                        container=False
                    )
                    send_btn = gr.Button("📤 Gửi", variant="primary", scale=1)
                
                # Action buttons
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Xóa lịch sử", variant="secondary")
                    history_btn = gr.Button("📚 Xem lịch sử", variant="secondary")
                    stats_btn = gr.Button("📊 Thống kê", variant="secondary")
            
            # Sidebar with information
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h3>🤖 Các chuyên gia AI:</h3>
                    <ul>
                        <li>🍽️ <strong>FoodAgent</strong>: Ẩm thực</li>
                        <li>🏛️ <strong>LocationAgent</strong>: Địa điểm</li>
                        <li>📅 <strong>ItineraryAgent</strong>: Lịch trình</li>
                        <li>🏨 <strong>BookingAgent</strong>: Đặt phòng</li>
                        <li>💬 <strong>DefaultAgent</strong>: Tư vấn chung</li>
                    </ul>
                </div>
                """)
                
                # System status
                system_status = gr.HTML(
                    value="<div class='stats-panel'>📊 <strong>Trạng thái:</strong><br/>✅ Hệ thống sẵn sàng</div>"
                )
                
                # Weather info
                gr.HTML("""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; margin: 15px 0;">
                    <h4>🌤️ Tính năng thời tiết:</h4>
                    <p>• Dự báo thời tiết real-time</p>
                    <p>• Tối ưu hoạt động theo thời tiết</p>
                    <p>• Gợi ý trang phục phù hợp</p>
                </div>
                """)
        
        # Examples section
        with gr.Accordion("💡 Câu hỏi mẫu", open=False):
            examples_display = gr.Markdown(chatbot_ui.get_example_queries())
        
        # Information modals
        with gr.Row():
            history_output = gr.Textbox(
                label="📚 Lịch sử cuộc trò chuyện",
                visible=False,
                max_lines=10
            )
            stats_output = gr.Textbox(
                label="📊 Thống kê hệ thống",
                visible=False,
                max_lines=10
            )
        
        # Event handlers
        def submit_message(message, history):
            """Handle message submission"""
            return chatbot_ui.process_message(message, history)
        
        def show_hide_history():
            """Toggle history visibility"""
            history_text = chatbot_ui.get_conversation_history()
            return gr.update(visible=True, value=history_text)
        
        def show_hide_stats():
            """Toggle stats visibility"""
            stats_text = chatbot_ui.get_system_stats()
            return gr.update(visible=True, value=stats_text)
        
        def clear_chat():
            """Clear chat history"""
            chatbot_ui.clear_conversation()
            return []
        
        # Wire up events
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=True
        )
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=True
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=chatbot
        )
        
        history_btn.click(
            fn=show_hide_history,
            outputs=history_output
        )
        
        stats_btn.click(
            fn=show_hide_stats,
            outputs=stats_output
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd;">
            <p>🌟 <strong>Multi-Agent Travel Assistant System</strong> 🌟</p>
            <p>Powered by CrewAI, LangChain, WeatherAPI.com & OpenAI</p>
            <p><em>Hệ thống AI tư vấn du lịch thông minh cho Việt Nam</em></p>
        </div>
        """)
    
    return demo

def main():
    """Main function to launch the Gradio interface"""
    print("🚀 Starting Gradio Chatbot UI...")
    
    try:
        # Create and launch the interface
        demo = create_chatbot_interface()
        
        # Launch with custom settings
        demo.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,       # Default Gradio port
            share=False,            # Set to True to create shareable link
            debug=True,             # Enable debug mode
            show_error=True,        # Show error messages
            inbrowser=True,         # Open in browser automatically
            favicon_path=None,      # Add custom favicon if available
            auth=None,              # Add authentication if needed
            max_threads=10          # Handle multiple concurrent users
        )
        
    except Exception as e:
        print(f"❌ Failed to start Gradio interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
