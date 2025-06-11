"""
Simple launcher for the Gradio Travel Chatbot UI
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ui.gradio_chatbot import main
    
    if __name__ == "__main__":
        print("🌟 Launching Travel Assistant Chatbot UI...")
        print("🔗 Access the interface at: http://localhost:7860")
        print("💡 Tip: Use Ctrl+C to stop the server")
        print("-" * 50)
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies:")
    print("pip install gradio")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching chatbot: {e}")
    sys.exit(1)
