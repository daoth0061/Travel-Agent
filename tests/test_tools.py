import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.vector_store import TravelRAGSystem
from tools.rag_tools import TravelRAGTools
from data.travel_data import TRAVEL_DATA
from core.config import settings


def main():
    """Main function to setup and test the RAG system"""

    # Paths
    CHROMA_DB_PATH = settings["chroma_path"]

    # Initialize RAG system
    config = settings["rag_config"]
    rag_system = TravelRAGSystem(config, CHROMA_DB_PATH, TRAVEL_DATA)

    # Setup vector store (force rebuild for demo)
    rag_system.setup_vectorstore(force_rebuild=True)

    # Initialize tools
    tools = TravelRAGTools(rag_system)

    # Test the system
    print("\n🧪 Testing RAG System:")
    print("=" * 50)

    # Test location search
    print("\n🏛️ Location Search Test:")
    result = tools.location_search._run("Hồ Gươm", "Hà Nội") # Added explicit destination for better filtering
    print(result)

    # Test food search
    print("\n🍜 Food Search Test:")
    result = tools.food_search._run("phở", "Hà Nội")
    print(result)

    # Test tips search
    print("\n💡 Tips Search Test:")
    result = tools.tips_search._run("thời tiết", "Sa Pa")
    print(result)

    # Test general search
    print("\n🔍 General Search Test:")
    result = tools.general_search._run("Hội An đèn lồng", "Hội An") # Added explicit destination for better filtering
    print(result)

    print("\n✅ RAG System setup and testing completed!")
    return rag_system, tools

if __name__ == "__main__":
    rag_system, tools = main()