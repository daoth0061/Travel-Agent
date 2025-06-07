from dataclasses import dataclass
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

@dataclass
class RAGConfig:
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

class TravelRAGSystem:
    def __init__(self, config: RAGConfig, persist_dir: str, travel_data: dict):
        self.config = config
        self.persist_dir = persist_dir
        self.travel_data = travel_data
        self.vectorstore = None

    def setup_vectorstore(self, force_rebuild: bool = False):
        if force_rebuild or not self.vectorstore:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
            )
            docs = []
            for dest_key, data in self.travel_data.items():
                for loc in data["locations"]:
                    docs.append(Document(page_content=loc, metadata={"type": "location", "destination": data["name"]}))
                for food in data["food"]:
                    docs.append(Document(page_content=food, metadata={"type": "food", "destination": data["name"]}))
            chunks = splitter.split_documents(docs)
            self.vectorstore = Chroma.from_documents(
                documents=chunks, 
                embedding=OpenAIEmbeddings(), 
                persist_directory=self.persist_dir
            )

    def search_locations(self, query: str, destination: str | None) -> str:
        filter_dict = {"type": "location"}
        if destination:
            filter_dict["destination"] = destination
        docs = self.vectorstore.similarity_search(query, k=self.config.top_k, filter=filter_dict)
        return "\n".join([doc.page_content for doc in docs])

    def search_food(self, query: str, destination: str | None) -> str:
        filter_dict = {"type": "food"}
        if destination:
            filter_dict["destination"] = destination
        docs = self.vectorstore.similarity_search(query, k=self.config.top_k, filter=filter_dict)
        return "\n".join([doc.page_content for doc in docs])

    def search_general(self, query: str, destination: str | None) -> str:
        filter_dict = None if not destination else {"destination": destination}
        docs = self.vectorstore.similarity_search(query, k=self.config.top_k, filter=filter_dict)
        return "\n".join([doc.page_content for doc in docs])   