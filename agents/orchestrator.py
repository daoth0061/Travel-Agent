from crewai import Crew, Process
from agents.location_agent import EnhancedLocationAgent
from agents.food_agent import EnhancedFoodAgent
from agents.itinerary_agent import EnhancedItineraryAgent
from tools.rag_tools import TravelRAGTools
from tools.vector_store import TravelRAGSystem
from data.travel_data import TRAVEL_DATA
from core.config import settings
from langchain_openai import ChatOpenAI

class EnhancedTravelOrchestrator:
    def __init__(self):
        self.rag_system = TravelRAGSystem(settings["rag_config"], settings["chroma_path"], TRAVEL_DATA)
        self.rag_system.setup_vectorstore(force_rebuild=False)
        self.rag_tools = TravelRAGTools(self.rag_system)

        self.llm35 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.llm4 = ChatOpenAI(model="gpt-4o-mini", temperature=0.25)

        self.loc_agent = EnhancedLocationAgent(self.llm35, self.rag_tools)
        self.food_agent = EnhancedFoodAgent(self.llm35, self.rag_tools)
        self.itin_agent = EnhancedItineraryAgent(self.llm4, self.rag_tools)

    def detect_dest(self, q: str) -> str:
        ql = q.lower()
        if "sa pa" in ql or "sapa" in ql:
            return "sapa"
        if "hội an" in ql or "hoi an" in ql:
            return "hoi_an"
        if "hà nội" in ql or "ha noi" in ql:
            return "ha_noi"
        return "ha_noi"

    def get_destination_name(self, dest_key: str) -> str:
        return {"sapa": "Sa Pa", "hoi_an": "Hội An", "ha_noi": "Hà Nội"}.get(dest_key, "Hà Nội")

    def run(self, user_request: str) -> str:
        print("🚀 Bắt đầu xử lý với Enhanced RAG System...")

        dest_key = self.detect_dest(user_request)
        dest_name = self.get_destination_name(dest_key)

        print(f"📍 Đã nhận diện điểm đến: {dest_name}")

        print("🔍 Phase 1: Tìm kiếm địa điểm và ẩm thực...")
        t_loc = self.loc_agent.create_task(user_request, dest_name)
        t_food = self.food_agent.create_task(user_request, dest_name)

        crew1 = Crew(agents=[self.loc_agent.agent, self.food_agent.agent], 
                     tasks=[t_loc, t_food], 
                     process=Process.sequential)
        crew1_results = crew1.kickoff()
        print(f"Crew 1 kickoff results: {crew1_results}")

        loc_out = str(t_loc.output) if t_loc.output else "Không có dữ liệu."
        food_out = str(t_food.output) if t_food.output else "Không có dữ liệu."

        print("✅ Phase 1 hoàn thành!")
        print("\n--- Output từ Location Agent ---\n", loc_out)
        print("\n--- Output từ Food Agent ---\n", food_out)

        print("\n📅 Phase 2: Tạo lịch trình tích hợp...")

        t_itin = self.itin_agent.create_task(user_request, dest_name, loc_out, food_out)
        crew2 = Crew(agents=[self.itin_agent.agent], 
                     tasks=[t_itin], 
                     process=Process.sequential
        )
        crew2_results = crew2.kickoff()
        print(f"Crew 2 kickoff results: {crew2_results}")

        return (
            f"🎯 **KẾT QUẢ CHO: {dest_name.upper()}**\n\n"
            f"=== 🗺️ ĐỊA ĐIỂM ===\n{loc_out}\n\n"
            f"=== 🍜 ẨM THỰC ===\n{food_out}\n\n"
            f"=== 📅 LỊCH TRÌNH ===\n{str(t_itin.output)}"
        )