from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
from core.utils import extract_days

class EnhancedItineraryAgent:
    def __init__(self, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="📅 Chuyên Gia Lịch Trình với RAG",
            goal="Tạo lịch trình chi tiết tích hợp địa điểm và ẩm thực.",
            backstory="Điều phối viên tour 12 năm kinh nghiệm, dùng RAG để tối ưu lịch trình.",
            llm=ChatOpenAI(model=settings["models"]["gpt_4o_mini"], temperature=0.25),
            allow_delegation=False,
            tools=[self.rag_tools.general_search, self.rag_tools.location_search, self.rag_tools.food_search]
        )

    def create_task(self, request: str, dest_name: str, loc_info: str, food_info: str) -> Task:
        days = extract_days(request, 2)
        skeleton = "\n".join([f"📅 **NGÀY {i+1}**\n🌅 Sáng: ...\n🍽️ Trưa: ...\n🌆 Chiều: ...\n🌃 Tối: ..." for i in range(days)])
        desc = f"""
            Yêu cầu: "{request}"
            Điểm đến: {dest_name}
            Địa điểm: {loc_info}
            Ẩm thực: {food_info}

            Nhiệm vụ:
            1. Lên lịch trình {days} ngày dựa trên yêu cầu, địa điểm và ẩm thực.
            2. Phân bổ địa điểm và món ăn vào các buổi, logic về thời gian.
            3. Dùng RAG tools để bổ sung thông tin nếu cần (hoạt động, giao thông...).

            Khung:
            {skeleton}
            """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Lịch trình {days} ngày chi tiết."
        )