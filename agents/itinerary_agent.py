"""
Enhanced Itinerary Agent with sophisticated planning scenarios
Implements PlanningWithoutTime and PlanningWithTime scenarios
"""
import os
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
from core.utils import detect_destination, detect_trip_length, detect_time, extract_preferences
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class AdvancedItineraryAgent:
    """
    The most complex agent, responsible for creating detailed, multi-day travel plans
    by synthesizing information from the FoodAgent and LocationAgent.
    """
    
    def __init__(self, llm, rag_tools: TravelRAGTools, food_agent, location_agent):
        self.rag_tools = rag_tools
        self.food_agent = food_agent
        self.location_agent = location_agent
        self.agent = Agent(
            role="📅 Chuyên Gia Lịch Trình Du Lịch Cao Cấp",
            goal="Tạo lịch trình du lịch chi tiết và được tối ưu hóa bằng cách tổng hợp thông tin từ các chuyên gia địa điểm và ẩm thực, có thể tích hợp dữ liệu thời tiết real-time để đưa ra kế hoạch hoàn hảo.",
            backstory="Chuyên gia lập kế hoạch du lịch với 15 năm kinh nghiệm, được đào tạo để tạo ra những lịch trình cân bằng giữa tham quan, ẩm thực và nghỉ ngơi. Có khả năng điều chỉnh kế hoạch dựa trên thời tiết thực tế và đảm bảo logic di chuyển hợp lý.",
            llm=llm,
            allow_delegation=False,
            tools=[
                self.rag_tools.general_search,
                self.rag_tools.location_search,
                self.rag_tools.food_search,
                self.rag_tools.weather_search,
                self.rag_tools.weather_recommendation
            ]
        )
    
    def extract_parameters(self, request: str) -> Dict[str, Any]:
        """
        Extract the three key parameters from user request:
        1. Destination
        2. Trip Length (in days) 
        3. Time/Dates
        """
        parameters = {
            "destination": detect_destination(request),
            "trip_length": detect_trip_length(request),
            "time_info": detect_time(request),
            "preferences": extract_preferences(request)
        }
        
        return parameters
    
    def calculate_resource_requirements(self, trip_length: int) -> Dict[str, int]:
        """
        Calculate the required number of food and location items based on trip length.
        
        Resource Calculation Logic:
        - Number of Foods: 2 * d (for noon and evening meals each day)
        - Number of Locations:
          - d = 1: 2 locations
          - d = 2 or 3: 2*d - 1 locations (last afternoon is for shopping)
          - d >= 4: 2*d - 2 locations (last day has only one activity slot for shopping)
        """
        
        food_count = 2 * trip_length
        
        if trip_length == 1:
            location_count = 2
        elif trip_length in [2, 3]:
            location_count = 2 * trip_length - 1
        else:  # trip_length >= 4
            location_count = 2 * trip_length - 2
            
        return {
            "food_items": food_count,
            "location_items": location_count
        }
    
    def get_resources_from_agents(self, destination: str, requirements: Dict[str, int], 
                                preferences: Dict[str, Any]) -> Dict[str, str]:
        """
        Call FoodAgent and LocationAgent to get required resources
        """
        # Prepare requests based on preferences
        food_request = f"Tìm {requirements['food_items']} món ăn đặc sản tại {destination}"
        if preferences.get('food_type'):
            food_request += f" theo phong cách {preferences['food_type']}"
            
        location_request = f"Tìm {requirements['location_items']} địa điểm tham quan tại {destination}"
        if preferences.get('activity_type'):
            location_request += f" phù hợp với sở thích {preferences['activity_type']}"
        
        # Get food recommendations
        food_task = self.food_agent.create_task(food_request, destination)
        food_result = "Đang lấy thông tin ẩm thực..."  # In real implementation, execute task
        
        # Get location recommendations  
        location_task = self.location_agent.create_task(location_request, destination)
        location_result = "Đang lấy thông tin địa điểm..."  # In real implementation, execute task
        
        return {
            "food_info": food_result,
            "location_info": location_result
        }
    
    def create_task_planning_without_time(self, request: str, destination: str, 
                                        trip_length: int, preferences: Dict[str, Any],
                                        resources: Dict[str, str]) -> Task:
        """
        Scenario A: PlanningWithoutTime
        Create itinerary without specific dates, focus on logical flow
        """
        
        # Generate skeleton based on overwhelm logic
        skeleton_days = []
        for day in range(1, trip_length + 1):
            if trip_length >= 4 and day == trip_length:
                # Last day for trips >= 4 days
                skeleton_days.append(f"""
📅 **NGÀY {day} - Free & Easy Day**
🌅 Sáng: Thời gian tự do khám phá cá nhân
🍽️ Trưa: [Món ăn từ FoodAgent]
🛍️ Chiều: Mua sắm quà lưu niệm 
🌃 Tối: [Món ăn từ FoodAgent]
""")
            elif (trip_length in [2, 3]) and day == trip_length:
                # Last day for 2-3 day trips
                skeleton_days.append(f"""
📅 **NGÀY {day}**
🌅 Sáng: [Hoạt động từ LocationAgent]
🍽️ Trưa: [Món ăn từ FoodAgent]
🛍️ Chiều: Mua sắm quà lưu niệm
🌃 Tối: [Món ăn từ FoodAgent] + hoạt động nhẹ nhàng phù hợp với {destination}
""")
            else:
                # Regular days
                skeleton_days.append(f"""
📅 **NGÀY {day}**
🌅 Sáng: [Hoạt động từ LocationAgent]
🍽️ Trưa: [Món ăn từ FoodAgent] 
🌆 Chiều: [Hoạt động từ LocationAgent]
🌃 Tối: [Món ăn từ FoodAgent] + hoạt động tối phù hợp với {destination}
""")
        
        skeleton = "\n".join(skeleton_days)
        
        desc = f"""
            Yêu cầu gốc: "{request}"
            Điểm đến: {destination}
            Số ngày: {trip_length}
            Sở thích: {preferences}
            
            THÔNG TIN TÀI NGUYÊN ĐÃ THU THẬP:
            Địa điểm: {resources['location_info']}
            Ẩm thực: {resources['food_info']}
            
            NHIỆM VỤ - PLANNING WITHOUT TIME:
            
            1. **Phân phối tài nguyên hợp lý:**
               - Sử dụng các địa điểm từ LocationAgent cho buổi sáng/chiều
               - Sử dụng các món ăn từ FoodAgent cho buổi trưa/tối
               - Đảm bảo logic di chuyển (gần nhau trong cùng ngày)
            
            2. **Áp dụng Logic Plan Overwhelm:**
               - Nếu {trip_length} = 2-3 ngày: Chiều cuối = "Mua sắm quà lưu niệm"
               - Nếu {trip_length} >= 4 ngày: Ngày cuối = "Free & Easy Day"
            
            3. **Hoạt động tối phù hợp với {destination}:**
               - Hà Nội: Dạo phố cổ, bia hơi, xem múa rối nước
               - Hội An: Ngắm đèn lồng, dạo bến Hoài, chợ đêm
               - Sa Pa: Ngắm sao, cafe thưởng thức view, trà ấm
               - Khác: Phù hợp với đặc trưng địa phương
            
            4. **Cân bằng lịch trình:**
               - Không quá tải hoạt động
               - Thời gian di chuyển hợp lý
               - Kết hợp tham quan và nghỉ ngơi
            
            5. **Không sử dụng thông tin thời tiết** (vì không có ngày cụ thể)
            
            KHUNG LỊCH TRÌNH:
            {skeleton}
            
            Trả lời bằng tiếng Việt với lịch trình chi tiết và logic.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Lịch trình {trip_length} ngày tại {destination} được tối ưu hóa logic, cân bằng giữa tham quan và ẩm thực, có tính đến đặc trưng địa phương."
        )
    
    def create_task_planning_with_time(self, request: str, destination: str, 
                                     trip_length: int, time_info: Dict[str, Any],
                                     preferences: Dict[str, Any], resources: Dict[str, str]) -> Task:
        """
        Scenario B: PlanningWithTime
        Create itinerary with specific dates and weather integration
        """
        
        start_date = time_info["start_date"]
        
        # Generate dates for each day
        dates = []
        for i in range(trip_length):
            current_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)
            dates.append(current_date.strftime("%Y-%m-%d"))
        
        # Generate skeleton with weather placeholders
        skeleton_days = []
        for day_num, date in enumerate(dates, 1):
            if trip_length >= 4 and day_num == trip_length:
                # Last day for trips >= 4 days
                skeleton_days.append(f"""
📅 **NGÀY {day_num} ({date}) - Free & Easy Day**
🌤️ Thời tiết tổng quan: [Sử dụng realtime_weather tool cho {destination} ngày {date}]

🌅 Sáng (8:00): [Thời tiết: realtime_weather hour=8 date={date}] 
   → Thời gian tự do khám phá cá nhân (điều chỉnh theo thời tiết)

🍽️ Trưa (12:00): [Thời tiết: realtime_weather hour=12 date={date}]
   → [Món ăn từ FoodAgent] (chọn nhà hàng trong/ngoài trời theo thời tiết)

🛍️ Chiều (16:00): [Thời tiết: realtime_weather hour=16 date={date}]
   → Mua sắm quà lưu niệm (chợ trong nhà nếu mưa, chợ ngoài trời nếu đẹp)

🌃 Tối (20:00): [Thời tiết: realtime_weather hour=20 date={date}]
   → [Món ăn từ FoodAgent] + hoạt động tối phù hợp với thời tiết
""")
            elif (trip_length in [2, 3]) and day_num == trip_length:
                # Last day for 2-3 day trips
                skeleton_days.append(f"""
📅 **NGÀY {day_num} ({date})**
🌤️ Thời tiết tổng quan: [Sử dụng realtime_weather tool cho {destination} ngày {date}]

🌅 Sáng (8:00): [Thời tiết: realtime_weather hour=8 date={date}]
   → [Hoạt động từ LocationAgent] (điều chỉnh indoor/outdoor theo thời tiết)

🍽️ Trưa (12:00): [Thời tiết: realtime_weather hour=12 date={date}]
   → [Món ăn từ FoodAgent] (chọn location có/không điều hòa theo nhiệt độ)

🛍️ Chiều (16:00): [Thời tiết: realtime_weather hour=16 date={date}]
   → Mua sắm quà lưu niệm (trung tâm thương mại nếu mưa/nóng)

🌃 Tối (20:00): [Thời tiết: realtime_weather hour=20 date={date}]
   → [Món ăn từ FoodAgent] + hoạt động tối phù hợp với thời tiết {destination}
""")
            else:
                # Regular days
                skeleton_days.append(f"""
📅 **NGÀY {day_num} ({date})**
🌤️ Thời tiết tổng quan: [Sử dụng realtime_weather tool cho {destination} ngày {date}]

🌅 Sáng (8:00): [Thời tiết: realtime_weather hour=8 date={date}]
   → [Hoạt động từ LocationAgent] (ưu tiên outdoor nếu đẹp trời, indoor nếu mưa)

🍽️ Trưa (12:00): [Thời tiết: realtime_weather hour=12 date={date}]
   → [Món ăn từ FoodAgent] (tránh ngoài trời nếu quá nóng >32°C)

🌆 Chiều (16:00): [Thời tiết: realtime_weather hour=16 date={date}]
   → [Hoạt động từ LocationAgent] (tận dụng ánh sáng đẹp cho chụp ảnh nếu trời trong)

🌃 Tối (20:00): [Thời tiết: realtime_weather hour=20 date={date}]
   → [Món ăn từ FoodAgent] + hoạt động tối phù hợp với thời tiết {destination}
""")
        
        skeleton = "\n".join(skeleton_days)
        
        desc = f"""
            Yêu cầu gốc: "{request}"
            Điểm đến: {destination}
            Số ngày: {trip_length}
            Ngày bắt đầu: {start_date}
            Thông tin thời gian: {time_info}
            Sở thích: {preferences}
            
            THÔNG TIN TÀI NGUYÊN ĐÃ THU THẬP:
            Địa điểm: {resources['location_info']}
            Ẩm thực: {resources['food_info']}
            
            NHIỆM VỤ - PLANNING WITH TIME (Weather-Enhanced):
            
            1. **BẮT BUỘC: Thu thập thông tin thời tiết chi tiết**
               - Sử dụng `realtime_weather` tool với city="{destination}" và days={trip_length}
               - Lấy thời tiết cho từng khung giờ: hour=8, hour=12, hour=16, hour=20
               - Cho mỗi ngày: {', '.join(dates)}
            
            2. **Tối ưu hóa hoạt động theo thời tiết từng giờ:**
               - Sáng có mưa → Bảo tàng, chợ đầm, cafe trong nhà
               - Trưa >32°C → Nhà hàng điều hòa, tránh outdoor
               - Chiều đẹp trời → Outdoor activities, chụp ảnh
               - Tối gió mạnh → Không gian đóng, tránh bến nước
            
            3. **Áp dụng travel recommendations từ weather tool:**
               - Mang ô nếu dự báo mưa
               - Kem chống nắng nếu UV cao
               - Áo ấm nếu nhiệt độ thấp
               - Nước uống nếu nóng và khô
            
            4. **Phân phối tài nguyên hợp lý theo thời tiết:**
               - Indoor locations cho ngày mưa/quá nóng
               - Outdoor scenic spots cho ngày đẹp trời
               - Restaurants có điều hòa cho trưa nóng
               - Street food cho tối mát mẻ
            
            5. **Áp dụng Logic Plan Overwhelm** (như Planning Without Time)
            
            6. **Bao gồm weather alerts nếu có**
            
            KHUNG LỊCH TRÌNH VỚI WEATHER INTEGRATION:
            {skeleton}
            
            Trả lời bằng tiếng Việt với lịch trình được tối ưu hóa hoàn toàn theo thời tiết thực tế.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Lịch trình {trip_length} ngày tại {destination} từ {start_date}, được tối ưu hóa hoàn toàn theo dự báo thời tiết real-time cho từng khung giờ, bao gồm travel recommendations cụ thể."
        )
    
    def create_task(self, request: str, context: Dict[str, Any] = None) -> Task:
        """
        Main entry point for creating itinerary tasks.
        Implements the full workflow: parameter extraction → resource calculation → plan generation
        """
        
        # Step 1: Extract parameters
        params = self.extract_parameters(request)
        
        destination = params["destination"]
        trip_length = params["trip_length"] or 2  # Default to 2 days
        time_info = params["time_info"]
        preferences = params["preferences"]
        
        # Handle missing destination
        if not destination:
            return self._create_missing_destination_task(request)
        
        # Step 2: Calculate resource requirements
        requirements = self.calculate_resource_requirements(trip_length)
        
        # Step 3: Get resources from other agents
        resources = self.get_resources_from_agents(destination, requirements, preferences)
        
        # Step 4: Choose planning scenario
        if time_info:
            # Scenario B: PlanningWithTime
            return self.create_task_planning_with_time(
                request, destination, trip_length, time_info, preferences, resources
            )
        else:
            # Scenario A: PlanningWithoutTime
            # First inform user about weather benefits
            inform_message = """
            ℹ️ **Lưu ý:** Bạn chưa cung cấp ngày cụ thể cho chuyến đi. 
            Việc cung cấp ngày sẽ giúp tôi tối ưu hóa lịch trình dựa trên dự báo thời tiết thực tế.
            Tuy nhiên, tôi sẽ tiếp tục tạo lịch trình tổng quát cho bạn.
            """
            
            return self.create_task_planning_without_time(
                request, destination, trip_length, preferences, resources
            )
    
    def _create_missing_destination_task(self, request: str) -> Task:
        """Handle case when destination is not detected"""
        desc = f"""
            Yêu cầu: "{request}"
            
            VẤN ĐỀ: Không thể xác định điểm đến cụ thể từ yêu cầu.
            
            Nhiệm vụ:
            1. Trả lời lịch sự rằng cần thông tin điểm đến cụ thể
            2. Liệt kê các điểm đến phổ biến ở Việt Nam
            3. Hỏi khách về sở thích để gợi ý điểm đến phù hợp
            
            Trả lời bằng tiếng Việt, thân thiện và hữu ích.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Yêu cầu khách cung cấp điểm đến cụ thể và gợi ý các điểm đến phổ biến."
        )