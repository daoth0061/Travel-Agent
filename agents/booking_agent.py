"""
Booking Agent for handling accommodation booking requests
Uses hotel booking APIs to find and suggest accommodations
"""
import os
import requests
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Dict, List
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class HotelSearchInput(BaseModel):
    destination: str = Field(..., description="Destination city or area")
    check_in_date: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out_date: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    number_of_guests: int = Field(default=2, description="Number of guests")
    budget_range: str = Field(default="mid_range", description="Budget range: budget, mid_range, luxury")


class HotelDetailInput(BaseModel):
    hotel_id: str = Field(..., description="Hotel ID to get details for")


class GoogleHotelsTool(BaseTool):
    """Tool for searching hotels using Google Hotels API (via RapidAPI)"""
    name: str = "google_hotels"
    description: str = "Search for hotels using Google Hotels API"
    args_schema: type[BaseModel] = HotelSearchInput
    
    model_config = ConfigDict(extra='allow')
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.api_key = os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            print("Warning: No RapidAPI key found. Please set RAPIDAPI_KEY environment variable.")
    
    def _run(self, destination: str, check_in_date: str, check_out_date: str, 
             number_of_guests: int = 2, budget_range: str = "mid_range") -> str:
        """Search for hotels using Google Hotels API"""
        
        if not self.api_key:
            return self._get_fallback_recommendations(destination, budget_range)
        
        try:
            # Using Google Travel Hotels API via RapidAPI
            url = "https://google-travel-hotels.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "google-travel-hotels.p.rapidapi.com"
            }
            
            params = {
                "query": destination,
                "check_in": check_in_date,
                "check_out": check_out_date,
                "guests": number_of_guests,
                "currency": "VND"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_hotel_results(data, budget_range)
            else:
                return self._get_fallback_recommendations(destination, budget_range)
                
        except Exception as e:
            print(f"Error fetching hotel data: {e}")
            return self._get_fallback_recommendations(destination, budget_range)
    
    def _format_hotel_results(self, data: Dict, budget_range: str) -> str:
        """Format hotel search results"""
        hotels = data.get('hotels', [])
        
        if not hotels:
            return f"Không tìm thấy khách sạn phù hợp. Vui lòng thử tìm kiếm với điều kiện khác."
        
        # Filter by budget range
        filtered_hotels = self._filter_by_budget(hotels, budget_range)
        
        result = f"🏨 **Khách sạn được đề xuất:**\n\n"
        
        for i, hotel in enumerate(filtered_hotels[:5], 1):
            name = hotel.get('name', 'N/A')
            price = hotel.get('price', {})
            price_text = price.get('total', 'Liên hệ để biết giá')
            rating = hotel.get('rating', 'N/A')
            location = hotel.get('location', 'N/A')
            amenities = hotel.get('amenities', [])
            
            result += f"**{i}. {name}**\n"
            result += f"💰 Giá: {price_text}\n"
            result += f"⭐ Đánh giá: {rating}/5\n"
            result += f"📍 Địa điểm: {location}\n"
            
            if amenities:
                result += f"🏊 Tiện ích: {', '.join(amenities[:3])}\n"
            
            result += "\n"
        
        return result
    
    def _filter_by_budget(self, hotels: List[Dict], budget_range: str) -> List[Dict]:
        """Filter hotels by budget range"""
        # This is a simplified filter - in real implementation, 
        # you'd have more sophisticated price filtering
        if budget_range == "luxury":
            return [h for h in hotels if h.get('rating', 0) >= 4.5]
        elif budget_range == "budget":
            return [h for h in hotels if h.get('rating', 0) <= 3.5]
        else:  # mid_range
            return hotels
    
    def _get_fallback_recommendations(self, destination: str, budget_range: str) -> str:
        """Provide fallback recommendations when API is unavailable"""
        
        # Vietnam-specific hotel recommendations
        vietnam_hotels = {
            "hà nội": {
                "luxury": [
                    "Hotel Metropole Hanoi - Khách sạn lịch sử 5 sao, trung tâm phố cổ",
                    "JW Marriott Hotel Hanoi - Sang trọng, view hồ Gươm",
                    "Lotte Hotel Hanoi - Cao cấp, trung tâm thành phố"
                ],
                "mid_range": [
                    "Golden Sun Suites Hotel - Gần phố cổ, giá tốt",
                    "Hanoi La Siesta Hotel - Spa, trung tâm",
                    "May de Ville Old Quarter - Phố cổ, view đẹp"
                ],
                "budget": [
                    "Hanoi Backpackers Hostel - Phố cổ, giá rẻ",
                    "Golden Lotus Luxury Hotel - Bình dân, sạch sẽ",
                    "Thuy Sakura Hotel - Gần bến xe, giá tốt"
                ]
            },
            "hội an": {
                "luxury": [
                    "Four Seasons Resort The Nam Hai - Resort 5 sao, view biển",
                    "Anantara Hoi An Resort - Bên sông, sang trọng",
                    "La Residence Hue Hotel & Spa - Cổ điển, đẹp"
                ],
                "mid_range": [
                    "Hoi An Historic Hotel - Trung tâm phố cổ",
                    "Little Hoi An Central Boutique - Gần chợ đêm",
                    "Villa Hội An Lodge - Yên tĩnh, đẹp"
                ],
                "budget": [
                    "Thuy Hostel Hoi An - Hostel sạch, giá rẻ",
                    "Hoi An Backpackers Hostel - Trung tâm, vui vẻ",
                    "Mad Monkey Hostel Hoi An - Quốc tế, giá tốt"
                ]
            },
            "sa pa": {
                "luxury": [
                    "Hotel de la Coupole MGallery - View núi đẹp nhất Sa Pa",
                    "Silk Path Grand Resort & Spa - Resort 5 sao, sang trọng",
                    "Amazing Hotel Sapa - Cao cấp, trung tâm"
                ],
                "mid_range": [
                    "Sapa Relax Hotel & Spa - Spa tốt, view đẹp",
                    "Pao's Sapa Leisure Hotel - Trung tâm, tiện nghi",
                    "Sapa Elite Hotel - Mới, sạch sẽ"
                ],
                "budget": [
                    "Sapa Backpackers - Hostel vui, giá rẻ",
                    "Amazing Sapa Hotel - Bình dân, tốt",
                    "Sapa Cozy Hotel - Nhỏ xinh, giá hợp lý"
                ]
            }
        }
        
        dest_lower = destination.lower()
        recommendations = []
        
        # Find matching destination
        for dest_key, hotels in vietnam_hotels.items():
            if dest_key in dest_lower or any(alias in dest_lower for alias in [dest_key.replace(" ", ""), dest_key.replace("ô", "o")]):
                recommendations = hotels.get(budget_range, hotels.get("mid_range", []))
                break
        
        if not recommendations:
            recommendations = [
                f"Booking.com - Tìm kiếm khách sạn tại {destination}",
                f"Agoda - Đặt phòng tại {destination}",
                f"Hotels.com - Khách sạn giá tốt tại {destination}"
            ]
        
        result = f"🏨 **Khách sạn đề xuất tại {destination}** (Phạm vi giá: {budget_range}):\n\n"
        
        for i, hotel in enumerate(recommendations[:5], 1):
            result += f"{i}. {hotel}\n"
        
        result += f"\n💡 **Lưu ý:** Để đặt phòng, bạn có thể:\n"
        result += f"- Truy cập Booking.com, Agoda.com, Hotels.com\n"
        result += f"- Gọi trực tiếp khách sạn\n"
        result += f"- Đặt qua ứng dụng du lịch\n"
        
        return result


class HotelDetailsTool(BaseTool):
    """Tool for getting detailed hotel information"""
    name: str = "get_hotel_details"
    description: str = "Get detailed information about a specific hotel"
    args_schema: type[BaseModel] = HotelDetailInput
    
    model_config = ConfigDict(extra='allow')
    
    def _run(self, hotel_id: str) -> str:
        """Get detailed hotel information"""
        # This would integrate with the hotel API to get details
        return f"Chi tiết khách sạn ID {hotel_id} sẽ được cung cấp qua API booking."


class BookingAgent:
    """
    Agent for handling accommodation booking requests
    """
    
    def __init__(self, llm):
        self.google_hotels_tool = GoogleHotelsTool()
        self.hotel_details_tool = HotelDetailsTool()
        
        self.agent = Agent(
            role="🏨 Chuyên Viên Đặt Phòng Khách Sạn",
            goal="Tìm kiếm và đề xuất các lựa chọn lưu trú phù hợp với ngân sách và yêu cầu của khách hàng.",
            backstory="Chuyên viên đặt phòng với 8 năm kinh nghiệm trong ngành khách sạn, có mạng lưới rộng khắp Việt Nam và hiểu rõ nhu cầu đa dạng của du khách từ budget backpacker đến luxury resort.",
            llm=llm,
            allow_delegation=False,
            tools=[self.google_hotels_tool, self.hotel_details_tool]
        )
    
    def create_task(self, request: str, context: dict = None) -> Task:
        """Create booking task based on user request"""
        
        # Extract context information
        destination = "Hà Nội"  # Default
        check_in = None
        check_out = None
        guests = 2
        budget_range = "mid_range"
        
        if context:
            current_context = context.get("current_context", {})
            destination = current_context.get("current_destination", destination)
            
            # Calculate dates if trip length is known
            if current_context.get("current_dates"):
                check_in = current_context["current_dates"]
            if current_context.get("current_trip_length") and check_in:
                try:
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                    check_out_date = check_in_date + timedelta(days=current_context["current_trip_length"])
                    check_out = check_out_date.strftime("%Y-%m-%d")
                except:
                    pass
            
            # Extract budget from preferences
            preferences = current_context.get("preferences", {})
            budget_range = preferences.get("budget", "mid_range")
        
        # Set default dates if not available
        if not check_in:
            tomorrow = datetime.now() + timedelta(days=1)
            check_in = tomorrow.strftime("%Y-%m-%d")
        if not check_out:
            day_after = datetime.now() + timedelta(days=3)
            check_out = day_after.strftime("%Y-%m-%d")
        
        desc = f"""
            Yêu cầu đặt phòng: "{request}"
            Điểm đến: {destination}
            Ngày nhận phòng: {check_in}
            Ngày trả phòng: {check_out}
            Số khách: {guests}
            Phạm vi giá: {budget_range}

            Nhiệm vụ:
            1. **Sử dụng tool `google_hotels` để tìm kiếm khách sạn** tại {destination} với các thông số:
               - destination: "{destination}"
               - check_in_date: "{check_in}"
               - check_out_date: "{check_out}"
               - number_of_guests: {guests}
               - budget_range: "{budget_range}"
            
            2. Phân tích yêu cầu cụ thể của khách từ câu hỏi:
               - Loại hình lưu trú (khách sạn, homestay, resort)
               - Vị trí mong muốn (trung tâm, gần biển, yên tĩnh)
               - Tiện ích cần thiết (spa, hồ bơi, gym, wifi)
               - Ngân sách dự kiến
            
            3. Đưa ra các gợi ý phù hợp dựa trên kết quả tìm kiếm.
            
            4. Cung cấp thông tin về:
               - Giá phòng và các loại phòng
               - Vị trí và cách di chuyển
               - Tiện ích và dịch vụ
               - Chính sách hủy và đặt phòng
            
            5. Đưa ra lời khuyên về cách đặt phòng và các lưu ý quan trọng.

            Trả lời bằng tiếng Việt.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Danh sách khách sạn được đề xuất tại {destination} với thông tin chi tiết về giá cả, vị trí, tiện ích và hướng dẫn đặt phòng."
        )
