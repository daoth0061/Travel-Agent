from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# ===== RAG SYSTEM =====
class TravelRAGSystem:
    """RAG system for travel information retrieval"""

    def __init__(self, config: dict, chroma_path: str, travel_data: dict):
        self.config = config
        self.chroma_path = chroma_path
        self.travel_data = travel_data
        self.embeddings = OpenAIEmbeddings(model=config['embedding_model'],
                                           api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config['chunk_size'],
            chunk_overlap=config['chunk_overlap'],
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.vectorstore = None

    def setup_vectorstore(self, force_rebuild: bool = False):
        """Setup or load vector store"""
        if force_rebuild or not os.path.exists(self.chroma_path):
            print("🔄 Building vector database...")
            documents = self._prepare_documents()
            chunks = self.text_splitter.split_documents(documents)

            # Ensure directory exists
            os.makedirs(self.chroma_path, exist_ok=True)

            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.chroma_path
            )
            print(f"✅ Vector database created with {len(chunks)} chunks")
        else:
            print("📂 Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings
            )
            print("✅ Vector database loaded successfully")

    def _prepare_documents(self) -> List[Document]:
        """Convert travel data to documents"""
        documents = []

        for dest_key, dest_data in self.travel_data.items():
            # Main destination document
            main_content = f"""
Điểm đến: {dest_data['name']}
Mô tả: {dest_data['description']}
Mã định danh: {dest_key}
"""
            documents.append(Document(
                page_content=main_content,
                metadata={
                    "destination": dest_data['name'],
                    "type": "overview",
                    "dest_key": dest_key
                }
            ))

            # Location documents
            for location in dest_data['locations']:
                documents.append(Document(
                    page_content=f"Địa điểm tại {dest_data['name']}: {location}",
                    metadata={
                        "destination": dest_data['name'],
                        "type": "location",
                        "dest_key": dest_key
                    }
                ))

            # Food documents
            for food in dest_data['food']:
                documents.append(Document(
                    page_content=f"Món ăn tại {dest_data['name']}: {food}",
                    metadata={
                        "destination": dest_data['name'],
                        "type": "food",
                        "dest_key": dest_key
                    }
                ))

            # Tips documents
            if 'tips' in dest_data:
                for tip in dest_data['tips']:
                    documents.append(Document(
                        page_content=f"Lời khuyên cho {dest_data['name']}: {tip}",
                        metadata={
                            "destination": dest_data['name'],
                            "type": "tips",
                            "dest_key": dest_key
                        }
                    ))

        return documents

    def search_locations(self, query: str, destination: str = None) -> str:
        """Search for location information"""
        if not self.vectorstore:
            return "Vector store not initialized"

        search_query = f"địa điểm {destination} {query}" if destination else f"địa điểm {query}"

        # FIX: Construct the filter dictionary with '$and' for multiple conditions
        filter_conditions = [{"type": "location"}]
        if destination:
            filter_conditions.append({"destination": destination})

        filter_dict = {"$and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
        if not destination: # If no destination, filter only by type
            filter_dict = {"type": "location"} # No need for $and if only one condition

        docs = self.vectorstore.similarity_search(
            search_query,
            k=self.config['top_k'],
            filter=filter_dict
        )
        return "\n".join([doc.page_content for doc in docs])

    def search_food(self, query: str, destination: str = None) -> str:
        """Search for food information"""
        if not self.vectorstore:
            return "Vector store not initialized"

        search_query = f"món ăn {destination} {query}" if destination else f"món ăn ẩm thực {query}"

        # FIX: Construct the filter dictionary with '$and' for multiple conditions
        filter_conditions = [{"type": "food"}]
        if destination:
            filter_conditions.append({"destination": destination})

        filter_dict = {"$and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
        if not destination: # If no destination, filter only by type
            filter_dict = {"type": "food"} # No need for $and if only one condition

        docs = self.vectorstore.similarity_search(
            search_query,
            k=self.config['top_k'],
            filter=filter_dict
        )
        return "\n".join([doc.page_content for doc in docs])

    def search_tips(self, query: str, destination: str = None) -> str:
        """Search for travel tips"""
        if not self.vectorstore:
            return "Vector store not initialized"

        search_query = f"lời khuyên {destination} {query}" if destination else f"lời khuyên {query}"

        # FIX: Construct the filter dictionary with '$and' for multiple conditions
        filter_conditions = [{"type": "tips"}]
        if destination:
            filter_conditions.append({"destination": destination})

        filter_dict = {"$and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
        if not destination: # If no destination, filter only by type
            filter_dict = {"type": "tips"} # No need for $and if only one condition

        docs = self.vectorstore.similarity_search(
            search_query,
            k=self.config['top_k'],
            filter=filter_dict
        )
        return "\n".join([doc.page_content for doc in docs])

    def search_general(self, query: str, destination: str = None) -> str:
        """General search across all content"""
        if not self.vectorstore:
            return "Vector store not initialized"

        # FIX: Construct the filter dictionary with '$and' for multiple conditions
        # General search doesn't filter by 'type', so only destination if present.
        filter_dict = None
        if destination:
            filter_dict = {"destination": destination}

        docs = self.vectorstore.similarity_search(
            query,
            k=self.config['top_k'],
            filter=filter_dict
        )
        return "\n".join([doc.page_content for doc in docs])