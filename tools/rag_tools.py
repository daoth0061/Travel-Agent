from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool
from tools.vector_store import TravelRAGSystem
from typing import Any

class LocationSearchInput(BaseModel):
    query: str = Field(..., description="Search query about locations")
    destination: str = Field("", description="Specific destination to search in (optional)")

class FoodSearchInput(BaseModel):
    query: str = Field(..., description="Search query about food/cuisine")
    destination: str = Field("", description="Specific destination to search in (optional)")

class TipsSearchInput(BaseModel):
    query: str = Field(..., description="Search query about travel tips")
    destination: str = Field("", description="Specific destination to search in (optional)")

class GeneralSearchInput(BaseModel):
    query: str = Field(..., description="General search query")
    destination: str = Field("", description="Specific destination for search (optional)")

# BaseTool subclasses now accept rag_system directly in __init__
# and store it as a regular attribute, not a Pydantic Field
class LocationSearchTool(BaseTool):
    name: str = "location_search"
    description: str = "Search for location information using RAG"
    args_schema: type[BaseModel] = LocationSearchInput

    # Pydantic v2 configuration to allow extra attributes (like rag_system)
    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data: Any):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_locations(query, destination if destination else None)

class FoodSearchTool(BaseTool):
    name: str = "food_search"
    description: str = "Search for food information using RAG"
    args_schema: type[BaseModel] = FoodSearchInput

    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data: Any):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_food(query, destination if destination else None)

class TipsSearchTool(BaseTool):
    name: str = "tips_search"
    description: str = "Search for travel tips using RAG"
    args_schema: type[BaseModel] = TipsSearchInput

    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data: Any):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_tips(query, destination if destination else None)

class GeneralSearchTool(BaseTool):
    name: str = "general_search"
    description: str = "General search across all travel content using RAG"
    args_schema: type[BaseModel] = GeneralSearchInput

    model_config = ConfigDict(extra='allow')

    def __init__(self, rag_system: TravelRAGSystem, **data: Any):
        super().__init__(**data)
        self.rag_system = rag_system

    def _run(self, query: str, destination: str = "") -> str:
        return self.rag_system.search_general(query, destination if destination else None)

class TravelRAGTools:
    def __init__(self, rag_system: TravelRAGSystem):
        self.rag_system = rag_system
        self.location_search = LocationSearchTool(rag_system=rag_system)
        self.food_search = FoodSearchTool(rag_system=rag_system)
        self.tips_search = TipsSearchTool(rag_system=rag_system)
        self.general_search = GeneralSearchTool(rag_system=rag_system)