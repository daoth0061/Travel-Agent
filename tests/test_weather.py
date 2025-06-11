"""
Test script for the enhanced weather tool with hour-specific functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.utils_tool import RealtimeWeatherTool
from datetime import datetime
import json

def test_weather_tool():
    """Test the enhanced weather tool functionality"""
    print("=" * 60)
    print("🌤️  TESTING ENHANCED WEATHER TOOL")
    print("=" * 60)
    
    # Initialize the weather tool
    weather_tool = RealtimeWeatherTool()
    
    # Test cities
    test_cities = ["Hanoi", "Sa Pa", "Hoi An"]
    
    for city in test_cities:
        print(f"\n🏙️  Testing weather for: {city}")
        print("-" * 40)
        
        # Test 1: Current weather
        print("1️⃣  Current Weather:")
        try:
            current_weather = weather_tool._run(city=city, days=1)
            print(current_weather[:200] + "..." if len(current_weather) > 200 else current_weather)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: 3-day forecast
        print("\n2️⃣  3-Day Forecast:")
        try:
            forecast = weather_tool._run(city=city, days=3)
            print(forecast[:300] + "..." if len(forecast) > 300 else forecast)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Hourly weather for specific times
        print("\n3️⃣  Hourly Weather for Key Times:")
        today = datetime.now().strftime("%Y-%m-%d")
        key_hours = [8, 12, 16, 20]  # Sáng, Trưa, Chiều, Tối
        
        for hour in key_hours:
            time_names = {8: "Sáng", 12: "Trưa", 16: "Chiều", 20: "Tối"}
            print(f"\n   🕐 {time_names[hour]} ({hour:02d}:00):")
            try:
                hourly_weather = weather_tool._run(city=city, hour=hour, date=today)
                print(hourly_weather[:150] + "..." if len(hourly_weather) > 150 else hourly_weather)
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test 4: All time periods for today
        print(f"\n4️⃣  Complete Today's Schedule for {city}:")
        try:
            complete_today = weather_tool.get_today_weather(city)
            print(complete_today[:400] + "..." if len(complete_today) > 400 else complete_today)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)

def check_api_key():
    """Check if WeatherAPI key is configured"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('WEATHERAPI_KEY') or os.getenv('WEATHER_API_KEY')
    
    if api_key:
        print(f"✅ WeatherAPI key found: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
        return True
    else:
        print("❌ No WeatherAPI key found. Please set WEATHERAPI_KEY in .env file")
        print("💡 You can get a free API key from: https://www.weatherapi.com/signup.aspx")
        return False

if __name__ == "__main__":
    print("🔧 WEATHER TOOL TEST SUITE")
    print("=" * 60)
    
    # Check API key first
    if not check_api_key():
        print("\n⚠️  Cannot run tests without API key")
        print("Please add WEATHERAPI_KEY=your_api_key to .env file")
        sys.exit(1)
    
    # Run the tests
    test_weather_tool()
    
    print("\n🎉 Weather tool testing completed!")
    print("Now the itinerary agent can use detailed weather data for better travel planning.")
