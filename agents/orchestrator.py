from crewai import Crew, Process
from agents.location_agent import EnhancedLocationAgent
from agents.food_agent import EnhancedFoodAgent
from agents.itinerary_agent import EnhancedItineraryAgent
from tools.rag_tools import TravelRAGTools
from tools.vector_store import TravelRAGSystem
from data.travel_data import TRAVEL_DATA
from core.config import settings

class EnhancedTravelOrchestrator:
    def __init__(self):
        self.rag_system = TravelRAGSystem(settings["rag_config"], settings["chroma_db_path"], TRAVEL_DATA)
        self.rag_system.setup_vectorstore(force_rebuild=False)
        self.rag_tools = TravelRAGTools(self.rag_system)
        self.loc_agent = EnhancedLocationAgent(self.rag_tools)
        self.food_agent = EnhancedFoodAgent(self.rag_tools)
        self.itin_agent = EnhancedItineraryAgent(self.rag_tools)

    def detect_dest(self, q: str) -> str:
        ql = q.lower()
        for key, name in {"sapa": "Sa Pa", "hoi_an": "Hội An", "ha_noi": "Hà Nội"}.items():
            if key.replace("_", " ") in ql:
                return key
        return "ha_noi"

    def get_destination_name(self, dest_key: str) -> str:
        return {"sapa": "Sa Pa", "hoi_an": "Hội An", "ha_noi": "Hà Nội"}.get(dest_key, "Hà Nội")

    def run(self, user_request: str) -> str:
        dest_key = self.detect_dest(user_request)
        dest_name = self.get_destination_name(dest_key)

        t_loc = self.loc_agent.create_task(user_request, dest_name)
        t_food = self.food_agent.create_task(user_request, dest_name)
        crew1 = Crew(agents=[self.loc_agent.agent, self.food_agent.agent], tasks=[t_loc, t_food], process=Process.sequential)
        crew1.kickoff()

        loc_out = str(t_loc.output) if t_loc.output else "Không có dữ liệu."
        food_out = str(t_food.output) if t_food.output else "Không có dữ liệu."

        t_itin = self.itin_agent.create_task(user_request, dest_name, loc_out, food_out)
        crew2 = Crew(agents=[self.itin_agent.agent], tasks=[t_itin], process=Process.sequential)
        crew2.kickoff()

        return (
            f"🎯 **KẾT QUẢ CHO: {dest_name.upper()}**\n\n"
            f"=== 🗺️ ĐỊA ĐIỂM ===\n{loc_out}\n\n"
            f"=== 🍜 ẨM THỰC ===\n{food_out}\n\n"
            f"=== 📅 LỊCH TRÌNH ===\n{str(t_itin.output)}"
        )