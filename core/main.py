import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.orchestrator import EnhancedTravelOrchestrator

def main():
    orchestrator = EnhancedTravelOrchestrator()
    # user_query = "Tôi muốn đi du lịch Hà Nội 3 ngày, muốn khám phá văn hóa lịch sử và thử các món ăn truyền thống."
    user_query = "Tôi muốn đi Sa Pa 2 ngày, thích trekking và cảnh đẹp núi rừng, muốn thử các món ăn đặc sản vùng cao."
    # user_query = "Tôi muốn đi Hội An 4 ngày, muốn đi dạo phố cổ và chụp ảnh đèn lồng, muốn tìm các quán ăn ngon."
    final_report = orchestrator.run(user_query)
    print("\n\n" + "="*50)
    print("🌟 BÁO CÁO DU LỊCH HOÀN CHỈNH 🌟")
    print("="*50 + "\n")
    print(final_report)

if __name__ == "__main__":
    main()