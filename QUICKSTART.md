# Quick Start Guide - Multi-Agent Travel Assistant System

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys:
# WEATHERAPI_KEY=your_weatherapi_key_here
# OPENAI_API_KEY=your_openai_key_here
# RAPIDAPI_KEY=your_rapidapi_key_here (optional, for hotel booking)
```

### 3. Download Travel Database
Download the `chroma_travel_db/` folder and place it in the `data/` directory.

### 4. Run the System
```bash
# Interactive chat mode
python core/main.py

# Or run tests
python tests/test_multi_agent_system.py
```

## 💬 Example Conversations

### Food Recommendations
```
You: Món ăn ngon ở Hà Nội có gì?
System: 🍜 **GỢI Ý ẨM THỰC TẠI HÀ NỘI**
        Phở Bò, Bún Chả, Chả Cá Lã Vọng...
```

### Location Planning
```
You: Chỗ nào đẹp ở Sa Pa để chụp ảnh?
System: 🗺️ **ĐỊA ĐIỂM THAM QUAN TẠI SA PA**
        Fansipan, Ruộng Bậc Thang, Thác Bạc...
```

### Complete Itinerary
```
You: Lập lịch đi Hội An 3 ngày từ 15/6/2025
System: 📋 **LỊCH TRÌNH DU LỊCH CHI TIẾT**
        NGÀY 1 (2025-06-15)
        🌤️ Thời tiết: 28°C, Sunny
        🌅 Sáng (8:00): Phố Cổ Hội An...
```

### Follow-up Questions
```
You: Lập lịch đi Sa Pa 3 ngày
System: [Creates itinerary]

You: Thay đổi thành 2 ngày được không?
System: [Automatically understands context and modifies the Sa Pa plan]
```

### Hotel Booking
```
You: Tìm khách sạn tốt ở Đà Nẵng cho 2 người
System: 🏨 **THÔNG TIN KHÁCH SẠN & ĐẶT PHÒNG**
        Recommended hotels with pricing...
```

### General Questions
```
You: Tiền tệ Việt Nam là gì?
System: 💡 **THÔNG TIN DU LỊCH TỔNG QUÁT**
        Đơn vị tiền tệ: Đồng Việt Nam (VND)...
```

## 🎯 Intent Recognition

The system automatically detects what you want:

| Your Words | Intent | Agent Used |
|------------|--------|------------|
| "ăn", "món", "quán" | eat | FoodAgent |
| "đi", "tham quan", "chỗ" | visit | LocationAgent |
| "lịch trình", "kế hoạch" | plan | ItineraryAgent |
| "đặt", "khách sạn" | book | BookingAgent |
| "tiền tệ", "visa" | other | DefaultAgent |

## 🧠 Smart Features

### Context Memory
- Remembers your conversation
- Handles follow-up questions naturally
- Learns your preferences over time

### Weather Intelligence
- Real-time weather integration
- Hour-specific activity optimization
- Automatic indoor/outdoor recommendations

### Robust Processing
- Handles misspellings ("Sa-pa" → "Sa Pa")
- Understands Vietnamese numbers ("hai ngày" → 2 days)
- Flexible date formats ("ngày mai", "15/6/2025")

## 🔧 Advanced Usage

### Programmatic Access
```python
from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

orchestrator = MultiAgentTravelOrchestrator()

# Process single query
response = orchestrator.process_query("Món ăn ngon ở Hà Nội")

# Get conversation history
history = orchestrator.get_conversation_history()

# Clear conversation context
orchestrator.clear_conversation()
```

### Custom Configuration
Edit `configs/settings.yaml` to customize:
- RAG chunk sizes
- Model temperatures
- Vector database settings

## 🆘 Troubleshooting

### Common Issues

**"No WeatherAPI key found"**
```bash
# Add to .env file:
WEATHERAPI_KEY=your_key_here
```

**"Vector database not found"**
```bash
# Download chroma_travel_db/ to data/ folder
# Or set force_rebuild=True in orchestrator.py
```

**"Import errors"**
```bash
pip install -r requirements.txt
```

### Need Help?

1. Run the test suite: `python tests/test_multi_agent_system.py`
2. Check logs for detailed error messages
3. Verify all API keys are configured correctly
4. Ensure the travel database is downloaded

## 🎉 You're Ready!

Start chatting with your AI travel assistant:
```bash
python core/main.py
```

The system will guide you through creating amazing travel experiences! 🌟
