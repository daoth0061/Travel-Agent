# Multi-Agent Travel Assistant System

A sophisticated AI-powered travel planning system that uses multiple specialized agents working in concert to provide comprehensive travel assistance. The system features intelligent intent classification, context-aware conversations, and real-time weather integration.

## 🤖 Multi-Agent Architecture

### Core Agents

1. **🎯 OrchestratorAgent** - Central coordinator that classifies user intent and routes queries to specialist agents
2. **🍽️ FoodAgent** - Specializes in food recommendations using RAG system  
3. **🏛️ LocationAgent** - Specializes in sightseeing and attraction recommendations using RAG system
4. **📅 ItineraryAgent** - Creates detailed multi-day travel plans by synthesizing information from other agents
5. **🏨 BookingAgent** - Handles accommodation booking requests with hotel APIs
6. **🤖 DefaultAgent** - Handles general travel questions (currency, visa, culture, etc.)
7. **🧠 MemoryAgent** - Tracks conversation history for context-aware follow-up questions

### Intent Classification & Routing

The system automatically classifies user queries into intents:
- **eat**: Food recommendations → FoodAgent
- **visit**: Location/attraction recommendations → LocationAgent  
- **plan**: Travel itinerary creation → ItineraryAgent
- **book**: Hotel/accommodation booking → BookingAgent
- **other**: General questions → DefaultAgent

## 🌟 Advanced Features

### Sophisticated Itinerary Planning

The ItineraryAgent implements two advanced planning scenarios:

#### Scenario A: PlanningWithoutTime
- Creates logical itinerary flow without specific dates
- Implements "Plan Overwhelm Logic":
  - **2-3 days**: Final afternoon = shopping for souvenirs
  - **4+ days**: Entire last day = "Free & Easy Day"
- Resource calculation:
  - **Food items**: 2 × days (lunch + dinner each day)
  - **Location items**: 
    - 1 day: 2 locations
    - 2-3 days: 2×days - 1 (last afternoon for shopping)
    - 4+ days: 2×days - 2 (last day is free)

#### Scenario B: PlanningWithTime  
- Weather-enhanced planning with specific dates
- Hour-specific weather forecasts (8AM, 12PM, 4PM, 8PM)
- Activity optimization based on real-time weather
- Weather-adaptive recommendations (indoor/outdoor activities)

### Context-Aware Conversations
- Persistent memory across conversation sessions
- Follow-up question handling with relevant context
- User preference learning and adaptation
- Natural conversation flow with intelligent routing

### Real-Time Weather Integration
- **Current Conditions**: Temperature, humidity, wind, UV index, air quality
- **Multi-Day Forecasts**: Up to 14-day weather forecasts with alerts
- **Hourly Forecasts**: Detailed hour-by-hour planning for 4 daily periods
- **Weather-Adaptive Scheduling**: Activities optimized for weather conditions

## 🛠️ Setup Instructions

### 1. Download Required Dataset

**Download the `chroma_travel_db/` folder**  
Download the [`chroma_travel_db/` folder from Google Drive`](https://drive.google.com/your_link_here).

**Place the folder in the correct location**  
Move or copy the downloaded `chroma_travel_db/` folder into the `data/` directory of this project.

### 2. Configure API Keys

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Get your WeatherAPI.com API key:
   - Sign up at [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)
   - Get your free API key (supports 1M calls/month)

3. Edit `.env` file and add your API keys:
   ```bash
   WEATHERAPI_KEY=your_weatherapi_com_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the System

```bash
python core/main.py
```

## 🌤️ Weather Integration Features

### Real-Time Weather Data
- **Current Conditions**: Temperature, humidity, wind, UV index, air quality
- **Multi-Day Forecasts**: Up to 14-day weather forecasts
- **Weather Alerts**: Severe weather warnings and advisories
- **Hourly Forecasts**: Detailed hour-by-hour weather data

### Time-Specific Planning
The system optimizes activities for 4 key time periods:
- **🌅 Sáng (8:00 AM)**: Morning activities planning
- **☀️ Trưa (12:00 PM)**: Midday activity recommendations
- **🌤️ Chiều (4:00 PM)**: Afternoon tourism optimization
- **🌙 Tối (8:00 PM)**: Evening activity scheduling

### Weather-Adaptive Recommendations
- Indoor activities during rain/storms
- Shade-seeking during high temperatures
- UV protection recommendations
- Wind-resistant activity suggestions
- Seasonal clothing advice

## 📁 Project Structure

```
project_root/
├── agents/                  # AI agents for different tasks
│   ├── itinerary_agent.py  # Enhanced with weather integration
│   ├── location_agent.py   # Location recommendations
│   ├── food_agent.py      # Food recommendations
│   └── orchestrator.py    # Main coordination
├── tools/                  # AI tools and utilities
│   ├── utils_tool.py      # Weather tool (WeatherAPI.com)
│   ├── rag_tools.py       # RAG search tools
│   └── vector_store.py    # Vector database management
├── data/                   # Data storage
│   └── chroma_travel_db/   # Vector database (download required)
├── core/                   # Core system files
│   ├── main.py            # Main application entry
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions
├── test_weather.py        # Weather tool testing script
└── requirements.txt       # Python dependencies
```

## 🧪 Testing Weather Integration

Run the weather tool test to verify integration:

```bash
python test_weather.py
```

This will test:
- Current weather fetching
- Multi-day forecast retrieval
- Hour-specific weather queries
- Complete daily weather schedules

## 🔧 Usage Examples

### Simple Query Processing
```python
from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

orchestrator = MultiAgentTravelOrchestrator()

# Food recommendations
response = orchestrator.process_query("Món ăn ngon ở Hà Nội")

# Location recommendations  
response = orchestrator.process_query("Chỗ nào đẹp ở Sa Pa để chụp ảnh")

# Complete itinerary planning
response = orchestrator.process_query("Lập lịch đi Hội An 3 ngày từ 15/6/2025")

# Hotel booking
response = orchestrator.process_query("Tìm khách sạn tốt ở Đà Nẵng")

# General questions
response = orchestrator.process_query("Tiền tệ Việt Nam là gì?")
```

### Interactive Chat Mode
```python
from agents.multi_agent_orchestrator import MultiAgentTravelOrchestrator

orchestrator = MultiAgentTravelOrchestrator()
orchestrator.run_interactive()  # Starts interactive chat
```

### Context-Aware Follow-ups
```python
# First query
orchestrator.process_query("Tôi muốn đi Sa Pa 3 ngày")

# Follow-up questions automatically use context
orchestrator.process_query("Thay đổi thành 2 ngày được không?")
orchestrator.process_query("Thêm hoạt động trekking vào lịch trình")
```

## 🧪 System Workflow

### For Itinerary Planning Queries:

1. **Parameter Extraction**:
   - 🎯 Destination detection (fuzzy matching for misspellings)
   - ⏱️ Trip length detection (numbers + Vietnamese words)
   - 📅 Date/time detection (absolute, relative, natural language)

2. **Resource Calculation**:
   - 🍽️ Required food recommendations (2 × days)
   - 🏛️ Required location recommendations (based on overwhelm logic)

3. **Agent Coordination**:
   - 📞 Call FoodAgent for cuisine recommendations
   - 📞 Call LocationAgent for attraction recommendations
   - 🔄 Synthesize information into coherent itinerary

4. **Weather Enhancement** (if dates provided):
   - 🌤️ Fetch real-time weather for each day
   - ⏰ Get hourly forecasts for key time periods
   - 🎯 Optimize activities based on weather conditions
   - 💡 Generate weather-specific recommendations

The system will:
1. 🎯 Classify your intent automatically
2. 📚 Use conversation context if it's a follow-up
3. 🤖 Route to the appropriate specialist agent
4. 🔍 Search relevant information using RAG
5. 🌤️ Integrate real-time weather data (if applicable)
6. 📋 Create optimized recommendations
7. 💾 Remember the conversation for future queries

## 🌍 Supported Locations

Currently optimized for Vietnamese destinations including:
- Hanoi (Hà Nội)
- Ho Chi Minh City (TP. Hồ Chí Minh)
- Sa Pa
- Hoi An (Hội An)
- Da Nang (Đà Nẵng)
- And many more...

---

⚠️ **Note:** Ensure that the folder `chroma_travel_db/` is directly inside the `data/` folder for proper RAG functionality.

If you have any questions or run into issues, feel free to reach out!
