from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
import os

class EnhancedLocationAgent:
    def __init__(self, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🗺️ Chuyên Gia Địa Điểm với RAG",
            goal="Sử dụng RAG để đề xuất 3 điểm tham quan phù hợp nhất.",
            backstory="Chuyên gia du lịch 15 năm kinh nghiệm, dùng RAG để tìm thông tin chính xác.",
            llm=ChatOpenAI(model=settings["models"]["gpt_35"], 
                           temperature=0.3,
                           openai_api_key=os.getenv("OPENAI_API_KEY")),
            allow_delegation=False,
            tools=[self.rag_tools.location_search, self.rag_tools.general_search]
        )

    def create_task(self, request: str, dest_name: str) -> Task:
        desc = f"""
            Yêu cầu: "{request}"
            Điểm đến: {dest_name}

            Nhiệm vụ:
            1. Dùng `location_search` để tìm địa điểm tại {dest_name}.
            2. Phân tích sở thích từ yêu cầu (lịch sử, thiên nhiên, văn hóa...).
            3. Chọn 3 địa điểm phù hợp, giải thích lý do và thời gian tham quan.

            Format:
            1. [Địa điểm] – [Lý do] – [Thời gian]
            2. [Địa điểm] – [Lý do] – [Thời gian]
            3. [Địa điểm] – [Lý do] – [Thời gian]
            """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Danh sách 3 địa điểm với lý do và thời gian."
        )