"""
Default Agent for handling general questions and queries outside other categories
"""
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Any


class DefaultAgent:
    """
    Fallback agent to handle general questions or queries that don't fit other categories
    (e.g., "What is the currency in Vietnam?", "What's the weather like?", etc.)
    """
    
    def __init__(self, llm):
        self.agent = Agent(
            role="🤖 Chuyên Viên Tư Vấn Du Lịch Tổng Quát",
            goal="Trả lời các câu hỏi chung về du lịch Việt Nam, thông tin văn hóa, tiền tệ, giao thông và các vấn đề không thuộc về ẩm thực, địa điểm cụ thể hay lịch trình.",
            backstory="Chuyên viên tư vấn du lịch với kiến thức sâu rộng về Việt Nam, có khả năng trả lời mọi câu hỏi chung về văn hóa, phong tục, tiền tệ, giao thông, thời tiết, visa và các thông tin hữu ích khác cho du khách.",
            llm=llm,
            allow_delegation=False,
            tools=[]  # No specific tools needed, relies on LLM knowledge
        )
    
    def create_task(self, request: str, context: dict = None) -> Task:
        """Create task for handling general queries"""
        
        context_info = ""
        if context and context.get("current_context", {}).get("current_destination"):
            destination = context["current_context"]["current_destination"]
            context_info = f"\nThông tin bối cảnh: Người dùng đang quan tâm đến {destination}."
        
        desc = f"""
            Câu hỏi của khách: "{request}"{context_info}

            Nhiệm vụ:
            1. Phân tích câu hỏi để xác định loại thông tin khách cần.
            2. Cung cấp thông tin chính xác, hữu ích và thực tế về:
               - Tiền tệ và tỷ giá hối đoái
               - Visa và thủ tục nhập cảnh
               - Giao thông công cộng và di chuyển
               - Văn hóa và phong tục
               - Thời tiết theo mùa
               - Ngôn ngữ và giao tiếp
               - Mẹo và lưu ý an toàn
               - Thông tin chung khác về Việt Nam
            3. Nếu câu hỏi liên quan đến địa điểm cụ thể, hãy đưa ra lời khuyên chung phù hợp.
            4. Đưa ra các gợi ý bổ sung hoặc thông tin liên quan có thể hữu ích.
            5. Nếu câu hỏi quá cụ thể và cần chuyên gia khác, hãy đề xuất người dùng hỏi cụ thể hơn.

            Trả lời bằng tiếng Việt, thân thiện và dễ hiểu.
        """
        
        return Task(
            description=desc,
            agent=self.agent,
            expected_output="Thông tin hữu ích và chính xác trả lời câu hỏi của khách, kèm theo các gợi ý bổ sung nếu phù hợp."
        )
    
    def handle_currency_question(self) -> str:
        """Handle currency-related questions"""
        return """
💰 **Tiền tệ Việt Nam:**
- Đơn vị: Đồng Việt Nam (VND)
- Ký hiệu: ₫ hoặc VND
- Mệnh giá: 10,000₫, 20,000₫, 50,000₫, 100,000₫, 200,000₫, 500,000₫
- Tỷ giá: ~23,000-25,000 VND = 1 USD (thay đổi)
- Đổi tiền: Ngân hàng, tiệm vàng, sân bay
- Thẻ ATM: Được chấp nhận rộng rãi ở thành phố lớn
"""
    
    def handle_visa_question(self) -> str:
        """Handle visa-related questions"""
        return """
📋 **Visa Việt Nam:**
- **Miễn visa 45 ngày:** 13 quốc gia (Đức, Pháp, Anh, Ý, Tây Ban Nha...)
- **Miễn visa 30 ngày:** ASEAN, Nhật Bản, Hàn Quốc, Nga...
- **E-visa:** Đăng ký online, 30 ngày, 1 lần nhập cảnh
- **Visa du lịch:** 30 ngày, có thể gia hạn
- **Yêu cầu:** Hộ chiếu còn 6 tháng, vé máy bay khứ hồi
- **Website chính thức:** evisa.xuatnhapcanh.gov.vn
"""
    
    def handle_transportation_question(self) -> str:
        """Handle transportation questions"""
        return """
🚗 **Giao thông Việt Nam:**
- **Máy bay:** Nội địa giá rẻ (VietJet, Bamboo Airways)
- **Tàu hỏa:** Bắc-Nam, cabin giường nằm, cảnh đẹp
- **Xe khách:** Giường nằm, rẻ nhất, nhiều tuyến
- **Grab/Gojek:** Xe ôm, taxi, delivery ở thành phố
- **Xe máy:** Thuê 150,000-300,000₫/ngày
- **Ô tô:** Cần bằng lái quốc tế
- **Xe bus:** Rẻ nhưng chậm, phù hợp ngân sách thấp
"""
    
    def handle_weather_question(self) -> str:
        """Handle general weather questions"""
        return """
🌤️ **Thời tiết Việt Nam:**
- **Miền Bắc:** 4 mùa rõ rệt
  - Xuân (3-4): Ấm áp, mưa phùn
  - Hè (5-8): Nóng ẩm, mưa lớn
  - Thu (9-11): Mát mẻ, đẹp nhất
  - Đông (12-2): Lạnh, khô
- **Miền Trung:** 2 mùa
  - Khô (1-8): Nắng nóng
  - Mưa (9-12): Mưa bão nhiều
- **Miền Nam:** Nhiệt đới
  - Khô (11-4): Ít mưa, mát
  - Mưa (5-10): Mưa chiều, nóng ẩm
"""
