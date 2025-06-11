"""
Enhanced Location Agent - Specialist in location information retrieval using RAG
Only agent with permission to access RAG database for location information
"""
import re
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings
import os


class LocationAgent:
    """
    LocationAgent: Specializes in sightseeing recommendations using RAG system.
    Retrieves specified number of top-rated attractions and points of interest.
    Constraint: Only this agent has permission to access RAG database for locations.
    """
    
    def __init__(self, llm, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🗺️ Chuyên Gia Địa Điểm với RAG",
            goal="Là chuyên gia duy nhất có quyền truy cập cơ sở dữ liệu RAG về địa điểm du lịch, tìm và đề xuất số lượng điểm tham quan cụ thể phù hợp nhất với sở thích và thời gian của khách.",
            backstory="Chuyên gia du lịch 15 năm kinh nghiệm, là người duy nhất được ủy quyền truy cập vào hệ thống RAG về địa điểm du lịch Việt Nam. Có khả năng phân tích sở thích du khách và đề xuất các điểm đến được tối ưu hóa về thời gian và logic di chuyển.",
            llm=llm,
            allow_delegation=False,
            tools=[
                self.rag_tools.location_search,
                self.rag_tools.general_search
            ]
        )

    def create_task(self, request: str, destination: str, quantity: int = None) -> Task:
        """
        Create location recommendation task with specific quantity handling
        
        Args:
            request: User request describing location preferences
            destination: Target destination
            quantity: Specific number of location items needed (for itinerary planning)
        """
        
        # Extract quantity from request if not specified
        if quantity is None:
            quantity = self._extract_quantity_from_request(request)
        
        desc = f"""
            Yêu cầu của khách: "{request}"
            Điểm đến: {destination}
            Số lượng địa điểm cần tìm: {quantity}

            Nhiệm vụ:
            1. **BẮT BUỘC: Sử dụng tool `location_search`** để tìm thông tin về các địa điểm tại {destination}.
               - Tìm kiếm với từ khóa phù hợp từ yêu cầu khách
               - Ưu tiên các địa điểm nổi tiếng và được đánh giá cao
            
            2. **Phân tích sở thích du lịch từ yêu cầu:**
               - Loại hình: lịch sử/văn hóa, thiên nhiên, thư giãn, phiêu lưu, tâm linh
               - Độ tuổi/thể lực: phù hợp mọi lứa tuổi, cần thể lực, dễ tiếp cận
               - Thời gian: nửa ngày, cả ngày, vài giờ
               - Phong cách: độc lập, guided tour, chụp ảnh, trải nghiệm
            
            3. **Chọn chính xác {quantity} địa điểm phù hợp nhất** dựa trên:
               - Độ phù hợp với sở thích đã phân tích
               - Tính đại diện cho {destination}
               - Logic di chuyển (gần nhau hoặc cùng tuyến)
               - Đa dạng trải nghiệm (nếu số lượng > 2)
               - Tính khả thi về thời gian
            
            4. **Đối với mỗi địa điểm, cung cấp thông tin:**
               - Tên và mô tả ngắn gọn
               - Lý do phù hợp với yêu cầu khách
               - Thời gian tham quan ước tính
               - Khung giờ lý tưởng (sáng/chiều/tối)
               - Mức độ khó tiếp cận và phí tham quan
               - Mẹo tham quan và điều cần lưu ý
            
            5. **Sắp xếp theo độ ưu tiên:** Must-see → highly recommended → interesting options
            
            6. **Tối ưu hóa logic di chuyển:** Nhóm các địa điểm gần nhau và đề xuất thứ tự tham quan hợp lý.
            
            Trả lời theo format:
            **{quantity} Địa Điểm Tham Quan {destination}:**
            
            1. **[Tên địa điểm]** - [Khung giờ lý tưởng]
               - Mô tả: [Ngắn gọn về điểm đặc biệt]
               - Phù hợp vì: [Lý do match với yêu cầu]
               - Thời gian: [X giờ tham quan]
               - Phí: [Miễn phí/X VND]
               - Lưu ý: [Mẹo quan trọng]
            
            [Tiếp tục cho các địa điểm khác...]
            
            **🗺️ Đề xuất tuyến di chuyển:** [Thứ tự tối ưu]
            **💡 Mẹo bổ sung:** [Lời khuyên chung về tham quan {destination}]

            Trả lời bằng tiếng Việt, chi tiết và thực tế.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Danh sách {quantity} địa điểm tham quan {destination} được đề xuất chi tiết với thông tin thời gian, lý do phù hợp và tối ưu hóa di chuyển."
        )
    
    def _extract_quantity_from_request(self, request: str) -> int:
        """Extract quantity from request, default to 3 if not specified"""
        
        # Look for numbers in request
        numbers = re.findall(r'\d+', request)
        if numbers:
            # Use the first reasonable number found
            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= 20:  # Reasonable range for locations
                    return num
        
        # Default quantity based on request type
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['nhiều', 'đa dạng', 'khác nhau', 'đầy đủ']):
            return 5
        elif any(word in request_lower for word in ['ít', 'vài', 'một số', 'chính']):
            return 2
        else:
            return 3  # Default for most location requests
    
    def create_simple_task(self, request: str, dest_name: str) -> Task:
        """Backward compatibility method for simple requests"""
        return self.create_task(request, dest_name, quantity=3)