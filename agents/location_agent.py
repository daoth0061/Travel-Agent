from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
import os


class EnhancedLocationAgent:
    def __init__(self, llm, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🗺️ Chuyên Gia Địa Điểm với RAG",
            goal="Sử dụng RAG để tìm và đề xuất 3 điểm tham quan phù hợp nhất dựa trên yêu cầu của khách.",
            backstory="Chuyên gia du lịch 15 năm kinh nghiệm, sử dụng công nghệ RAG để tìm kiếm thông tin chính xác về các điểm đến và sở thích của khách.",
            llm=llm,
            # verbose=True, # REMOVED: verbose from agent, set at Crew level
            allow_delegation=False,
            tools=[
                self.rag_tools.location_search,
                self.rag_tools.general_search
            ]
        )

    def create_task(self, request: str, dest_name: str) -> Task:
        desc = f"""
            Yêu cầu của khách: "{request}"
            Điểm đến: {dest_name}

            Nhiệm vụ:
            1. Sử dụng tool `location_search` để tìm thông tin về các địa điểm tại {dest_name} liên quan đến yêu cầu của khách.
            2. Phân tích sở thích của khách từ yêu cầu (ví dụ: thích lịch sử, thích thiên nhiên, muốn thư giãn, muốn khám phá văn hóa...).
            3. Chọn 3 địa điểm phù hợp nhất dựa trên thông tin RAG và sở thích đã phân tích.
            4. Đối với mỗi địa điểm, giải thích lý do tại sao nó phù hợp và ước tính thời gian tham quan.

            Trả lời theo format:
            1. [Địa điểm] – [Lý do phù hợp] – [Thời gian tham quan ước tính]
            2. [Địa điểm] – [Lý do phù hợp] – [Thời gian tham quan ước tính]
            3. [Địa điểm] – [Lý do phù hợp] – [Thời gian tham quan ước tính]

            Trả lời bằng tiếng Việt.
        """
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Danh sách 3 địa điểm được đề xuất với lý do và thời gian tham quan ước tính."
        )