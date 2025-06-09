import os
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
from core.utils import extract_days

class EnhancedItineraryAgent:
    def __init__(self, llm, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="📅 Chuyên Gia Lịch Trình với RAG và Thời Tiết Real-time",
            goal="Sử dụng RAG và dữ liệu thời tiết real-time từ OpenWeatherMap API để tạo lịch trình du lịch chi tiết và tối ưu nhất, tích hợp thông tin về địa điểm, ẩm thực và điều kiện thời tiết thực tế.",
            backstory="Điều phối viên tour dày dạn 12 năm kinh nghiệm, được trang bị công cụ dự báo thời tiết real-time từ OpenWeatherMap API, sử dụng RAG để tích hợp thông tin từ nhiều nguồn tạo lịch trình hoàn hảo, có tính đến logic di chuyển, thời gian và điều kiện thời tiết thực tế.",
            llm=llm,
            # verbose=True, # REMOVED: verbose from agent, set at Crew level
            allow_delegation=False,
            tools=[
                self.rag_tools.general_search,
                self.rag_tools.location_search,
                self.rag_tools.food_search,
                self.rag_tools.weather_search  # Add real-time weather tool
            ]
        )

    def create_task(self, request: str, dest_name: str, loc_info: str, food_info: str) -> Task:
        days = extract_days(request, 2)
        skeleton = "\n".join(
            [f"📅 **NGÀY {i+1}**\n🌤️ Thời tiết: [Sử dụng realtime_weather tool để lấy dự báo thực tế]\n🌅 Sáng: ...\n🍽️ Trưa: ...\n🌆 Chiều: ...\n🌃 Tối: ..." for i in range(days)]
        )

        desc = f"""
            Yêu cầu của khách: "{request}"
            Điểm đến: {dest_name}
            Số ngày dự kiến: {days} ngày

            THÔNG TIN ĐỊA ĐIỂM ĐÃ ĐƯỢC CHỌN từ LocationAgent:
            {loc_info}

            THÔNG TIN ẨM THỰC ĐÃ ĐƯỢC CHỌN từ FoodAgent:
            {food_info}

            Nhiệm vụ:
            1. **BẮT BUỘC: Sử dụng `realtime_weather` tool để lấy dự báo thời tiết THỰC TẾ từ OpenWeatherMap API cho {dest_name} trong {days} ngày. Truyền tham số city="{dest_name}" và days={days}.**
            2. Dựa vào "Yêu cầu của khách", "Thông tin địa điểm", "Thông tin ẩm thực" và **dữ liệu thời tiết thực tế từ API**, hãy lên một lịch trình chi tiết và hợp lý cho {days} ngày tại {dest_name}.
            3. Phân bổ các địa điểm tham quan và món ăn đã được đề xuất vào các buổi (sáng, trưa, chiều, tối) của từng ngày một cách logic, có tính đến thời gian di chuyển hợp lý giữa các điểm VÀ **điều kiện thời tiết thực tế** (ví dụ: nếu API dự báo mưa, ưu tiên hoạt động trong nhà; nếu quá nóng, tránh hoạt động ngoài trời vào giữa trưa).
            4. **Áp dụng các travel recommendations từ weather tool** vào lịch trình (ví dụ: "mang ô" nếu có mưa, "mặc áo ấm" nếu lạnh, "tránh hoạt động ngoài trời giữa trưa" nếu quá nóng).
            5. **Chỉ sử dụng các RAG tools (general_search, location_search, food_search) để tìm thêm thông tin bổ sung NẾU THỰC SỰ CẦN THIẾT** để làm phong phú thêm lịch trình. **KHÔNG dùng RAG tools để tìm thông tin thời tiết - chỉ dùng realtime_weather tool.**
            6. **Nếu không có đủ hoạt động/địa điểm cụ thể từ thông tin đã cho, hãy đề xuất các hoạt động chung chung phù hợp với thời tiết thực tế** từ API như 'tự do tham quan khu vực trung tâm có mái che nếu API dự báo mưa', 'mua sắm quà lưu niệm tại chợ trong nhà', hoặc 'thời gian nghỉ ngơi tại khách sạn nếu thời tiết xấu'.
            7. Đảm bảo lịch trình cân bằng giữa tham quan, ẩm thực và thời gian nghỉ ngơi, có tính đến yếu tố thời tiết thực tế.
            8. Thêm các tips hữu ích hoặc lưu ý quan trọng cho từng ngày hoặc cho toàn bộ chuyến đi, **bao gồm cả những lưu ý về trang phục, vật dụng cần thiết dựa trên dự báo thời tiết thực tế từ OpenWeatherMap API**.

            Khung lịch trình cần điền (bao gồm thông tin thời tiết thực tế cho từng ngày):
            {skeleton}

            Trả lời bằng tiếng Việt.
        """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Lịch trình chi tiết {days} ngày tại {dest_name} với thông tin tích hợp từ RAG, dự báo thời tiết REAL-TIME từ OpenWeatherMap API cho từng ngày, và các gợi ý thêm được điều chỉnh dựa trên thời tiết thực tế."
        )