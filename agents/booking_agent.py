"""
Booking Agent for handling accommodation booking requests
Uses SerpApi Google Hotels API to find and suggest accommodations
"""
import os
import requests
import json
import re
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Dict, List
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.utils import detect_destination, detect_time, extract_preferences, detect_trip_length

load_dotenv()


class HotelSearchInput(BaseModel):
    destination: str = Field(..., description="Destination city or area")
    check_in_date: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out_date: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(default=2, description="Number of adult guests")
    children: int = Field(default=0, description="Number of child guests")
    budget_range: str = Field(default="mid_range", description="Budget range: budget, mid_range, luxury")


class HotelDetailInput(BaseModel):
    hotel_id: str = Field(..., description="Hotel ID to get details for")


class SerpApiHotelsTool(BaseTool):
    """Tool for searching hotels using SerpApi Google Hotels API"""
    name: str = "hotel_search"
    description: str = "Search for hotels using SerpApi Google Hotels API with comprehensive filtering and error handling"
    args_schema: type[BaseModel] = HotelSearchInput
    
    model_config = ConfigDict(extra='allow')
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        self.api_key = os.getenv('SERPAPI_KEY')
        if not self.api_key:
            print("Warning: No SerpApi key found. Please set SERPAPI_KEY environment variable.")
            print("Hotel search will fallback to static recommendations.")
    
    def _run(self, destination: str, check_in_date: str, check_out_date: str, 
             adults: int = 2, children: int = 0, budget_range: str = "mid_range") -> str:
        """Search for hotels using SerpApi Google Hotels API"""
        
        if not self.api_key:
            return self._get_fallback_recommendations(destination, budget_range, adults, children)
        
        try:
            # Construct SerpApi request parameters
            params = {
                "engine": "google_hotels",
                "q": destination,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "adults": adults,
                "children": children,
                "currency": "VND",
                "gl": "vn",  # Country for Vietnam
                "hl": "vi",  # Language Vietnamese
                "api_key": self.api_key
            }
            
            # Add hotel class filter based on budget
            if budget_range == "luxury":
                params["hotel_class"] = "4,5"
            elif budget_range == "budget":
                params["hotel_class"] = "1,2,3"
            else:  # mid_range
                params["hotel_class"] = "2,3,4"
            
            print(f"🔍 Searching hotels via SerpApi for {destination}")
            print(f"   📅 {check_in_date} → {check_out_date}")
            print(f"   👥 {adults} adults, {children} children")
            print(f"   💰 Budget: {budget_range}")
            
            # Make API request
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_hotel_results(data, destination, budget_range, adults, children)
            else:
                print(f"❌ SerpApi error: HTTP {response.status_code}")
                return self._get_fallback_recommendations(destination, budget_range, adults, children)
                
        except requests.exceptions.Timeout:
            print("⏰ SerpApi request timeout")
            return self._get_fallback_recommendations(destination, budget_range, adults, children)
        except requests.exceptions.RequestException as e:
            print("🌐 Network error: {e}")
            return self._get_fallback_recommendations(destination, budget_range, adults, children)
        except Exception as e:
            print(f"❌ Unexpected error in hotel search: {e}")
            return self._get_fallback_recommendations(destination, budget_range, adults, children)
    
    def _format_hotel_results(self, data: Dict, destination: str, budget_range: str, 
                            adults: int, children: int) -> str:
        """Format hotel search results from SerpApi response"""
        try:
            hotels = data.get("properties", [])
            
            if not hotels:
                print("📍 No hotels found in API response")
                return self._get_fallback_recommendations(destination, budget_range, adults, children)
            
            # Filter and sort hotels
            filtered_hotels = self._filter_by_budget(hotels, budget_range)
            
            # Limit to top 5 results
            top_hotels = filtered_hotels[:5]
            
            if not top_hotels:
                print("🔍 No hotels match the budget criteria")
                return self._get_fallback_recommendations(destination, budget_range, adults, children)
            
            # Format results
            formatted_results = []
            for i, hotel in enumerate(top_hotels, 1):
                hotel_info = self._extract_hotel_info(hotel)
                
                formatted_hotel = f"""
{i}. **{hotel_info['name']}** ⭐{hotel_info['rating']}/5.0
   📍 Địa chỉ: {hotel_info['address']}
   💰 Giá phòng: {hotel_info['price']}
   🏆 Đánh giá: {hotel_info['reviews']}
   🏨 Tiện nghi: {hotel_info['amenities']}
   📝 Ghi chú: {hotel_info['notes']}
"""
                formatted_results.append(formatted_hotel)
            
            guest_info = f"{adults} người lớn"
            if children > 0:
                guest_info += f", {children} trẻ em"
            
            summary = f"""
🏨 **DANH SÁCH KHÁCH SẠN TẠI {destination.upper()}**
👥 Cho {guest_info} | 💰 Phân khúc: {budget_range}

{"".join(formatted_results)}

💡 **HƯỚNG DẪN ĐẶT PHÒNG:**
• Các giá trên có thể thay đổi theo thời gian thực
• Nên đặt phòng trước 1-2 tuần để có giá tốt
• Kiểm tra chính sách hủy phòng trước khi đặt
• Liên hệ trực tiếp khách sạn để có giá tốt nhất

📞 **Platform đề xuất:** Booking.com, Agoda, Traveloka
"""
            
            print(f"✅ Found {len(top_hotels)} hotels via SerpApi")
            return summary
            
        except Exception as e:
            print(f"❌ Error formatting hotel results: {e}")
            return self._get_fallback_recommendations(destination, budget_range, adults, children)
    
    def _extract_hotel_info(self, hotel: Dict) -> Dict[str, str]:
        """Extract and format hotel information from SerpApi response"""
        try:
            name = hotel.get("name", "Tên không có")
            
            # Extract rating
            rating = hotel.get("overall_rating", 0)
            if rating == 0:
                rating = hotel.get("rating", 0)
            
            # Extract address
            address = "Địa chỉ không có"
            if "gps_coordinates" in hotel:
                address = hotel.get("neighborhood", hotel.get("district", "Trung tâm"))
              # Extract price
            price = "Liên hệ để biết giá"
            if "rate_per_night" in hotel:
                rate = hotel["rate_per_night"]
                try:
                    if "lowest" in rate and isinstance(rate["lowest"], (int, float)):
                        price = f"Từ {int(rate['lowest']):,} VND/đêm"
                    elif "price" in rate and isinstance(rate["price"], (int, float)):
                        price = f"Từ {int(rate['price']):,} VND/đêm"
                except (ValueError, TypeError):
                    price = "Liên hệ để biết giá"
            
            # Extract review count
            reviews = "Chưa có đánh giá"
            if "reviews" in hotel:
                try:
                    review_count = hotel["reviews"]
                    if isinstance(review_count, (int, float)):
                        reviews = f"{int(review_count):,} đánh giá"
                except (ValueError, TypeError):
                    reviews = "Nhiều đánh giá tích cực"
            
            # Extract amenities
            amenities = []
            if "amenities" in hotel:
                amenities_list = hotel["amenities"]
                if isinstance(amenities_list, list):
                    amenities = amenities_list[:4]  # Top 4 amenities
            
            if not amenities and "type" in hotel:
                amenities = [hotel["type"]]
            
            amenities_str = ", ".join(amenities) if amenities else "Wi-Fi, Điều hòa"
            
            # Extract notes
            notes = []
            if hotel.get("free_cancellation"):
                notes.append("Hủy miễn phí")
            if hotel.get("deal"):
                notes.append("Có ưu đãi")
            if "sustainability" in hotel:
                notes.append("Thân thiện môi trường")
            
            notes_str = ", ".join(notes) if notes else "Dịch vụ tốt"
            
            return {
                "name": name,
                "rating": f"{rating:.1f}" if rating > 0 else "N/A",
                "address": address,
                "price": price,
                "reviews": reviews,
                "amenities": amenities_str,
                "notes": notes_str
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting hotel info: {e}")
            return {
                "name": "Hotel Name",
                "rating": "4.0",
                "address": "Trung tâm",
                "price": "Liên hệ để biết giá",
                "reviews": "Nhiều đánh giá tích cực",
                "amenities": "Wi-Fi, Điều hòa, Bữa sáng",
                "notes": "Dịch vụ tốt"
            }
    
    def _filter_by_budget(self, hotels: List[Dict], budget_range: str) -> List[Dict]:
        """Filter hotels by budget range and rating"""
        try:
            filtered = []
            
            for hotel in hotels:
                # Get rating for filtering
                rating = hotel.get("overall_rating", hotel.get("rating", 0))
                
                # Filter based on budget and rating
                if budget_range == "luxury":
                    if rating >= 4.0:
                        filtered.append(hotel)
                elif budget_range == "budget":
                    if rating >= 3.0:  # Still want decent quality
                        filtered.append(hotel)
                else:  # mid_range
                    if rating >= 3.5:
                        filtered.append(hotel)
            
            # Sort by rating descending
            filtered.sort(key=lambda x: x.get("overall_rating", x.get("rating", 0)), reverse=True)
            
            return filtered
            
        except Exception as e:
            print(f"⚠️ Error filtering hotels: {e}")
            return hotels[:5]  # Return first 5 if filtering fails
    
    def _get_fallback_recommendations(self, destination: str, budget_range: str, 
                                    adults: int, children: int) -> str:
        """Provide static fallback recommendations when API fails"""
        
        guest_info = f"{adults} người lớn"
        if children > 0:
            guest_info += f", {children} trẻ em"
        
        # Static recommendations by destination and budget
        recommendations = {
            "hanoi": {
                "luxury": [
                    "Lotte Hotel Hanoi - Đẳng cấp quốc tế 5 sao",
                    "InterContinental Hanoi Westlake - View Hồ Tây tuyệt đẹp",
                    "Hotel Metropole Hanoi - Lịch sử và sang trọng"
                ],
                "mid_range": [
                    "Silk Path Hotel - Vị trí trung tâm thuận tiện",
                    "Golden Silk Boutique Hotel - Phong cách boutique",
                    "La Siesta Hoi An Resort & Spa - Dịch vụ tuyệt vời"
                ],
                "budget": [
                    "May De Ville Old Quarter - Giá tốt ở phố cổ",
                    "Hanoi La Siesta Hotel & Spa - Tầm trung chất lượng",
                    "Golden Legend Hotel - Gần các điểm tham quan"
                ]
            },
            "saigon": {
                "luxury": [
                    "Park Hyatt Saigon - Luxury tại trung tâm",
                    "The Reverie Saigon - Xa hoa và đẳng cấp",
                    "Hotel Majestic Saigon - Lịch sử và view sông"
                ],
                "mid_range": [
                    "Liberty Central Saigon Riverside - View sông đẹp",
                    "Silverland Jolie Hotel & Spa - Boutique hiện đại",
                    "Hotel Royal Saigon - Trung tâm thành phố"
                ],
                "budget": [
                    "Mai House Saigon - Hostel chất lượng cao",
                    "Saigon Backpackers - Gặp gỡ du khách quốc tế",
                    "Liberty Central Saigon Centre - Tầm trung tốt"
                ]
            },
            "danang": {
                "luxury": [
                    "InterContinental Danang Sun Peninsula Resort - Resort đẳng cấp",
                    "Pullman Danang Beach Resort - Bãi biển riêng",
                    "Hyatt Regency Danang Resort and Spa - Spa world-class"
                ],
                "mid_range": [
                    "Novotel Danang Premier Han River - View sông Hàn",
                    "Muong Thanh Luxury Danang - Gần bãi biển",
                    "Danang Golden Bay - Thiết kế độc đáo"
                ],
                "budget": [
                    "Danang Backpackers - Hostel gần biển",
                    "Memory Hostel - Clean và an toàn",
                    "Okay Boutique Hotel - Tầm trung giá tốt"
                ]
            }
        }
        
        # Default recommendations
        default_recs = {
            "luxury": [
                "Khách sạn 4-5 sao địa phương - Dịch vụ cao cấp",
                "Resort nghỉ dưỡng - Không gian yên tĩnh",
                "Boutique hotel - Phong cách độc đáo"
            ],
            "mid_range": [
                "Khách sạn 3-4 sao - Vị trí thuận tiện",
                "Hotel boutique - Dịch vụ tốt, giá hợp lý",
                "Khách sạn trung tâm - Gần điểm tham quan"
            ],
            "budget": [
                "Hostel chất lượng cao - Gặp gỡ bạn bè mới",
                "Nhà nghỉ sạch sẽ - Tiết kiệm chi phí",
                "Hotel mini - Đầy đủ tiện nghi cơ bản"
            ]
        }
        
        # Find matching destination
        dest_key = None
        destination_lower = destination.lower()
        for key in recommendations.keys():
            if key in destination_lower or destination_lower in key:
                dest_key = key
                break
        
        # Get recommendations
        if dest_key and dest_key in recommendations:
            recs = recommendations[dest_key].get(budget_range, default_recs[budget_range])
        else:
            recs = default_recs[budget_range]
        
        # Format response
        formatted_recs = []
        for i, rec in enumerate(recs, 1):
            formatted_recs.append(f"{i}. **{rec}**")
        
        return f"""
🏨 **GỢI Ý KHÁCH SẠN TẠI {destination.upper()}**
👥 Cho {guest_info} | 💰 Phân khúc: {budget_range}

⚠️ *Thông tin từ cơ sở dữ liệu địa phương (API tạm thời không khả dụng)*

{"".join([f"\n{rec}" for rec in formatted_recs])}

💡 **HƯỚNG DẪN ĐẶT PHÒNG:**
• Kiểm tra giá và tình trạng phòng trực tiếp
• Đặt phòng qua các platform: Booking.com, Agoda, Traveloka
• Liên hệ trực tiếp khách sạn để có giá tốt nhất
• Đọc review và chính sách hủy phòng

📍 **Lưu ý:** Giá có thể thay đổi theo mùa và sự kiện đặc biệt tại {destination}
"""


class HotelDetailsTool(BaseTool):
    """Tool for getting detailed hotel information"""
    name: str = "get_hotel_details"
    description: str = "Get detailed information about a specific hotel"
    args_schema: type[BaseModel] = HotelDetailInput
    
    model_config = ConfigDict(extra='allow')
    
    def _run(self, hotel_id: str) -> str:
        """Get detailed hotel information"""
        return f"Chi tiết khách sạn ID {hotel_id} sẽ được cung cấp qua API booking platform."


class BookingAgent:
    """
    Agent for handling accommodation booking requests
    Enhanced with SerpApi integration and robust error handling
    """
    
    def __init__(self, llm):
        self.serpapi_hotels_tool = SerpApiHotelsTool()
        self.hotel_details_tool = HotelDetailsTool()
        
        self.agent = Agent(
            role="🏨 Chuyên Viên Đặt Phòng Khách Sạn",
            goal="Tìm kiếm và đề xuất các lựa chọn lưu trú phù hợp với ngân sách và yêu cầu của khách hàng sử dụng SerpApi Google Hotels API.",
            backstory="""Chuyên viên đặt phòng với 8 năm kinh nghiệm trong ngành khách sạn, có mạng lưới rộng khắp Việt Nam và hiểu rõ nhu cầu đa dạng của du khách từ budget backpacker đến luxury resort. Được trang bị công nghệ SerpApi để tìm kiếm thông tin khách sạn real-time.
            
            QUAN TRỌNG: Luôn trả lời trực tiếp với thông tin khách sạn cuối cùng, KHÔNG bao gồm quá trình suy nghĩ, phân tích, hay các bước 'Thought:', 'Action:', 'I now know the final answer' trong câu trả lời. Chỉ đưa ra kết quả tìm kiếm khách sạn hoàn chỉnh và chuyên nghiệp.""",
            llm=llm,
            allow_delegation=False,
            verbose=False,
            tools=[SerpApiHotelsTool()]
        )
    
    def create_task(self, request: str, context: dict) -> Task:
        """
        Create a hotel booking task with automatic parameter extraction.
        
        Args:
            request: User request for booking
            context: The conversation context from memory agent
        """
        
        # Extract parameters from request and context
        destination = self._extract_destination(request, context)
        dates_info = self._extract_dates(request, context)
        guests_info = self._extract_guests(request, context)
        budget_info = self._extract_budget(request, context)
        
        relevant_history = context.get("relevant_history", "")
        
        print(f"🏨 BookingAgent Task Parameters:")
        print(f"   📍 Destination: {destination}")
        print(f"   📅 Check-in: {dates_info['check_in']}")
        print(f"   📅 Check-out: {dates_info['check_out']}")
        print(f"   👥 Guests: {guests_info['adults']} adults, {guests_info['children']} children")
        print(f"   💰 Budget: {budget_info}")
        
        desc = f"""
            Dựa vào lịch sử trò chuyện sau:
            ---
            {relevant_history}
            ---
            
            Yêu cầu của khách: "{request}"
            
            Thông tin đã trích xuất:
            - Điểm đến: {destination}
            - Ngày nhận phòng: {dates_info['check_in']}
            - Ngày trả phòng: {dates_info['check_out']}
            - Số khách: {guests_info['adults']} người lớn, {guests_info['children']} trẻ em
            - Ngân sách: {budget_info}

            Nhiệm vụ:
            1. **BẮT BUỘC: Sử dụng tool `hotel_search`** để tìm khách sạn phù hợp tại {destination}.
               - Tham số tìm kiếm:
                 * destination: "{destination}"
                 * check_in_date: "{dates_info['check_in']}"
                 * check_out_date: "{dates_info['check_out']}"
                 * adults: {guests_info['adults']}
                 * children: {guests_info['children']}
                 * budget_range: "{budget_info}"
            
            2. **Phân tích kết quả từ SerpApi và bổ sung thông tin:**
               - Giải thích tại sao từng khách sạn phù hợp với yêu cầu
               - So sánh ưu nhược điểm của các lựa chọn
               - Đưa ra gợi ý dựa trên sở thích từ lịch sử trò chuyện
            
            3. **Chọn tối đa 5 khách sạn phù hợp nhất** dựa trên:
               - Độ phù hợp với sở thích đã phân tích
               - Vị trí thuận tiện cho du lịch
               - Tiện nghi và dịch vụ
               - Đánh giá từ khách hàng
               - Giá cả trong ngân sách
            
            4. **Thông tin chi tiết cho mỗi khách sạn:**
               - Tên và địa chỉ cụ thể
               - Giá phòng cho {guests_info['adults']} người lớn, {guests_info['children']} trẻ em
               - Điểm đánh giá và tóm tắt nhận xét
               - Tiện nghi nổi bật (Wi-Fi, bể bơi, gym, spa, v.v.)
               - Lưu ý đặc biệt (gần sân bay, view đẹp, có ưu đãi, v.v.)
            
            5. **Lời khuyên đặt phòng:**
               - Platform đặt phòng tốt nhất cho từng khách sạn
               - Thời điểm tốt nhất để đặt
               - Cách tiết kiệm chi phí
               - Lưu ý về chính sách hủy phòng
            
            Trả lời theo format:
            **🏨 KHÁCH SẠN ĐỀ XUẤT TẠI {destination.upper()}**
            👥 Cho {guests_info['adults']} người lớn, {guests_info['children']} trẻ em | 📅 {dates_info['check_in']} → {dates_info['check_out']}
            
            [Kết quả từ hotel_search tool sẽ được hiển thị ở đây]
            
            **💡 PHÂN TÍCH & GỢI Ý:**
            • [Phân tích tổng quan về các lựa chọn]
            • [Gợi ý cụ thể dựa trên sở thích và ngân sách]
            • [So sánh ưu nhược điểm]
              **📞 HƯỚNG DẪN ĐẶT PHÒNG:**
            • [Lời khuyên cụ thể cho {destination}]
            • [Platform đặt phòng được đề xuất]
            • [Thời điểm tốt nhất để đặt và mẹo tiết kiệm]

            **QUAN TRỌNG: Chỉ trả lời với thông tin khách sạn cuối cùng. KHÔNG bao gồm 'Thought:', 'Action:', 'I now know the final answer', hay quá trình suy nghĩ trong câu trả lời.**

            Trả lời bằng tiếng Việt, chi tiết và hữu ích. Đảm bảo sử dụng tool hotel_search trước khi phân tích.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Danh sách 5 khách sạn phù hợp tại {destination} với thông tin chi tiết về giá, tiện nghi, đánh giá và hướng dẫn đặt phòng cụ thể."
        )
    
    def _extract_destination(self, request: str, context: dict) -> str:
        """Extract destination from request or context"""
        # Try to extract from request first
        destination = detect_destination(request)
        
        # If not found, check context
        if not destination:
            # Check recent interactions
            recent_interactions = context.get("recent_interactions", [])
            for interaction in reversed(recent_interactions):
                if "destination" in interaction.get("extracted_info", {}):
                    destination = interaction["extracted_info"]["destination"]
                    break
            
            # Check current context
            if not destination:
                destination = context.get("current_context", {}).get("current_destination")
        
        return destination or "Việt Nam"
    
    def _extract_dates(self, request: str, context: dict) -> dict:
        """Extract check-in and check-out dates"""
        # Try to extract from request
        time_info = detect_time(request)
        
        if time_info and "start_date" in time_info:
            check_in = time_info["start_date"]
            
            # Calculate check-out date
            trip_length = detect_trip_length(request)
            if trip_length:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = check_in_date + timedelta(days=trip_length)
                check_out = check_out_date.strftime("%Y-%m-%d")
            else:
                # Default to 2 nights
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = check_in_date + timedelta(days=2)
                check_out = check_out_date.strftime("%Y-%m-%d")
        else:
            # Default dates - next week for 2 nights
            default_check_in = datetime.now() + timedelta(days=7)
            default_check_out = default_check_in + timedelta(days=2)
            
            check_in = default_check_in.strftime("%Y-%m-%d")
            check_out = default_check_out.strftime("%Y-%m-%d")
        
        return {
            "check_in": check_in,
            "check_out": check_out
        }
    
    def _extract_guests(self, request: str, context: dict) -> dict:
        """Extract number of guests from request"""
        adults = 2  # default
        children = 0  # default
        
        # Look for guest numbers in request
        guest_patterns = [
            r'(\d+)\s*người',
            r'(\d+)\s*khách',
            r'(\d+)\s*adult',
            r'(\d+)\s*người lớn',
        ]
        
        for pattern in guest_patterns:
            match = re.search(pattern, request.lower())
            if match:
                adults = int(match.group(1))
                break
        
        # Look for children
        children_patterns = [
            r'(\d+)\s*trẻ\s*em',
            r'(\d+)\s*children',
            r'(\d+)\s*child',
        ]
        
        for pattern in children_patterns:
            match = re.search(pattern, request.lower())
            if match:
                children = int(match.group(1))
                break
        
        return {
            "adults": adults,
            "children": children,
            "total": adults + children,
            "note": f"{adults} người lớn" + (f", {children} trẻ em" if children > 0 else "")
        }
    
    def _extract_budget(self, request: str, context: dict) -> str:
        """Extract budget range from request or preferences"""
        request_lower = request.lower()
        
        # Budget keywords
        luxury_keywords = ['luxury', 'cao cấp', 'sang trọng', '5 sao', '4 sao', 'resort', 'đắt tiền']
        budget_keywords = ['budget', 'rẻ', 'tiết kiệm', 'bình dân', 'hostel', 'nhà nghỉ']
        
        if any(keyword in request_lower for keyword in luxury_keywords):
            return "luxury"
        elif any(keyword in request_lower for keyword in budget_keywords):
            return "budget"
        else:
            return "mid_range"
        
        if not self.api_key:
            return self._get_fallback_recommendations(destination, budget_range)
        
        try:
            # SerpApi Google Hotels endpoint
            url = "https://serpapi.com/search"
            
            params = {
                "api_key": self.api_key,
                "engine": "google_hotels",
                "q": f"hotels in {destination}",
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "adults": number_of_guests,
                "currency": "USD",  # Can be changed to VND if supported
                "gl": "vn",  # Country for search
                "hl": "vi",  # Language
                "num": 20  # Number of results
            }
            
            print(f"🔍 Searching hotels via SerpApi: {destination}, {check_in_date} to {check_out_date}, {number_of_guests} guests")
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API errors
                if "error" in data:
                    print(f"SerpApi Error: {data['error']}")
                    return self._get_fallback_recommendations(destination, budget_range)
                
                return self._format_serpapi_results(data, budget_range, destination)
            
            elif response.status_code == 401:
                print("SerpApi Authentication Error: Invalid API key")
                return self._get_fallback_recommendations(destination, budget_range)
            
            elif response.status_code == 429:
                print("SerpApi Rate Limit Exceeded")
                return self._get_fallback_recommendations(destination, budget_range)
            
            else:
                print(f"SerpApi HTTP Error: {response.status_code}")
                return self._get_fallback_recommendations(destination, budget_range)
                
        except requests.exceptions.Timeout:
            print("SerpApi request timeout")
            return self._get_fallback_recommendations(destination, budget_range)
        
        except requests.exceptions.RequestException as e:
            print(f"SerpApi request error: {e}")
            return self._get_fallback_recommendations(destination, budget_range)
        
        except Exception as e:
            print(f"Unexpected error in hotel search: {e}")
            return self._get_fallback_recommendations(destination, budget_range)
    
    def _format_serpapi_results(self, data: Dict, budget_range: str, destination: str) -> str:
        """Format SerpApi hotel search results with enhanced error handling"""
        
        # Extract hotels from SerpApi response
        hotels = data.get('properties', [])
        
        if not hotels:
            print("No hotels found in SerpApi response")
            return self._get_fallback_recommendations(destination, budget_range)
        
        print(f"Found {len(hotels)} hotels from SerpApi")
        
        # Filter hotels by budget and quality
        filtered_hotels = self._filter_hotels_by_budget(hotels, budget_range)
        
        if not filtered_hotels:
            print(f"No hotels match budget range: {budget_range}")
            filtered_hotels = hotels[:5]  # Fallback to first 5 hotels
        
        result = f"🏨 **KHÁCH SẠN ĐỀ XUẤT TẠI {destination.upper()}**\n\n"
        result += f"📅 Tìm kiếm cho {len(filtered_hotels)} khách sạn phù hợp với ngân sách **{budget_range}**\n\n"
        
        for i, hotel in enumerate(filtered_hotels[:5], 1):
            try:
                # Extract hotel information with fallbacks
                name = hotel.get('name', 'Khách sạn không tên')
                
                # Handle price information
                price_info = self._extract_price_info(hotel)
                
                # Extract rating
                rating = hotel.get('overall_rating', hotel.get('rating'))
                rating_text = f"{rating}/5.0" if rating else "Chưa có đánh giá"
                
                # Extract location/address
                location = hotel.get('neighborhood', hotel.get('location', hotel.get('address', 'Vị trí trung tâm')))
                
                # Extract amenities
                amenities = self._extract_amenities(hotel)
                
                # Extract images
                images = hotel.get('images', [])
                has_photos = len(images) > 0
                
                # Build hotel entry
                result += f"**{i}. {name}**\n"
                result += f"💰 **Giá:** {price_info}\n"
                result += f"⭐ **Đánh giá:** {rating_text}\n"
                result += f"📍 **Vị trí:** {location}\n"
                
                if amenities:
                    result += f"🏊 **Tiện nghi:** {', '.join(amenities[:4])}\n"
                
                if has_photos:
                    result += f"📷 **Hình ảnh:** Có {len(images)} ảnh\n"
                
                # Add booking link if available
                if 'link' in hotel:
                    result += f"🔗 **Đặt phòng:** {hotel['link']}\n"
                
                result += "\n"
                
            except Exception as e:
                print(f"Error formatting hotel {i}: {e}")
                # Continue with next hotel
                continue
        
        # Add booking tips
        result += self._get_booking_tips(destination)
        
        return result
    
    def _extract_price_info(self, hotel: Dict) -> str:
        """Extract and format price information from hotel data"""
        
        # Try different price fields
        price_fields = ['rate_per_night', 'price', 'total_rate', 'nightly_rate']
        
        for field in price_fields:
            if field in hotel and hotel[field]:
                price_data = hotel[field]
                
                if isinstance(price_data, dict):
                    # Handle complex price structure
                    amount = price_data.get('lowest', price_data.get('value', price_data.get('amount')))
                    currency = price_data.get('currency', 'USD')
                    
                    if amount:
                        return f"{amount} {currency}/đêm"
                
                elif isinstance(price_data, (int, float)):
                    return f"${price_data}/đêm"
                
                elif isinstance(price_data, str):
                    return price_data
        
        # Fallback if no price found
        return "Liên hệ để biết giá"
    
    def _extract_amenities(self, hotel: Dict) -> List[str]:
        """Extract amenities from hotel data"""
        amenities = []
        
        # Check various amenity fields
        amenity_fields = ['amenities', 'highlights', 'features', 'services']
        
        for field in amenity_fields:
            if field in hotel and isinstance(hotel[field], list):
                amenities.extend(hotel[field])
        
        # Common amenity mappings (English to Vietnamese)
        amenity_translations = {
            'Free WiFi': 'WiFi miễn phí',
            'Swimming pool': 'Hồ bơi', 
            'Gym': 'Phòng gym',
            'Restaurant': 'Nhà hàng',
            'Bar': 'Quầy bar',
            'Spa': 'Spa',
            'Parking': 'Bãi đỗ xe',
            'Air conditioning': 'Điều hòa',
            'Room service': 'Dịch vụ phòng',
            'Business center': 'Trung tâm thương mại'
        }
        
        # Translate amenities
        translated_amenities = []
        for amenity in amenities[:10]:  # Limit to first 10
            if isinstance(amenity, str):
                translated = amenity_translations.get(amenity, amenity)
                if translated not in translated_amenities:
                    translated_amenities.append(translated)
        
        return translated_amenities
    
    def _filter_hotels_by_budget(self, hotels: List[Dict], budget_range: str) -> List[Dict]:
        """Filter hotels by budget range using rating and price indicators"""
        
        if budget_range == "luxury":
            # Filter for high-end hotels
            return [h for h in hotels if 
                   (h.get('overall_rating', 0) >= 4.5 or h.get('rating', 0) >= 4.5) and
                   self._is_luxury_hotel(h)]
        
        elif budget_range == "budget":
            # Filter for budget-friendly hotels 
            return [h for h in hotels if 
                   (h.get('overall_rating', 5) <= 3.5 or h.get('rating', 5) <= 3.5) or
                   self._is_budget_hotel(h)]
        
        else:  # mid_range
            # Return mid-range hotels or all if filtering fails
            mid_range = [h for h in hotels if 
                        3.5 < (h.get('overall_rating', 4) or h.get('rating', 4)) < 4.5]
            return mid_range if mid_range else hotels
    
    def _is_luxury_hotel(self, hotel: Dict) -> bool:
        """Check if hotel appears to be luxury based on name and amenities"""
        name = hotel.get('name', '').lower()
        luxury_keywords = ['resort', 'luxury', 'grand', 'premium', 'five star', '5 star', 'intercontinental', 'marriott', 'hilton', 'sheraton']
        return any(keyword in name for keyword in luxury_keywords)
    
    def _is_budget_hotel(self, hotel: Dict) -> bool:
        """Check if hotel appears to be budget-friendly based on name"""
        name = hotel.get('name', '').lower()
        budget_keywords = ['hostel', 'backpacker', 'budget', 'inn', 'lodge', 'guesthouse', 'homestay']
        return any(keyword in name for keyword in budget_keywords)
    
    def _get_booking_tips(self, destination: str) -> str:
        """Get location-specific booking tips"""
        tips = f"\n💡 **TIPS ĐẶT PHÒNG TẠI {destination.upper()}:**\n"
        tips += "• So sánh giá trên Booking.com, Agoda, Hotels.com\n"
        tips += "• Đặt trước 2-4 tuần để có giá tốt\n"
        tips += "• Kiểm tra chính sách hủy miễn phí\n"
        tips += "• Đọc review gần đây từ khách Việt Nam\n"
        tips += "• Xác nhận địa chỉ và cách di chuyển từ sân bay\n"
        
        # Add destination-specific tips
        dest_lower = destination.lower()
        if 'hà nội' in dest_lower or 'hanoi' in dest_lower:
            tips += "• Nên ở gần phố cổ để dễ di chuyển\n"
        elif 'hội an' in dest_lower:
            tips += "• Chọn khách sạn trong hoặc gần phố cổ\n"
        elif 'sa pa' in dest_lower:
            tips += "• Ưu tiên khách sạn có view núi/ruộng bậc thang\n"
        
        return tips
    
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
    Enhanced with SerpApi integration and robust error handling
    """
    
    def __init__(self, llm):
        self.serpapi_hotels_tool = SerpApiHotelsTool()
        self.hotel_details_tool = HotelDetailsTool()
        
        self.agent = Agent(
            role="🏨 Chuyên Viên Đặt Phòng Khách Sạn",
            goal="Tìm kiếm và đề xuất các lựa chọn lưu trú phù hợp với ngân sách và yêu cầu của khách hàng.",
            backstory="Chuyên viên đặt phòng với 8 năm kinh nghiệm trong ngành khách sạn, có mạng lưới rộng khắp Việt Nam và hiểu rõ nhu cầu đa dạng của du khách từ budget backpacker đến luxury resort.",
            llm=llm,
            allow_delegation=False,
            tools=[SerpApiHotelsTool()]
        )

    def create_task(self, request: str, context: dict) -> Task:
        """
        Create a hotel booking task with automatic parameter extraction.
        
        Args:
            request: User request for booking
            context: The conversation context from memory agent
        """
        
        # Extract parameters from request and context
        destination = self._extract_destination(request, context)
        dates_info = self._extract_dates(request, context)
        guests_info = self._extract_guests(request, context)
        budget_info = self._extract_budget(request, context)
        
        relevant_history = context.get("relevant_history", "")
        
        print(f"🏨 BookingAgent Task Parameters:")
        print(f"   📍 Destination: {destination}")
        print(f"   📅 Check-in: {dates_info['check_in']}")
        print(f"   📅 Check-out: {dates_info['check_out']}")
        print(f"   👥 Guests: {guests_info['count']}")
        print(f"   💰 Budget: {budget_info}")
        
        desc = f"""
            Dựa vào lịch sử trò chuyện sau:
            ---
            {relevant_history}
            ---
            
            Yêu cầu của khách: "{request}"
            
            Thông tin đã trích xuất:
            - Điểm đến: {destination}
            - Ngày nhận phòng: {dates_info['check_in']}
            - Ngày trả phòng: {dates_info['check_out']}
            - Số khách: {guests_info['count']} người ({guests_info['note']})
            - Ngân sách: {budget_info}

            Nhiệm vụ:
            1. **BẮT BUỘC: Sử dụng tool `hotel_search`** để tìm khách sạn phù hợp tại {destination}.
               - Tham số tìm kiếm:
                 * destination: "{destination}"
                 * check_in_date: "{dates_info['check_in']}"
                 * check_out_date: "{dates_info['check_out']}"
                 * number_of_guests: {guests_info['count']}
                 * budget_range: "{budget_info}"
            
            2. **Phân tích sở thích lưu trú từ yêu cầu và lịch sử trò chuyện:**
               - Loại hình: resort, khách sạn, homestay, hostel
               - Tiện nghi: hồ bơi, gần biển, view đẹp, bữa sáng
               - Vị trí: trung tâm, gần sân bay, yên tĩnh
            
            3. **Đề xuất tối đa 5 khách sạn phù hợp nhất** dựa trên:
               - Độ phù hợp với sở thích đã phân tích
               - Vị trí thuận tiện cho du lịch
               - Tiện nghi và dịch vụ
               - Đánh giá từ khách hàng
               - Giá cả trong ngân sách
            
            4. **Thông tin chi tiết cho mỗi khách sạn:**
               - Tên và địa chỉ
               - Giá phòng cho {guests_info['count']} người
               - Điểm đánh giá và nhận xét
               - Tiện nghi nổi bật
               - Lưu ý đặc biệt (gần sân bay, view đẹp, v.v.)
            
            5. **Lời khuyên đặt phòng:**
               - Các trang web/app đặt phòng tốt nhất
               - Thời điểm đặt phòng để có giá tốt
               - Điều cần lưu ý khi đặt phòng tại {destination}
            
            **Định dạng trả lời:**
            📋 **THÔNG TIN TÌM KIẾM:**
            - Điểm đến: {destination}
            - Ngày: {dates_info['check_in']} đến {dates_info['check_out']}
            - Số khách: {guests_info['count']} người
            - Ngân sách: {budget_info}
            
            🏨 **KHÁCH SẠN ĐỀ XUẤT:**
            
            1. **[Tên khách sạn]**
               - 📍 Địa chỉ: [Địa chỉ cụ thể]
               - 💰 Giá phòng: [Khoảng giá/đêm]
               - ⭐ Đánh giá: [X.X/5.0 - Nhận xét tóm tắt]
               - 🏊 Tiện nghi: [Danh sách tiện nghi]
               - 📝 Ghi chú: [Lưu ý đặc biệt]
            
            [Tiếp tục cho 4 khách sạn khác...]
            
            💡 **HƯỚNG DẪN ĐẶT PHÒNG:**
            - [Lời khuyên cụ thể cho {destination}]
            - [Platform đặt phòng được đề xuất]
            - [Thời điểm tốt nhất để đặt]
            - [Điều cần chú ý]

            Trả lời bằng tiếng Việt, chi tiết và thực tế. Nếu tool tìm kiếm không hoạt động, hãy sử dụng kiến thức để đưa ra gợi ý khách sạn phù hợp với ngân sách và khu vực.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Danh sách khách sạn phù hợp tại {destination} với thông tin chi tiết về giá cả, tiện nghi, đánh giá và hướng dẫn đặt phòng."
        )
    
    def _extract_destination(self, request: str, context: dict) -> str:
        """Extract destination from request or context"""
        # First try to extract from current request
        destination = detect_destination(request)
        
        # If not found, try to get from context
        if not destination:
            current_context = context.get("current_context", {})
            destination = current_context.get("current_destination")
        
        # If still not found, try to extract from conversation history
        if not destination:
            history = context.get("relevant_history", "")
            destination = detect_destination(history)
        
        return destination or "Việt Nam"
    
    def _extract_dates(self, request: str, context: dict) -> dict:
        """Extract check-in and check-out dates"""
        # Try to detect dates from request
        time_info = detect_time(request)
        
        today = datetime.now()
        
        if time_info and time_info.get("start_date"):
            check_in_date = time_info["start_date"]
            # If no trip length specified, default to 2 nights
            trip_length = detect_trip_length(request) or 2
            check_out = datetime.strptime(check_in_date, "%Y-%m-%d") + timedelta(days=trip_length)
            check_out_date = check_out.strftime("%Y-%m-%d")
        else:
            # Default to tomorrow for 2 nights
            tomorrow = today + timedelta(days=1)
            check_in_date = tomorrow.strftime("%Y-%m-%d")
            check_out_date = (tomorrow + timedelta(days=2)).strftime("%Y-%m-%d")
        
        return {
            "check_in": check_in_date,
            "check_out": check_out_date
        }
    
    def _extract_guests(self, request: str, context: dict) -> dict:
        """Extract number of guests from request"""
        # Look for explicit numbers
        import re
        
        # Try to find guest numbers in request
        guest_patterns = [
            r'(\d+)\s*người',
            r'(\d+)\s*khách',
            r'(\d+)\s*guest',
            r'(\d+)\s*pax'
        ]
        
        for pattern in guest_patterns:
            match = re.search(pattern, request.lower())
            if match:
                count = int(match.group(1))
                return {"count": count, "note": f"theo yêu cầu"}
        
        # Check for family keywords
        if any(word in request.lower() for word in ['gia đình', 'family', 'vợ chồng', 'couple']):
            return {"count": 2, "note": "gia đình/cặp đôi"}
        
        # Default
        return {"count": 2, "note": "mặc định"}
    
    def _extract_budget(self, request: str, context: dict) -> str:
        """Extract budget range from request or preferences"""
        preferences = extract_preferences(request)
        budget = preferences.get('budget', 'mid_range')
        
        # Check for explicit budget mentions
        request_lower = request.lower()
        if any(word in request_lower for word in ['rẻ', 'cheap', 'budget', 'tiết kiệm', 'bình dân']):
            return 'budget'
        elif any(word in request_lower for word in ['cao cấp', 'luxury', 'sang trọng', '5 sao', '4 sao']):
            return 'luxury'
        
        return budget
