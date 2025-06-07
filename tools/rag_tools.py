from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool
from tools.vector_store import TravelRAGSystem

class LocationSearchInput(BaseModel):
    query: str = Field(..., description="Search query about locations")
    destination: str = Field("", description="Specific destination (optional)")

class FoodSearchInput(BaseModel):
    query: str = Field(..., description="Search query about food")
    destination: str = Field("", description="Specific destination (optional)")

class GeneralSearchInput(BaseModel):
    query: str = Field(..., description="General search query")
    destination: str = Field("", description="Specific destination (optional)")

class LocationSearchTool(BaseTool):
    name: str = "location_search"
    description: str = "Search for location information using RAG"
    args_schema = LocationSearchInput
    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_locations(query, destination or None)

class FoodSearchTool(BaseTool):
    name: str = "food_search"
    description: str = "Search for food information using RAG"
    args_schema = FoodSearchInput
    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_food(query, destination or None)

class GeneralSearchTool(BaseTool):
    name: str = "general_search"
    description: str = "General search across travel content using RAG"
    args_schema = GeneralSearchInput
    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_general(query, destination or None)

class TravelRAGTools:
    def __init__(self, rag_system: TravelRAGSystem):
        self.location_search = LocationSearchTool(rag_system=rag_system)
        self.food_search = FoodSearchTool(rag_system=rag_system)
        self.general_search = GeneralSearchTool(rag_system=rag_system)