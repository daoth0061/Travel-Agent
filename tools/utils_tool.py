import requests
import os
from datetime import datetime, timedelta
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

class WeatherSearchInput(BaseModel):
    city: str = Field(..., description="The city name for weather forecast (e.g., 'Hanoi', 'Sa Pa', 'Hoi An')")
    days: int = Field(default=1, description="Number of days for forecast (1-14 days). Default is 1 for current weather.")
    hour: Optional[int] = Field(default=None, description="Specific hour for weather forecast (0-23). Optional - used for hourly forecasts.")
    date: Optional[str] = Field(default=None, description="Specific date for weather forecast (YYYY-MM-DD format). Optional - defaults to today.")

class RealtimeWeatherTool(BaseTool):
    name: str = "realtime_weather"
    description: str = "Get real-time weather data and forecast using WeatherAPI.com. Provides current weather, hourly forecasts, and up to 14-day forecast."
    args_schema: type[BaseModel] = WeatherSearchInput
    
    model_config = ConfigDict(extra='allow')
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.api_key = os.getenv('WEATHERAPI_KEY') or os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            print("Warning: No WeatherAPI.com API key found. Please set WEATHERAPI_KEY or WEATHER_API_KEY environment variable.")

    def _run(self, city: str, days: int = 1, hour: Optional[int] = None, date: Optional[str] = None) -> str:
        """
        Fetch real-time weather data from WeatherAPI.com
        """
        if not self.api_key:
            return "Error: WeatherAPI.com API key not configured. Please set WEATHERAPI_KEY environment variable."
        
        try:
            if hour is not None:
                # Get hourly weather forecast
                return self._get_hourly_weather(city, hour, date)
            elif days == 1 and date is None:
                # Get current weather
                return self._get_current_weather(city)
            else:
                # Get weather forecast
                return self._get_weather_forecast(city, days, date)
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"

    def _get_current_weather(self, city: str) -> str:
        """Get current weather for the city using WeatherAPI.com"""
        url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={city}&aqi=yes"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not fetch weather data for {city}. Status code: {response.status_code}"
        
        data = response.json()
        
        # Extract location and current weather info
        location = data["location"]
        current = data["current"]
        
        weather_info = {
            "city": location["name"],
            "region": location["region"],
            "country": location["country"],
            "description": current["condition"]["text"],
            "temperature": current["temp_c"],
            "feels_like": current["feelslike_c"],
            "humidity": current["humidity"],
            "wind_speed": current["wind_kph"],
            "wind_dir": current["wind_dir"],
            "pressure": current["pressure_mb"],
            "visibility": current["vis_km"],
            "uv_index": current["uv"],
            "is_day": current["is_day"],
            "local_time": location["localtime"]
        }
        
        # Add air quality if available
        air_quality_info = ""
        if "air_quality" in data:
            aqi = data["air_quality"]
            air_quality_info = f"\n🌬️ Air Quality: US EPA Index {aqi.get('us-epa-index', 'N/A')}, PM2.5: {aqi.get('pm2_5', 'N/A')} μg/m³"
        
        # Add travel recommendations
        recommendations = self._get_travel_recommendations(weather_info)
        
        result = f"""🌤️ Current Weather for {weather_info['city']}, {weather_info['region']}, {weather_info['country']}
📅 Local Time: {weather_info['local_time']}
🌡️ Temperature: {weather_info['temperature']:.1f}°C (feels like {weather_info['feels_like']:.1f}°C)
☁️ Conditions: {weather_info['description']}
💧 Humidity: {weather_info['humidity']}%
🌬️ Wind: {weather_info['wind_speed']} km/h {weather_info['wind_dir']}
🔽 Pressure: {weather_info['pressure']} mb
👁️ Visibility: {weather_info['visibility']} km
☀️ UV Index: {weather_info['uv_index']}{air_quality_info}

🧳 Travel Recommendations: {recommendations}"""        
        return result

    def _get_hourly_weather(self, city: str, hour: int, date: Optional[str] = None) -> str:
        """Get hourly weather forecast for specific hour"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # For hourly forecast, we need at least 1 day forecast
        url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={city}&days=3&aqi=yes"
        
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not fetch hourly weather data for {city}. Status code: {response.status_code}"
        
        data = response.json()
        location = data["location"]
        forecast_days = data["forecast"]["forecastday"]
        
        # Find the specific date
        target_day = None
        for day_data in forecast_days:
            if day_data["date"] == date:
                target_day = day_data
                break
        
        if not target_day:
            return f"Error: No hourly data available for {date}"
        
        # Find the specific hour
        target_hour = None
        for hour_data in target_day["hour"]:
            hour_time = datetime.strptime(hour_data["time"], "%Y-%m-%d %H:%M")
            if hour_time.hour == hour:
                target_hour = hour_data
                break
        
        if not target_hour:
            return f"Error: No data available for hour {hour} on {date}"
        
        # Format the result
        time_period = self._get_time_period(hour)
        hour_time = datetime.strptime(target_hour["time"], "%Y-%m-%d %H:%M")
        
        weather_info = {
            "temperature": target_hour["temp_c"],
            "feels_like": target_hour["feelslike_c"],
            "description": target_hour["condition"]["text"],
            "humidity": target_hour["humidity"],
            "wind_speed": target_hour["wind_kph"],
            "wind_dir": target_hour["wind_dir"],
            "pressure": target_hour["pressure_mb"],
            "visibility": target_hour["vis_km"],
            "uv_index": target_hour["uv"],
            "is_day": target_hour["is_day"],
            "chance_of_rain": target_hour["chance_of_rain"],
            "chance_of_snow": target_hour["chance_of_snow"]
        }
        
        recommendations = self._get_travel_recommendations(weather_info)
        
        result = f"""🌤️ Hourly Weather for {location['name']}, {location['region']}, {location['country']}
📅 Date & Time: {hour_time.strftime('%A, %B %d, %Y')} - {time_period} ({hour:02d}:00)
🌡️ Temperature: {weather_info['temperature']:.1f}°C (feels like {weather_info['feels_like']:.1f}°C)
☁️ Conditions: {weather_info['description']}
🌧️ Chance of Rain: {weather_info['chance_of_rain']}% | Snow: {weather_info['chance_of_snow']}%
💧 Humidity: {weather_info['humidity']}%
🌬️ Wind: {weather_info['wind_speed']} km/h {weather_info['wind_dir']}
🔽 Pressure: {weather_info['pressure']} mb
👁️ Visibility: {weather_info['visibility']} km
☀️ UV Index: {weather_info['uv_index']}

🧳 Travel Recommendations: {recommendations}"""
        
        return result

    def _get_weather_forecast(self, city: str, days: int, date: Optional[str] = None) -> str:
        """Get weather forecast for multiple days using WeatherAPI.com"""
        # WeatherAPI.com supports up to 14 days forecast
        days = min(days, 14)
        
        url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={city}&days={days}&aqi=yes&alerts=yes"
        
                
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not fetch forecast data for {city}. Status code: {response.status_code}"
        
        data = response.json()
        
        location = data["location"]
        forecast_days = data["forecast"]["forecastday"]
        
        # Format the forecast result
        result = f"🌤️ Weather Forecast for {location['name']}, {location['region']}, {location['country']}\n"
        
        # Add weather alerts if available
        if "alerts" in data and data["alerts"]["alert"]:
            result += "\n⚠️ WEATHER ALERTS:\n"
            for alert in data["alerts"]["alert"]:
                result += f"🚨 {alert['headline']}\n"
                result += f"   Severity: {alert['severity']} | Category: {alert['category']}\n"
                result += f"   Effective: {alert['effective']} to {alert['expires']}\n"
        
        result += "\n"
        
        for day_data in forecast_days:
            date_obj = datetime.strptime(day_data["date"], "%Y-%m-%d")
            day_name = date_obj.strftime("%A, %B %d, %Y")
            day_info = day_data["day"]
            astro_info = day_data["astro"]
            
            recommendations = self._get_forecast_recommendations(day_info)
            
            # Add hourly breakdown for key times
            daily_periods = self._get_daily_periods_weather(day_data["hour"])
            
            result += f"📅 {day_name}\n"
            result += f"🌡️ Temperature: {day_info['mintemp_c']:.1f}°C - {day_info['maxtemp_c']:.1f}°C (avg: {day_info['avgtemp_c']:.1f}°C)\n"
            result += f"☁️ Conditions: {day_info['condition']['text']}\n"
            result += f"🌧️ Chance of Rain: {day_info['daily_chance_of_rain']}% | Snow: {day_info['daily_chance_of_snow']}%\n"
            result += f"💧 Humidity: {day_info['avghumidity']}%\n"
            result += f"🌬️ Max Wind: {day_info['maxwind_kph']} km/h\n"
            result += f"☀️ UV Index: {day_info['uv']}\n"
            result += f"🌅 Sunrise: {astro_info['sunrise']} | 🌇 Sunset: {astro_info['sunset']}\n"
            result += f"🧳 Recommendations: {recommendations}\n"
            result += daily_periods
            result += "\n"
        
        return result

    def _get_daily_periods_weather(self, hourly_data: list) -> str:
        """Get weather for 4 key periods of the day"""
        periods = {
            "🌅 Sáng (8:00)": 8,
            "☀️ Trưa (12:00)": 12,
            "🌤️ Chiều (16:00)": 16,
            "🌙 Tối (20:00)": 20
        }
        
        result = "\n📊 Key Times of Day:\n"
        
        for period_name, target_hour in periods.items():
            # Find the closest hour data
            hour_data = None
            for hour in hourly_data:
                hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
                if hour_time.hour == target_hour:
                    hour_data = hour
                    break
            
            if hour_data:
                result += f"   {period_name}: {hour_data['temp_c']:.1f}°C, {hour_data['condition']['text']}, Rain: {hour_data['chance_of_rain']}%\n"
            else:
                result += f"   {period_name}: No data available\n"
        
        return result

    def _get_time_period(self, hour: int) -> str:
        """Convert hour to Vietnamese time period"""
        if 5 <= hour < 11:
            return "Sáng (Morning)"
        elif 11 <= hour < 14:
            return "Trưa (Noon)"
        elif 14 <= hour < 18:
            return "Chiều (Afternoon)"
        elif 18 <= hour < 22:
            return "Tối (Evening)"
        else:
            return "Đêm (Night)"

    def _get_travel_recommendations(self, weather_info: dict) -> str:
        """Generate travel recommendations based on current weather"""
        temp = weather_info['temperature']
        description = weather_info['description'].lower()
        humidity = weather_info['humidity']
        wind_speed = weather_info['wind_speed']
        uv_index = weather_info.get('uv_index', 0)
        is_day = weather_info.get('is_day', 1)        
        recommendations = []
        
        # Temperature-based recommendations
        if temp < 10:
            recommendations.append("dress warmly with layers")
        elif temp < 20:
            recommendations.append("bring a light jacket")
        elif temp > 32:
            recommendations.append("stay hydrated and wear light clothing")
            recommendations.append("avoid midday outdoor activities")
        elif temp > 28:
            recommendations.append("stay hydrated")
        
        # Weather condition recommendations
        if any(word in description for word in ['rain', 'drizzle', 'shower']):
            recommendations.append("bring umbrella or raincoat")
            recommendations.append("consider indoor activities")
        elif 'snow' in description:
            recommendations.append("dress warmly and wear appropriate footwear")
        elif any(word in description for word in ['clear', 'sunny']):
            recommendations.append("perfect for outdoor activities")
            if is_day:
                recommendations.append("don't forget sunscreen")
        elif any(word in description for word in ['fog', 'mist', 'overcast']):
            recommendations.append("visibility may be limited")
        elif 'thunderstorm' in description:
            recommendations.append("stay indoors during storms")
            recommendations.append("avoid outdoor activities")
        
        # Humidity recommendations
        if humidity > 80:
            recommendations.append("expect muggy conditions")
        elif humidity < 30:
            recommendations.append("dry conditions - stay hydrated")
        
        # Wind recommendations
        if wind_speed > 25:  # WeatherAPI uses km/h
            recommendations.append("expect windy conditions")
        
        # UV index recommendations
        if uv_index > 7:
            recommendations.append("high UV - use strong sunscreen")
        elif uv_index > 5:
            recommendations.append("moderate UV - use sunscreen")
        
        return "; ".join(recommendations) if recommendations else "Good conditions for travel"

    def _get_forecast_recommendations(self, day_info: dict) -> str:
        """Generate recommendations for forecast day"""
        temp_min = day_info['mintemp_c']
        temp_max = day_info['maxtemp_c']
        temp_avg = (temp_min + temp_max) / 2
        description = day_info['condition']['text'].lower()
        rain_chance = day_info.get('daily_chance_of_rain', 0)
        snow_chance = day_info.get('daily_chance_of_snow', 0)
        uv_index = day_info.get('uv', 0)
        
        recommendations = []
        
        # Temperature recommendations
        if temp_max < 10:
            recommendations.append("pack warm clothes")
        elif temp_min < 15 and temp_max > 25:
            recommendations.append("dress in layers")
        elif temp_max > 32:
            recommendations.append("plan indoor activities during midday")
            recommendations.append("stay hydrated")
        
        # Weather condition recommendations
        if rain_chance > 70 or any(word in description for word in ['rain', 'shower', 'drizzle']):
            recommendations.append("bring rain gear")
            recommendations.append("plan indoor activities")
        elif rain_chance > 30:
            recommendations.append("pack umbrella just in case")
        
        if snow_chance > 50:
            recommendations.append("prepare for snow")
            recommendations.append("dress warmly")
        
        if any(word in description for word in ['clear', 'sunny']):
            recommendations.append("great day for outdoor activities")
        elif 'thunderstorm' in description:
            recommendations.append("avoid outdoor activities during storms")
        
        # UV recommendations
        if uv_index > 7:
            recommendations.append("high UV - use strong sunscreen")
        elif uv_index > 5:
            recommendations.append("use sunscreen")
        
        return "; ".join(recommendations) if recommendations else "Good day for travel"

    def get_weather_for_time_periods(self, city: str, date: Optional[str] = None) -> str:
        """Get weather for all 4 time periods of the day (Sáng, Trưa, Chiều, Tối)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        periods = [
            ("Sáng", 8),
            ("Trưa", 12), 
            ("Chiều", 16),
            ("Tối", 20)
        ]
        
        results = []
        for period_name, hour in periods:
            weather_data = self._get_hourly_weather(city, hour, date)
            results.append(f"\n=== {period_name.upper()} ({hour:02d}:00) ===\n{weather_data}")
        
        return "\n".join(results)

    def get_today_weather(self, city: str) -> str:
        """Get comprehensive weather for today including all time periods"""
        current_weather = self._get_current_weather(city)
        time_periods = self.get_weather_for_time_periods(city)
        
        return f"{current_weather}\n\n📊 TODAY'S DETAILED SCHEDULE:\n{time_periods}"

class WeatherRecommendationInput(BaseModel):
    destination: str = Field(..., description="Destination city")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    session: str = Field(..., description="Session: 'morning', 'noon', 'afternoon', 'evening'")

class WeatherRecommendationTool(BaseTool):
    name: str = "get_weather_and_recommendation"
    description: str = "Get weather forecast and activity recommendation for specific destination, date, and session"
    args_schema: type[BaseModel] = WeatherRecommendationInput
    
    model_config = ConfigDict(extra='allow')
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.weather_tool = RealtimeWeatherTool()
        
    def _run(self, destination: str, date: str, session: str) -> str:
        """
        Get weather forecast and recommendation for specific session.
        Returns: weather forecast + activity recommendation
        """
        # Map session to hour
        session_hours = {
            'morning': 8,
            'noon': 12, 
            'afternoon': 16,
            'evening': 20
        }
        
        hour = session_hours.get(session.lower(), 12)
        
        # Get weather data
        weather_data = self.weather_tool._get_hourly_weather(destination, hour, date)
        
        if "Error" in weather_data:
            return f"Weather: Unavailable, Recommendation: Plan indoor activities as backup"
        
        # Extract key weather info for recommendation
        lines = weather_data.split('\n')
        temp_line = next((line for line in lines if 'Temperature:' in line), "")
        condition_line = next((line for line in lines if 'Conditions:' in line), "")
        rain_line = next((line for line in lines if 'Chance of Rain:' in line), "")
        
        # Generate activity recommendation based on weather
        recommendation = self._generate_activity_recommendation(
            temp_line, condition_line, rain_line, session, destination
        )
        
        return f"Weather: {temp_line.split(':')[1].strip() if temp_line else 'Unknown'}, {condition_line.split(':')[1].strip() if condition_line else 'Unknown'}. Recommendation: {recommendation}"
    
    def _generate_activity_recommendation(self, temp_line: str, condition_line: str, 
                                        rain_line: str, session: str, destination: str) -> str:
        """Generate specific activity recommendations based on weather"""
        
        # Extract temperature if available
        temp = None
        if temp_line and '°C' in temp_line:
            try:
                temp = float(temp_line.split('°C')[0].split()[-1])
            except:
                pass
        
        condition = condition_line.lower() if condition_line else ""
        rain_chance = 0
        if rain_line and '%' in rain_line:
            try:
                rain_chance = int(rain_line.split('%')[0].split()[-1])
            except:
                pass
        
        recommendations = []
        
        # Weather-based recommendations
        if rain_chance > 70:
            recommendations.append("indoor activities like museums, cafes, or shopping malls")
        elif rain_chance > 30:
            recommendations.append("covered areas with indoor backup options")
        
        if temp and temp > 32:
            recommendations.append("air-conditioned spaces during peak heat")
        elif temp and temp < 15:
            recommendations.append("warm indoor venues or dress warmly for outdoor")
        
        if 'sunny' in condition or 'clear' in condition:
            recommendations.append("great for outdoor sightseeing and photography")
        elif 'thunderstorm' in condition:
            recommendations.append("stay indoors until weather clears")
        
        # Session-specific recommendations
        if session == 'morning':
            recommendations.append("start with outdoor activities if weather permits")
        elif session == 'noon':
            recommendations.append("choose restaurants with appropriate climate control")
        elif session == 'afternoon':
            recommendations.append("perfect timing for scenic photography if clear")
        elif session == 'evening':
            recommendations.append("evening activities adapted to weather conditions")
        
        if not recommendations:
            recommendations.append("moderate weather suitable for most activities")
        
        return "; ".join(recommendations[:2])  # Limit to 2 main recommendations