"""
Advanced Gradio Chatbot UI with Enhanced Features
Includes image support, file export, and advanced analytics
"""
import gradio as gr
import sys
import os
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator
    from core.utils import classify_intent, detect_destination, detect_trip_length
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class AdvancedTravelChatbotUI:
    """
    Advanced Gradio interface with analytics and export features
    """
    
    def __init__(self):
        self.orchestrator = None
        self.conversation_log = []
        self.session_data = {
            "start_time": datetime.now(),
            "total_queries": 0,
            "intent_stats": {},
            "response_times": [],
            "destinations_mentioned": {},
            "trip_lengths": []
        }
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the system with progress tracking"""
        try:
            self.orchestrator = MultiAgentTravelOrchestrator()
            return "✅ System Ready - Multi-Agent Travel Assistant Initialized!"
        except Exception as e:
            return f"❌ Initialization Error: {str(e)}"
    
    def process_enhanced_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]], str]:
        """
        Enhanced message processing with analytics
        """
        if not message.strip():
            return "", history, self.get_quick_stats()
        
        try:
            # Record start time
            start_time = time.time()
            
            # Show typing indicator
            history.append((message, "🤖 Đang phân tích yêu cầu và tìm chuyên gia phù hợp..."))
            
            # Process query
            response = self.orchestrator.process_query(message)
            
            # Record analytics
            processing_time = time.time() - start_time
            self.record_analytics(message, response, processing_time)
            
            # Update history with final response
            history[-1] = (message, response)
            
            # Return updated components
            return "", history, self.get_quick_stats()
            
        except Exception as e:
            error_response = f"❌ Lỗi xử lý: {str(e)}"
            history[-1] = (message, error_response)
            return "", history, self.get_quick_stats()
    
    def record_analytics(self, message: str, response: str, processing_time: float):
        """Record detailed analytics"""
        # Basic stats
        self.session_data["total_queries"] += 1
        self.session_data["response_times"].append(processing_time)
        
        # Intent analysis
        try:
            intent = classify_intent(message)
            if intent in self.session_data["intent_stats"]:
                self.session_data["intent_stats"][intent] += 1
            else:
                self.session_data["intent_stats"][intent] = 1
        except:
            pass
        
        # Destination analysis
        try:
            destination = detect_destination(message)
            if destination:
                if destination in self.session_data["destinations_mentioned"]:
                    self.session_data["destinations_mentioned"][destination] += 1
                else:
                    self.session_data["destinations_mentioned"][destination] = 1
        except:
            pass
        
        # Trip length analysis
        try:
            trip_length = detect_trip_length(message)
            if trip_length:
                self.session_data["trip_lengths"].append(trip_length)
        except:
            pass
        
        # Log conversation
        self.conversation_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response[:200] + "..." if len(response) > 200 else response,
            "processing_time": processing_time,
            "intent": classify_intent(message),
            "destination": detect_destination(message)
        })
    
    def get_quick_stats(self) -> str:
        """Get quick statistics display"""
        avg_response_time = sum(self.session_data["response_times"]) / len(self.session_data["response_times"]) if self.session_data["response_times"] else 0
        session_duration = datetime.now() - self.session_data["start_time"]
        
        return f"""📊 **Session Stats**
⏱️ Duration: {str(session_duration).split('.')[0]}
📝 Queries: {self.session_data['total_queries']}
⚡ Avg Response: {avg_response_time:.2f}s
🎯 Top Intent: {max(self.session_data['intent_stats'], key=self.session_data['intent_stats'].get) if self.session_data['intent_stats'] else 'None'}
"""
    
    def create_analytics_chart(self):
        """Create analytics visualization"""
        if not self.session_data["intent_stats"]:
            return gr.update(visible=False)
        
        # Intent distribution pie chart
        fig = px.pie(
            values=list(self.session_data["intent_stats"].values()),
            names=list(self.session_data["intent_stats"].keys()),
            title="Distribution of Query Intents"
        )
        
        return fig
    
    def export_conversation(self):
        """Export conversation history"""
        if not self.conversation_log:
            return "No conversation data to export."
        
        # Create DataFrame
        df = pd.DataFrame(self.conversation_log)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_conversation_{timestamp}.csv"
        filepath = os.path.join("exports", filename)
        
        # Create exports directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return f"✅ Conversation exported to: {filepath}"
    
    def get_destination_insights(self):
        """Get insights about mentioned destinations"""
        if not self.session_data["destinations_mentioned"]:
            return "No destinations mentioned yet."
        
        insights = "🗺️ **Destinations Mentioned:**\n\n"
        for dest, count in sorted(self.session_data["destinations_mentioned"].items(), key=lambda x: x[1], reverse=True):
            insights += f"• **{dest}**: {count} times\n"
        
        if self.session_data["trip_lengths"]:
            avg_trip = sum(self.session_data["trip_lengths"]) / len(self.session_data["trip_lengths"])
            insights += f"\n📅 **Average Trip Length**: {avg_trip:.1f} days"
        
        return insights

def create_advanced_interface():
    """Create the advanced Gradio interface"""
    
    chatbot_ui = AdvancedTravelChatbotUI()
    
    # Enhanced CSS
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
        margin: auto !important;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stats-card {
        background: #f8f9ff;
        border: 1px solid #e1e5ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .feature-badge {
        background: #e8f5e8;
        padding: 8px 12px;
        border-radius: 20px;
        margin: 5px;
        display: inline-block;
        font-size: 12px;
        color: #2e7d32;
    }
    """
    
    with gr.Blocks(css=custom_css, title="🌟 AI Travel Assistant Pro", theme=gr.themes.Soft()) as demo:
        
        # Enhanced Header
        gr.HTML("""
        <div class="main-header">
            <h1>🌟 Multi-Agent Travel Assistant Pro</h1>
            <p>AI-Powered Travel Planning with Real-Time Analytics</p>
            <div style="margin-top: 15px;">
                <span class="feature-badge">🤖 7 AI Agents</span>
                <span class="feature-badge">🌤️ Live Weather</span>
                <span class="feature-badge">📊 Analytics</span>
                <span class="feature-badge">🗂️ Export Data</span>
            </div>
        </div>
        """)
        
        # Main Interface
        with gr.Row():
            # Chat Column
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="💬 AI Travel Assistant",
                    height=500,
                    show_copy_button=True,
                    avatar_images=("👤", "🤖")
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask about food, places, itineraries, hotels, or general travel info...",
                        scale=4,
                        container=False
                    )
                    send_btn = gr.Button("🚀 Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                    export_btn = gr.Button("📥 Export", variant="secondary")
                    insights_btn = gr.Button("🔍 Insights", variant="secondary")
            
            # Analytics Sidebar
            with gr.Column(scale=1):
                # Live Stats
                stats_display = gr.Markdown(
                    value=chatbot_ui.get_quick_stats(),
                    label="📊 Live Statistics"
                )
                
                # System Info
                gr.HTML("""
                <div class="stats-card">
                    <h4>🤖 Active AI Agents:</h4>
                    <small>
                    🎯 <strong>Orchestrator</strong> - Routes queries<br/>
                    🍽️ <strong>Food Agent</strong> - Cuisine expert<br/>
                    🏛️ <strong>Location Agent</strong> - Places expert<br/>
                    📅 <strong>Itinerary Agent</strong> - Trip planner<br/>
                    🏨 <strong>Booking Agent</strong> - Hotel finder<br/>
                    💬 <strong>Default Agent</strong> - General Q&A<br/>
                    🧠 <strong>Memory Agent</strong> - Context tracker
                    </small>
                </div>
                """)
                
                # Weather Status
                gr.HTML("""
                <div class="stats-card">
                    <h4>🌤️ Weather Integration:</h4>
                    <small>
                    ✅ Real-time forecasts<br/>
                    ✅ 14-day predictions<br/>
                    ✅ Hourly optimization<br/>
                    ✅ Activity recommendations
                    </small>
                </div>
                """)
        
        # Advanced Features Tabs
        with gr.Tabs():
            # Analytics Tab
            with gr.TabItem("📊 Analytics"):
                with gr.Row():
                    with gr.Column():
                        analytics_chart = gr.Plot(label="Query Intent Distribution")
                        refresh_chart_btn = gr.Button("🔄 Refresh Chart")
                    
                    with gr.Column():
                        destination_insights = gr.Markdown(
                            value="Start chatting to see destination insights!",
                            label="🗺️ Destination Analysis"
                        )
            
            # Examples Tab
            with gr.TabItem("💡 Examples"):
                gr.Markdown("""
                ### 🍽️ Food & Cuisine
                - "Món ăn ngon ở Hà Nội có gì?"
                - "Đặc sản Sa Pa nổi tiếng nhất"
                - "Quán ăn đường phố tốt nhất Hội An"
                
                ### 🏛️ Places & Attractions  
                - "Chỗ nào đẹp ở Đà Nẵng để chụp ảnh?"
                - "Điểm tham quan miễn phí ở TP.HCM"
                - "Núi nào ở Sa Pa dễ leo nhất?"
                
                ### 📅 Trip Planning
                - "Lập lịch đi Hội An 3 ngày từ 15/6/2025"
                - "Du lịch Sa Pa 2 ngày cuối tuần này"
                - "Kế hoạch Hà Nội 4 ngày cho gia đình"
                
                ### 🏨 Hotels & Booking
                - "Tìm khách sạn 4 sao ở Đà Nẵng"
                - "Resort biển Phú Quốc giá tốt"
                - "Homestay Sa Pa view đẹp"
                
                ### 💬 General Questions
                - "Tiền tệ Việt Nam là gì?"
                - "Mùa nào đi Việt Nam đẹp nhất?"
                - "Cần chuẩn bị gì khi đi du lịch?"
                """)
            
            # Export Tab
            with gr.TabItem("📥 Export & History"):
                with gr.Row():
                    export_status = gr.Textbox(
                        label="Export Status",
                        value="Ready to export conversation data",
                        interactive=False
                    )
                    
                with gr.Row():
                    export_csv_btn = gr.Button("📊 Export CSV", variant="primary")
                    export_json_btn = gr.Button("📋 Export JSON", variant="secondary")
                
                conversation_history = gr.Textbox(
                    label="Conversation History",
                    max_lines=15,
                    visible=False
                )
        
        # Event Handlers
        def submit_message(message, history):
            return chatbot_ui.process_enhanced_message(message, history)
        
        def refresh_analytics():
            chart = chatbot_ui.create_analytics_chart()
            insights = chatbot_ui.get_destination_insights()
            stats = chatbot_ui.get_quick_stats()
            return chart, insights, stats
        
        def export_data():
            return chatbot_ui.export_conversation()
        
        # Wire Events
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, stats_display],
            queue=True
        )
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, stats_display],
            queue=True
        )
        
        clear_btn.click(
            fn=lambda: ([], chatbot_ui.get_quick_stats()),
            outputs=[chatbot, stats_display]
        )
        
        refresh_chart_btn.click(
            fn=refresh_analytics,
            outputs=[analytics_chart, destination_insights, stats_display]
        )
        
        export_csv_btn.click(
            fn=export_data,
            outputs=export_status
        )
        
        insights_btn.click(
            fn=lambda: (chatbot_ui.get_destination_insights(), chatbot_ui.create_analytics_chart()),
            outputs=[destination_insights, analytics_chart]
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd; color: #666;">
            <p><strong>🌟 Multi-Agent Travel Assistant Pro</strong></p>
            <p>Advanced AI Travel Planning • Real-Time Analytics • Vietnamese Tourism</p>
            <p><small>Powered by CrewAI, LangChain, WeatherAPI.com & OpenAI</small></p>
        </div>
        """)
    
    return demo

def main():
    """Launch the advanced interface"""
    print("🚀 Starting Advanced Travel Chatbot UI...")
    
    try:
        demo = create_advanced_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7861,  # Different port for advanced version
            share=False,
            debug=True,
            inbrowser=True,
            show_error=True,
            max_threads=15
        )
    except Exception as e:
        print(f"❌ Failed to start advanced interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
