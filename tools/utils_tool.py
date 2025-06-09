import requests
import os
from datetime import datetime, timedelta
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class WeatherSearchInput(BaseModel):
    city: str = Field(..., description="The city name for weather forecast (e.g., 'Hanoi', 'Sa Pa', 'Hoi An')")
    days: int = Field(default=1, description="Number of days for forecast (1-5 days). Default is 1 for current weather.")

class RealtimeWeatherTool(BaseTool):
    name: str = "realtime_weather"
    description: str = "Get real-time weather data and forecast using OpenWeatherMap API. Provides current weather and up to 5-day forecast."
    args_schema: type[BaseModel] = WeatherSearchInput
    
    model_config = ConfigDict(extra='allow')

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.api_key = os.getenv('OPENWEATHER_API_KEY') or os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            print("Warning: No OpenWeatherMap API key found. Please set OPENWEATHER_API_KEY or WEATHER_API_KEY environment variable.")

    def _run(self, city: str, days: int = 1) -> str:
        """
        Fetch real-time weather data from OpenWeatherMap API
        """
        if not self.api_key:
            return "Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
        
        try:
            if days == 1:
                # Get current weather
                return self._get_current_weather(city)
            else:
                # Get weather forecast
                return self._get_weather_forecast(city, days)
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"

    def _get_current_weather(self, city: str) -> str:
        """Get current weather for the city"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not fetch weather data for {city}. Status code: {response.status_code}"
        
        data = response.json()
        
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "description": data["weather"][0]["description"].title(),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "datetime": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add travel recommendations
        recommendations = self._get_travel_recommendations(weather_info)
        
        result = f"""🌤️ Current Weather for {weather_info['city']}, {weather_info['country']}
📅 Date & Time: {weather_info['datetime']}
🌡️ Temperature: {weather_info['temperature']:.1f}°C (feels like {weather_info['feels_like']:.1f}°C)
☁️ Conditions: {weather_info['description']}
💧 Humidity: {weather_info['humidity']}%
🌬️ Wind Speed: {weather_info['wind_speed']} m/s
👁️ Visibility: {weather_info['visibility']:.1f} km

🧳 Travel Recommendations: {recommendations}"""
        
        return result

    def _get_weather_forecast(self, city: str, days: int) -> str:
        """Get weather forecast for multiple days"""
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not fetch forecast data for {city}. Status code: {response.status_code}"
        
        data = response.json()
        
        forecast_days = {}
        today = datetime.now().date()
        
        # Process forecast data (API returns 3-hour intervals for 5 days)
        for entry in data["list"]:
            forecast_time = datetime.fromtimestamp(entry["dt"])
            forecast_date = forecast_time.date()
            
            # Skip today's data if we want future days only
            if forecast_date <= today:
                continue
                
            if len(forecast_days) >= days:
                break
                
            if forecast_date not in forecast_days:
                forecast_days[forecast_date] = {
                    "date": forecast_date,
                    "description": entry["weather"][0]["description"].title(),
                    "temp_min": entry["main"]["temp_min"],
                    "temp_max": entry["main"]["temp_max"],
                    "humidity": entry["main"]["humidity"],
                    "wind_speed": entry["wind"]["speed"],
                    "entries": []
                }
            
            forecast_days[forecast_date]["entries"].append({
                "time": forecast_time.strftime("%H:%M"),
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"]
            })
            
            # Update min/max temperatures
            forecast_days[forecast_date]["temp_min"] = min(
                forecast_days[forecast_date]["temp_min"], 
                entry["main"]["temp_min"]
            )
            forecast_days[forecast_date]["temp_max"] = max(
                forecast_days[forecast_date]["temp_max"], 
                entry["main"]["temp_max"]
            )

        # Format the forecast result
        city_name = data["city"]["name"]
        country = data["city"]["country"]
        
        result = f"🌤️ Weather Forecast for {city_name}, {country}\n\n"
        
        for date, info in list(forecast_days.items())[:days]:
            day_name = date.strftime("%A, %B %d, %Y")
            recommendations = self._get_forecast_recommendations(info)
            
            result += f"📅 {day_name}\n"
            result += f"🌡️ Temperature: {info['temp_min']:.1f}°C - {info['temp_max']:.1f}°C\n"
            result += f"☁️ Conditions: {info['description']}\n"
            result += f"💧 Humidity: {info['humidity']}%\n"
            result += f"🌬️ Wind Speed: {info['wind_speed']} m/s\n"
            result += f"🧳 Recommendations: {recommendations}\n\n"
        
        return result

    def _get_travel_recommendations(self, weather_info: dict) -> str:
        """Generate travel recommendations based on current weather"""
        temp = weather_info['temperature']
        description = weather_info['description'].lower()
        humidity = weather_info['humidity']
        wind_speed = weather_info['wind_speed']
        
        recommendations = []
        
        # Temperature-based recommendations
        if temp < 10:
            recommendations.append("dress warmly with layers")
        elif temp < 20:
            recommendations.append("bring a light jacket")
        elif temp > 30:
            recommendations.append("stay hydrated and wear light clothing")
            recommendations.append("avoid midday outdoor activities")
        
        # Weather condition recommendations
        if any(word in description for word in ['rain', 'drizzle', 'shower']):
            recommendations.append("bring umbrella or raincoat")
            recommendations.append("consider indoor activities")
        elif 'snow' in description:
            recommendations.append("dress warmly and wear appropriate footwear")
        elif any(word in description for word in ['clear', 'sunny']):
            recommendations.append("perfect for outdoor activities")
            recommendations.append("don't forget sunscreen")
        elif 'fog' in description or 'mist' in description:
            recommendations.append("visibility may be limited")
        
        # Humidity recommendations
        if humidity > 80:
            recommendations.append("expect muggy conditions")
        
        # Wind recommendations
        if wind_speed > 7:
            recommendations.append("expect windy conditions")
        
        return "; ".join(recommendations) if recommendations else "Good conditions for travel"

    def _get_forecast_recommendations(self, forecast_info: dict) -> str:
        """Generate recommendations for forecast day"""
        temp_avg = (forecast_info['temp_min'] + forecast_info['temp_max']) / 2
        description = forecast_info['description'].lower()
        
        recommendations = []
        
        if temp_avg < 15:
            recommendations.append("pack warm clothes")
        elif temp_avg > 30:
            recommendations.append("plan indoor activities during midday")
        
        if any(word in description for word in ['rain', 'shower', 'drizzle']):
            recommendations.append("bring rain gear")
        elif 'clear' in description or 'sunny' in description:
            recommendations.append("great day for outdoor activities")
        
        return "; ".join(recommendations) if recommendations else "Good day for travel"