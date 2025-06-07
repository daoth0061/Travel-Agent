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
            role="📅 Chuyên Gia Lịch Trình với RAG",
            goal="Sử dụng RAG để tạo lịch trình du lịch chi tiết và tối ưu nhất, tích hợp thông tin về địa điểm và ẩm thực.",
            backstory="Điều phối viên tour dày dạn 12 năm kinh nghiệm, sử dụng RAG để tích hợp thông tin từ nhiều nguồn tạo lịch trình hoàn hảo, có tính đến logic di chuyển và thời gian.",
            llm=llm,
            # verbose=True, # REMOVED: verbose from agent, set at Crew level
            allow_delegation=False,
            tools=[
                self.rag_tools.general_search,
                self.rag_tools.location_search,
                self.rag_tools.food_search
            ]
        )

    def create_task(self, request: str, dest_name: str, loc_info: str, food_info: str) -> Task:
        days = extract_days(request, 2)
        skeleton = "\n".join(
            [f"📅 **NGÀY {i+1}**\n🌅 Sáng: ...\n🍽️ Trưa: ...\n🌆 Chiều: ...\n🌃 Tối: ..." for i in range(days)]
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
            1. Dựa vào "Yêu cầu của khách", "Thông tin địa điểm" và "Thông tin ẩm thực", hãy lên một lịch trình chi tiết và hợp lý cho {days} ngày tại {dest_name}.
            2. Phân bổ các địa điểm tham quan và món ăn đã được đề xuất vào các buổi (sáng, trưa, chiều, tối) của từng ngày một cách logic, có tính đến thời gian di chuyển hợp lý giữa các điểm.
            3. Sử dụng các RAG tools (general_search, location_search, food_search) để tìm thêm thông tin bổ sung nếu cần thiết để làm lịch trình phong phú hơn (ví dụ: các hoạt động buổi tối, gợi ý về giao thông, thời điểm tốt nhất để đi...).
            4. Đảm bảo lịch trình cân bằng giữa tham quan, ẩm thực và thời gian nghỉ ngơi.
            5. Thêm các tips hữu ích hoặc lưu ý quan trọng cho từng ngày hoặc cho toàn bộ chuyến đi.

            Khung lịch trình cần điền:
            {skeleton}

            Trả lời bằng tiếng Việt.
        """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Lịch trình chi tiết {days} ngày tại {dest_name} với thông tin tích hợp từ RAG và các gợi ý thêm."
        )