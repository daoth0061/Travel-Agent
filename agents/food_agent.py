import os
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings

class EnhancedFoodAgent:
    def __init__(self, llm, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🍜 Chuyên Gia Ẩm Thực với RAG",
            goal="Sử dụng RAG để tìm và gợi ý 2 món đặc sản phù hợp nhất dựa trên yêu cầu của khách.",
            backstory="Food blogger chuyên nghiệp với 10 năm kinh nghiệm, sử dụng RAG để tìm kiếm thông tin chính xác về ẩm thực địa phương và khẩu vị khách hàng.",
            llm=llm,
            # verbose=True, # REMOVED: verbose from agent, set at Crew level
            allow_delegation=False,
            tools=[
                self.rag_tools.food_search,
                self.rag_tools.general_search
            ]
        )

    def create_task(self, request: str, dest_name: str) -> Task:
        desc = f"""
            Yêu cầu của khách: "{request}"
            Điểm đến: {dest_name}

            Nhiệm vụ:
            1. Sử dụng tool `food_search` để tìm thông tin về các món ăn đặc sản tại {dest_name} liên quan đến yêu cầu của khách.
            2. Phân tích khẩu vị và sở thích của khách từ yêu cầu (ví dụ: thích ăn cay, thích đồ ngọt, muốn thử món truyền thống, món ăn đường phố...).
            3. Chọn 2 món đặc sản phù hợp nhất dựa trên thông tin RAG và sở thích đã phân tích.
            4. Đối với mỗi món ăn, mô tả hương vị chính và gợi ý các quán ăn nổi tiếng hoặc khoảng giá cả nếu có thông tin.

            Trả lời theo format:
            1. [Món ăn] – [Mô tả hương vị chính] – [Gợi ý quán/khoảng giá cả]
            2. [Món ăn] – [Mô tả hương vị chính] – [Gợi ý quán/khoảng giá cả]

            Trả lời bằng tiếng Việt.
        """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Danh sách 2 món đặc sản được gợi ý với mô tả hương vị và thông tin quán/giá cả."
        )