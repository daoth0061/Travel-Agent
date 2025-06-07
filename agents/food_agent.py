import os
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings

class EnhancedFoodAgent:
    def __init__(self, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🍜 Chuyên Gia Ẩm Thực với RAG",
            goal="Sử dụng RAG để gợi ý 2 món đặc sản phù hợp nhất.",
            backstory="Food blogger 10 năm kinh nghiệm, dùng RAG để tìm thông tin ẩm thực.",
            llm=ChatOpenAI(model=settings["models"]["gpt_35"], 
                           temperature=0.3,
                           openai_api_key=os.getenv("OPENAI_API_KEY")),
            allow_delegation=False,
            tools=[self.rag_tools.food_search, self.rag_tools.general_search]
        )

    def create_task(self, request: str, dest_name: str) -> Task:
        desc = f"""
            Yêu cầu: "{request}"
            Điểm đến: {dest_name}

            Nhiệm vụ:
            1. Dùng `food_search` để tìm món ăn tại {dest_name}.
            2. Phân tích khẩu vị từ yêu cầu (cay, ngọt, truyền thống...).
            3. Chọn 2 món phù hợp, mô tả hương vị và gợi ý quán/giá.

            Format:
            1. [Món] – [Hương vị] – [Quán/Giá]
            2. [Món] – [Hương vị] – [Quán/Giá]
            """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Danh sách 2 món với mô tả và quán/giá."
        )