"""
Enhanced Food Agent - Specialist in food information retrieval using RAG
Only agent with permission to access RAG database for food information
"""
import os
import re
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from tools.rag_tools import TravelRAGTools
from core.config import settings


class EnhancedFoodAgent:
    """
    FoodAgent: Specializes in food recommendations using RAG system.
    Retrieves specified number of top-rated local dishes and restaurants.
    Constraint: Only this agent has permission to access RAG database for food.
    """
    
    def __init__(self, llm, rag_tools: TravelRAGTools):
        self.rag_tools = rag_tools
        self.agent = Agent(
            role="🍜 Chuyên Gia Ẩm Thực với RAG",
            goal="Là chuyên gia duy nhất có quyền truy cập cơ sở dữ liệu RAG về ẩm thực, tìm và gợi ý số lượng món đặc sản cụ thể theo yêu cầu, phù hợp với sở thích và ngân sách của khách.",
            backstory="Food blogger chuyên nghiệp với 10 năm kinh nghiệm, là người duy nhất được ủy quyền truy cập vào hệ thống RAG về ẩm thực Việt Nam. Có khả năng tìm kiếm chính xác và đề xuất món ăn phù hợp với khẩu vị, ngân sách và số lượng cụ thể theo yêu cầu.",
            llm=llm,
            allow_delegation=False,
            tools=[
                self.rag_tools.food_search,
                self.rag_tools.general_search
            ]
        )
    
    def create_task(self, request: str, destination: str, quantity: int = None) -> Task:
        """
        Create food recommendation task with specific quantity handling
        
        Args:
            request: User request describing food preferences
            destination: Target destination
            quantity: Specific number of food items needed (for itinerary planning)
        """
        
        # Extract quantity from request if not specified
        if quantity is None:
            quantity = self._extract_quantity_from_request(request)
        
        desc = f"""
            Yêu cầu của khách: "{request}"
            Điểm đến: {destination}
            Số lượng món ăn cần tìm: {quantity}

            Nhiệm vụ:
            1. **BẮT BUỘC: Sử dụng tool `food_search`** để tìm thông tin về các món ăn đặc sản tại {destination}.
               - Tìm kiếm với từ khóa phù hợp từ yêu cầu khách
               - Ưu tiên các món ăn đặc trưng và được đánh giá cao
            
            2. **Phân tích sở thích ẩm thực từ yêu cầu:**
               - Loại hình: truyền thống, đường phố, cao cấp, chay/mặn
               - Khẩu vị: cay, ngọt, chua, đậm đà, nhẹ nhàng
               - Ngân sách: bình dân, trung bình, cao cấp
               - Đặc biệt: món nổi tiếng, đặc sản địa phương, must-try
            
            3. **Chọn chính xác {quantity} món ăn phù hợp nhất** dựa trên:
               - Độ phù hợp với sở thích đã phân tích
               - Tính đại diện cho ẩm thực {destination}
               - Đa dạng về loại hình (nếu số lượng > 2)
               - Khả năng tiếp cận (có nhiều quán phục vụ)
            
            4. **Đối với mỗi món ăn, cung cấp thông tin:**
               - Tên món và mô tả hương vị chính
               - Gợi ý quán ăn nổi tiếng (nếu có trong RAG)
               - Khoảng giá cả ước tính
               - Thời điểm thích hợp (sáng/trưa/chiều/tối)
               - Lưu ý đặc biệt (ăn kèm, cách thưởng thức)
            
            5. **Sắp xếp theo độ ưu tiên:** Món đặc trưng nhất → món phổ biến → món thú vị
            
            Trả lời theo format:
            **{quantity} Món Ăn Đặc Sản {destination}:**
            
            1. **[Tên món]** - [Thời điểm phù hợp]
               - Hương vị: [Mô tả chi tiết]
               - Địa điểm: [Quán nổi tiếng/khu vực]
               - Giá cả: [Khoảng giá] 
               - Đặc biệt: [Lưu ý quan trọng]
            
            [Tiếp tục cho các món khác...]
            
            **💡 Gợi ý bổ sung:** [Lời khuyên về ẩm thực địa phương]

            Trả lời bằng tiếng Việt, chi tiết và hữu ích.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output=f"Danh sách {quantity} món đặc sản {destination} được đề xuất chi tiết với thông tin hương vị, địa điểm, giá cả và lời khuyên thưởng thức."
        )
    
    def _extract_quantity_from_request(self, request: str) -> int:
        """Extract quantity from request, default to 2 if not specified"""
        
        # Look for numbers in request
        numbers = re.findall(r'\d+', request)
        if numbers:
            # Use the first reasonable number found
            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= 20:  # Reasonable range for food items
                    return num
        
        # Default quantity based on request type
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['nhiều', 'đa dạng', 'khác nhau']):
            return 5
        elif any(word in request_lower for word in ['ít', 'vài', 'một số']):
            return 3
        else:
            return 2  # Default for most requests
    
    def create_simple_task(self, request: str, dest_name: str) -> Task:
        """Backward compatibility method for simple requests"""
        return self.create_task(request, dest_name, quantity=2)