from core.utils import classify_intent
from typing import Dict, List, Tuple
import json
from datetime import datetime

def evaluate_intent_classification():
    """
    Detailed evaluation of the intent classification system with:
    - Accuracy per intent
    - Confusion matrix
    - Detailed error analysis
    """
    # Extended test cases
    test_cases = [
        # Food related queries (50)
        ("Món ăn ngon ở Hà Nội có gì?", "eat"),
        ("Quán phở ngon nhất Sài Gòn", "eat"),
        ("Địa chỉ bánh mì ngon", "eat"),
        ("Nhà hàng hải sản Đà Nẵng", "eat"),
        ("Quán ăn ngon rẻ ở Huế", "eat"),
        ("Đặc sản Hội An", "eat"),
        ("Quán bún chả ngon", "eat"),
        ("Nhà hàng buffet hải sản", "eat"),
        ("Món ngon ở chợ Bến Thành", "eat"),
        ("Quán cơm tấm sạch sẽ", "eat"),
        ("Tiệm bánh ngọt nổi tiếng", "eat"),
        ("Quán ốc ngon ở Sài Gòn", "eat"),
        ("Nhà hàng view đẹp ở Đà Lạt", "eat"),
        ("Quán cafe có đồ ăn ngon", "eat"),
        ("Địa chỉ ăn vặt ngon", "eat"),
        ("Nhà hàng chay nổi tiếng", "eat"),
        ("Quán lẩu ngon rẻ", "eat"),
        ("Địa điểm ăn đêm", "eat"),
        ("Nhà hàng BBQ ngon", "eat"),
        ("Quán bún bò Huế authenthic", "eat"),
        ("Tiệm bánh mì nổi tiếng nhất", "eat"),
        ("Quán ăn view biển", "eat"),
        ("Nhà hàng món Bắc ngon", "eat"),
        ("Quán ăn gia đình", "eat"),
        ("Địa điểm ăn sáng ngon", "eat"),
        ("Nhà hàng có phòng riêng", "eat"),
        ("Quán nhậu ngon", "eat"),
        ("Tiệm dimsum authentic", "eat"),
        ("Quán cháo sườn ngon", "eat"),
        ("Nhà hàng có live music", "eat"),
        ("Quán ăn đường phố nổi tiếng", "eat"),
        ("Địa chỉ bánh xèo ngon", "eat"),
        ("Nhà hàng Nhật authentic", "eat"),
        ("Quán ăn cho nhóm đông", "eat"),
        ("Tiệm cà phê có bánh ngọt", "eat"),
        ("Quán ăn view phố cổ", "eat"),
        ("Nhà hàng Hàn Quốc ngon", "eat"),
        ("Quán bún đậu mắm tôm", "eat"),
        ("Địa điểm ăn trưa văn phòng", "eat"),
        ("Nhà hàng hải sản tự chọn", "eat"),
        ("Quán ăn có chỗ đậu xe", "eat"),
        ("Tiệm pizza ngon", "eat"),
        ("Quán ăn mở cả ngày", "eat"),
        ("Nhà hàng có set menu", "eat"),
        ("Quán ăn ship đêm", "eat"),
        ("Địa chỉ gỏi cuốn ngon", "eat"),
        ("Nhà hàng buffet trưa", "eat"),
        ("Quán bia craft", "eat"),
        ("Tiệm trà sữa ngon", "eat"),
        
        # Visit related queries (50)
        ("Chỗ nào đẹp ở Sa Pa để tham quan?", "visit"),
        ("Địa điểm du lịch Hội An", "visit"),
        ("Bảo tàng ở Hà Nội", "visit"),
        ("Công viên đẹp ở Đà Lạt", "visit"),
        ("Điểm tham quan ở Huế", "visit"),
        ("Chùa đẹp ở Hà Nội", "visit"),
        ("Địa điểm check-in Sài Gòn", "visit"),
        ("Thác nước đẹp ở Đà Lạt", "visit"),
        ("Làng nghề truyền thống", "visit"),
        ("Điểm ngắm hoàng hôn đẹp", "visit"),
        ("Bãi biển đẹp Phú Quốc", "visit"),
        ("Di tích lịch sử ở Huế", "visit"),
        ("Vườn hoa đẹp ở Đà Lạt", "visit"),
        ("Điểm săn mây ở Tam Đảo", "visit"),
        ("Chợ đêm ở Nha Trang", "visit"),
        ("Điểm cắm trại đẹp", "visit"),
        ("Hang động ở Quảng Bình", "visit"),
        ("Điểm picnic cuối tuần", "visit"),
        ("Đảo đẹp ở Hạ Long", "visit"),
        ("Thác nước ở Tây Nguyên", "visit"),
        ("Điểm ngắm tuyết ở Sa Pa", "visit"),
        ("Làng cổ ở Hội An", "visit"),
        ("Điểm săn ảnh đẹp", "visit"),
        ("Núi đẹp để leo", "visit"),
        ("Bãi tắm hoang sơ", "visit"),
        ("Điểm du lịch sinh thái", "visit"),
        ("Khu bảo tồn thiên nhiên", "visit"),
        ("Điểm ngắm cảnh đẹp", "visit"),
        ("Chợ nổi miền Tây", "visit"),
        ("Điểm trekking đẹp", "visit"),
        ("Công viên giải trí", "visit"),
        ("Điểm ngắm pháo hoa", "visit"),
        ("Làng bích họa đẹp", "visit"),
        ("Điểm ngắm hoa dã quỳ", "visit"),
        ("Vườn quốc gia đẹp", "visit"),
        ("Điểm ngắm hoa tam giác mạch", "visit"),
        ("Làng hoa đẹp", "visit"),
        ("Điểm ngắm thành phố về đêm", "visit"),
        ("Khu phố cổ", "visit"),
        ("Điểm trải nghiệm văn hóa", "visit"),
        ("Đồi chè đẹp", "visit"),
        ("Điểm ngắm bình minh", "visit"),
        ("Làng rượu vang Đà Lạt", "visit"),
        ("Điểm xem concert ngoài trời", "visit"),
        ("Khu du lịch sinh thái", "visit"),
        ("Điểm chụp ảnh cưới đẹp", "visit"),
        ("Làng gốm truyền thống", "visit"),
        ("Điểm ngắm sao đêm", "visit"),
        ("Công viên nước", "visit"),
        ("Điểm trượt tuyết", "visit"),

        # Plan related queries (50)
        ("Lập lịch đi Hội An 3 ngày", "plan"),
        ("Kế hoạch du lịch Hạ Long", "plan"),
        ("Tour Phú Quốc 4 ngày 3 đêm", "plan"),
        ("Lịch trình đi Nha Trang", "plan"),
        ("Kế hoạch đi Đà Lạt 2 ngày", "plan"),
        ("Tour du lịch Sapa", "plan"),
        ("Lịch trình phượt Tây Bắc", "plan"),
        ("Kế hoạch đi biển Vũng Tàu", "plan"),
        ("Tour khám phá Tây Nguyên", "plan"),
        ("Lập kế hoạch đi Huế-Đà Nẵng-Hội An", "plan"),
        ("Lịch trình đi Mộc Châu", "plan"),
        ("Tour xuyên Việt", "plan"),
        ("Kế hoạch du lịch Côn Đảo", "plan"),
        ("Lịch trình khám phá miền Tây", "plan"),
        ("Tour du lịch đảo Lý Sơn", "plan"),
        ("Kế hoạch đi Ninh Bình", "plan"),
        ("Lịch trình leo Fansipan", "plan"),
        ("Tour du lịch Cần Giờ", "plan"),
        ("Kế hoạch đi Phong Nha", "plan"),
        ("Lịch trình khám phá Tràng An", "plan"),
        ("Tour thăm quan chợ nổi", "plan"),
        ("Kế hoạch đi Mù Cang Chải", "plan"),
        ("Lịch trình phượt Hà Giang", "plan"),
        ("Tour du lịch Cát Bà", "plan"),
        ("Kế hoạch đi Đảo Phú Quý", "plan"),
        ("Lịch trình thăm làng nghề", "plan"),
        ("Tour khám phá hang động", "plan"),
        ("Kế hoạch đi Bà Nà Hills", "plan"),
        ("Lịch trình du lịch Tam Đảo", "plan"),
        ("Tour tham quan đền chùa", "plan"),
        ("Kế hoạch đi Măng Đen", "plan"),
        ("Lịch trình khám phá Đà Lạt", "plan"),
        ("Tour du lịch biển đảo", "plan"),
        ("Kế hoạch đi Nam Du", "plan"),
        ("Lịch trình thăm vườn quốc gia", "plan"),
        ("Tour leo núi Bà Đen", "plan"),
        ("Kế hoạch đi Mai Châu", "plan"),
        ("Lịch trình khám phá Quy Nhơn", "plan"),
        ("Tour du lịch Côn Sơn", "plan"),
        ("Kế hoạch đi Đảo Bình Ba", "plan"),
        ("Lịch trình thăm làng cổ", "plan"),
        ("Tour khám phá rừng nguyên sinh", "plan"),
        ("Kế hoạch đi Đảo Bình Hưng", "plan"),
        ("Lịch trình du lịch Phan Thiết", "plan"),
        ("Tour tham quan di tích", "plan"),
        ("Kế hoạch đi Pleiku", "plan"),
        ("Lịch trình khám phá Buôn Ma Thuột", "plan"),
        ("Tour du lịch sinh thái", "plan"),
        ("Kế hoạch đi Đảo Cù Lao Chàm", "plan"),
        ("Lịch trình thăm quan thác nước", "plan"),

        # Booking related queries (50)
        ("Tìm khách sạn tốt ở Đà Nẵng", "book"),
        ("Đặt phòng resort Phú Quốc", "book"),
        ("Homestay giá rẻ Đà Lạt", "book"),
        ("Book khách sạn 5 sao Sài Gòn", "book"),
        ("Đặt villa ở Nha Trang", "book"),
        ("Tìm homestay view đẹp", "book"),
        ("Book resort ven biển", "book"),
        ("Đặt khách sạn trung tâm", "book"),
        ("Tìm nơi ở giá rẻ", "book"),
        ("Đặt phòng view biển", "book"),
        ("Book homestay cho nhóm", "book"),
        ("Đặt villa có hồ bơi", "book"),
        ("Tìm khách sạn có gym", "book"),
        ("Đặt resort all-inclusive", "book"),
        ("Book phòng đôi khách sạn", "book"),
        ("Đặt homestay gần chợ", "book"),
        ("Tìm resort có spa", "book"),
        ("Book villa cho gia đình", "book"),
        ("Đặt khách sạn có buffet sáng", "book"),
        ("Tìm nơi ở có đưa đón sân bay", "book"),
        ("Đặt phòng view núi", "book"),
        ("Book resort có bãi biển riêng", "book"),
        ("Đặt villa gần trung tâm", "book"),
        ("Tìm khách sạn thân thiện môi trường", "book"),
        ("Đặt homestay phong cách vintage", "book"),
        ("Book resort có kids club", "book"),
        ("Đặt khách sạn có hồ bơi", "book"),
        ("Tìm nơi ở có bếp riêng", "book"),
        ("Đặt phòng suite", "book"),
        ("Book villa view thác", "book"),
        ("Đặt homestay kiểu Nhật", "book"),
        ("Tìm resort có golf", "book"),
        ("Book khách sạn boutique", "book"),
        ("Đặt villa BBQ", "book"),
        ("Tìm nơi ở có phòng họp", "book"),
        ("Đặt resort trên đồi", "book"),
        ("Book homestay có vườn", "book"),
        ("Đặt khách sạn pet-friendly", "book"),
        ("Tìm nơi ở có lò sưởi", "book"),
        ("Đặt phòng connecting", "book"),
        ("Book resort có tennis", "book"),
        ("Đặt villa có bếp BBQ", "book"),
        ("Tìm khách sạn có xe đạp", "book"),
        ("Đặt homestay gần biển", "book"),
        ("Book resort có casino", "book"),
        ("Đặt khách sạn có bar", "book"),
        ("Tìm nơi ở có karaoke", "book"),
        ("Đặt villa có quản gia", "book"),
        ("Book homestay có máy giặt", "book"),

        # Other queries (50)
        ("Tiền tệ Việt Nam là gì?", "other"),
        ("Thời tiết Hà Nội thế nào?", "other"),
        ("Cần mang những gì khi đi du lịch?", "other"),
        ("Visa du lịch Việt Nam", "other"),
        ("Nhiệt độ Đà Lạt hôm nay", "other"),
        ("Cách đổi tiền ở sân bay", "other"),
        ("Thủ tục check in máy bay", "other"),
        ("Mùa nào đẹp nhất để du lịch", "other"),
        ("Cần chuẩn bị gì khi đi biển", "other"),
        ("Thời tiết miền Bắc", "other"),
        ("Các món đồ cần mang theo", "other"),
        ("Điện áp ổ cắm Việt Nam", "other"),
        ("Cách di chuyển từ sân bay", "other"),
        ("Mùa mưa ở miền Nam", "other"),
        ("Thủ tục xuất nhập cảnh", "other"),
        ("Cách thuê xe máy", "other"),
        ("Thời gian bay giữa các thành phố", "other"),
        ("Quy định hành lý xách tay", "other"),
        ("Thời tiết Sapa tháng 12", "other"),
        ("Cách gọi taxi ở Việt Nam", "other"),
        ("Thủ tục hoàn thuế", "other"),
        ("Cần tiêm những mũi vaccine nào", "other"),
        ("Thời gian check in khách sạn", "other"),
        ("Cách mua sim điện thoại", "other"),
        ("Nhiệt độ trung bình các tháng", "other"),
        ("Thủ tục thuê xe ô tô", "other"),
        ("Cách đặt vé tàu", "other"),
        ("Thời tiết mùa đông miền Bắc", "other"),
        ("Quy định chụp ảnh ở di tích", "other"),
        ("Cách gửi đồ về nước", "other"),
        ("Thủ tục định cư", "other"),
        ("Cần mua bảo hiểm gì", "other"),
        ("Thời gian mở cửa bảo tàng", "other"),
        ("Cách đổi bằng lái xe", "other"),
        ("Nhiệt độ nước biển các mùa", "other"),
        ("Thủ tục khai báo y tế", "other"),
        ("Cách mua vé tham quan", "other"),
        ("Thời tiết mùa lễ hội", "other"),
        ("Quy định cách ly Covid", "other"),
        ("Cách đăng ký sim du lịch", "other"),
        ("Thủ tục xin visa", "other"),
        ("Cần đổi bao nhiêu tiền", "other"),
        ("Thời gian bay quốc tế", "other"),
        ("Cách book vé máy bay", "other"),
        ("Nhiệt độ trong hang động", "other"),
        ("Thủ tục nhập cảnh", "other"),
        ("Cách thanh toán ở Việt Nam", "other"),
        ("Thời tiết các mùa trong năm", "other"),
        ("Quy định phòng dịch", "other"),
        ("Cách liên hệ cấp cứu", "other")
    ]

    # Initialize metrics
    intents = ["eat", "visit", "plan", "book", "other", "weather"]
    confusion_matrix = {
        intent: {pred: 0 for pred in intents}
        for intent in intents
    }
    correct_counts = {intent: 0 for intent in intents}
    total_counts = {intent: 0 for intent in intents}

    # Run evaluation
    print("🧪 INTENT CLASSIFICATION EVALUATION")
    print("=" * 50)
    
    for query, expected in test_cases:
        predicted = classify_intent(query)
        
        # Update metrics
        total_counts[expected] += 1
        confusion_matrix[expected][predicted] += 1
        
        if predicted == expected:
            correct_counts[predicted] += 1
        # Print result
        status = "✅" if predicted == expected else "❌"
        print(f"{status} '{query}' → {predicted} (expected: {expected})")

    # Calculate and display results
    print("\n📊 Overall Results:")
    total_correct = sum(correct_counts.values())
    total = sum(total_counts.values())
    print(f"Total Accuracy: {total_correct}/{total} ({(total_correct/total*100):.1f}%)")
    
    print("\n📊 Per-Intent Accuracy:")
    for intent in intents:
        if total_counts[intent] > 0:
            accuracy = correct_counts[intent] / total_counts[intent] * 100
            print(f"{intent:6s}: {correct_counts[intent]}/{total_counts[intent]} ({accuracy:.1f}%)")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_accuracy": total_correct/total,
        "intent_metrics": {intent: {"correct": correct_counts[intent], "total": total_counts[intent]} for intent in intents},
        "confusion_matrix": confusion_matrix
    }
    
    with open("intent_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    evaluate_intent_classification()