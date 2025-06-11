import re
from thefuzz import fuzz, process
import dateparser
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

# Vietnamese destinations with common misspellings
VIETNAMESE_DESTINATIONS = {
    # Major cities
    "hà nội": ["ha noi", "hanoi", "hoanoi", "thanoi", "hani"],
    "tp. hồ chí minh": ["ho chi minh", "saigon", "sai gon", "tphcm", "hcm", "tp hcm"],
    "đà nẵng": ["da nang", "danang", "đa nẵng"],
    "hải phòng": ["hai phong", "haiphong"],
    "cần thơ": ["can tho", "cantho"],
    
    # Tourist destinations
    "sa pa": ["sapa", "xapa", "sa-pa"],
    "hội an": ["hoi an", "hoian", "hoi-an"],
    "nha trang": ["nhatrang", "nha-trang"],
    "vũng tàu": ["vung tau", "vungtau"],
    "đà lạt": ["da lat", "dalat", "đa lạt"],
    "phú quốc": ["phu quoc", "phuquoc"],
    "hạ long": ["ha long", "halong", "vịnh hạ long", "vinh ha long"],
    "mũi né": ["mui ne", "muine"],
    "tam cốc": ["tam coc", "tamcoc"],
    "ninh bình": ["ninh binh", "ninhbinh"],
    "côn đảo": ["con dao", "condao"],
    
    # Mountain regions
    "mai châu": ["mai chau", "maichau"],
    "mù cang chải": ["mu cang chai", "mucangchai"],
    "điện biên": ["dien bien", "dienbien"],
    "lào cai": ["lao cai", "laocai"],
    
    # Central Vietnam
    "huế": ["hue", "thừa thiên huế"],
    "quảng nam": ["quang nam", "quangnam"],
    "quảng bình": ["quang binh", "quangbinh"],
    "thanh hóa": ["thanh hoa", "thanhhoa"],
}

# Vietnamese number words
VIETNAMESE_NUMBERS = {
    "một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5,
    "sáu": 6, "bảy": 7, "tám": 8, "chín": 9, "mười": 10,
    "mười một": 11, "mười hai": 12, "mười ba": 13, "mười bốn": 14,
    "một mươi": 10, "hai mơi": 20, "ba mười": 30
}

def extract_days(request: str, default_days: int = 2) -> int:
    """Extract trip length from request with better handling"""
    # First try to find digits
    digit_match = re.search(r'(\d+)\s*(ngày|day)', request, re.IGNORECASE)
    if digit_match:
        return int(digit_match.group(1))
    
    # Try Vietnamese number words
    request_lower = request.lower()
    for viet_num, value in VIETNAMESE_NUMBERS.items():
        if f"{viet_num} ngày" in request_lower:
            return value
    
    return default_days

def detect_destination(query: str) -> Optional[str]:
    """
    Robustly identify Vietnamese destination with fuzzy matching.
    Returns the canonical destination name or None if not found.
    """
    query_lower = query.lower()
    
    # Direct match first
    for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
        if canonical in query_lower:
            return canonical
        for alias in aliases:
            if alias in query_lower:
                return canonical
    
    # Fuzzy matching for misspellings
    all_destinations = []
    for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
        all_destinations.append(canonical)
        all_destinations.extend(aliases)
    
    # Extract potential destination words (2-3 word combinations)
    words = query_lower.split()
    for i in range(len(words)):
        for j in range(i+1, min(i+4, len(words)+1)):  # 1-3 word combinations
            candidate = " ".join(words[i:j])
            if len(candidate) >= 3:  # Minimum length
                match, score = process.extractOne(candidate, all_destinations)
                if score >= 80:  # High confidence threshold
                    # Find canonical name
                    for canonical, aliases in VIETNAMESE_DESTINATIONS.items():
                        if match == canonical or match in aliases:
                            return canonical
    
    return None

def detect_trip_length(query: str) -> Optional[int]:
    """
    Detect trip duration from query.
    Handles both digits and Vietnamese number words.
    """
    return extract_days(query, None)

def detect_time(query: str) -> Optional[Dict[str, Any]]:
    """
    Detect dates/time information from query.
    Handles various formats including relative dates.
    """
    query_lower = query.lower()
    
    # Configure dateparser for Vietnamese
    dateparser_settings = {
        'LANGUAGES': ['vi', 'en'],
        'DATE_ORDER': 'DMY',
        'RETURN_AS_TIMEZONE_AWARE': False
    }
    
    time_info = {
        "has_dates": False,
        "start_date": None,
        "end_date": None,
        "relative_time": None,
        "date_format": None
    }
    
    # Common Vietnamese time expressions
    time_patterns = [
        # Absolute dates
        (r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', 'absolute_date'),
        (r'ngày (\d{1,2}) tháng (\d{1,2})', 'vietnamese_date'),
        
        # Relative dates
        (r'ngày mai|tomorrow', 'tomorrow'),
        (r'hôm nay|today', 'today'),
        (r'tuần sau|next week', 'next_week'),
        (r'cuối tuần này|this weekend', 'this_weekend'),
        (r'tháng sau|next month', 'next_month'),
        (r'(\d+) ngày nữa', 'days_from_now'),
        (r'(\d+) tuần nữa', 'weeks_from_now'),
    ]
    
    for pattern, time_type in time_patterns:
        match = re.search(pattern, query_lower)
        if match:
            time_info["has_dates"] = True
            time_info["date_format"] = time_type
            
            if time_type == 'absolute_date':
                day, month, year = match.groups()
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    time_info["start_date"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            elif time_type == 'vietnamese_date':
                day, month = match.groups()
                try:
                    current_year = datetime.now().year
                    date_obj = datetime(current_year, int(month), int(day))
                    time_info["start_date"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            elif time_type == 'tomorrow':
                tomorrow = datetime.now() + timedelta(days=1)
                time_info["start_date"] = tomorrow.strftime("%Y-%m-%d")
                time_info["relative_time"] = "tomorrow"
            
            elif time_type == 'today':
                today = datetime.now()
                time_info["start_date"] = today.strftime("%Y-%m-%d")
                time_info["relative_time"] = "today"
            
            elif time_type == 'this_weekend':
                today = datetime.now()
                days_until_saturday = (5 - today.weekday()) % 7
                saturday = today + timedelta(days=days_until_saturday)
                time_info["start_date"] = saturday.strftime("%Y-%m-%d")
                time_info["relative_time"] = "this_weekend"
            
            elif time_type == 'days_from_now':
                days = int(match.group(1))
                future_date = datetime.now() + timedelta(days=days)
                time_info["start_date"] = future_date.strftime("%Y-%m-%d")
                time_info["relative_time"] = f"{days}_days_from_now"
            
            break
    
    # Try dateparser as fallback
    if not time_info["has_dates"]:
        parsed_date = dateparser.parse(query, settings=dateparser_settings)
        if parsed_date and parsed_date > datetime.now():
            time_info["has_dates"] = True
            time_info["start_date"] = parsed_date.strftime("%Y-%m-%d")
            time_info["date_format"] = "parsed"
    
    return time_info if time_info["has_dates"] else None

def classify_intent(query: str) -> str:
    """
    Classify user intent from query.
    Returns: 'eat', 'visit', 'plan', 'book', or 'other'
    """
    query_lower = query.lower()
    
    # Intent keywords
    intent_keywords = {
        'eat': [
            'ăn', 'món', 'quán', 'nhà hàng', 'food', 'eat', 'restaurant',
            'đặc sản', 'ẩm thực', 'cuisine', 'dish', 'meal', 'breakfast',
            'lunch', 'dinner', 'snack', 'drink', 'cafe', 'coffee',
            'phở', 'bánh', 'bún', 'chả', 'nem'
        ],
        'visit': [
            'thăm', 'tham quan', 'visit', 'see', 'go to', 'attraction',
            'địa điểm', 'điểm', 'chỗ', 'place', 'location', 'destination',
            'bảo tàng', 'museum', 'temple', 'chùa', 'pagoda', 'beach',
            'bãi biển', 'núi', 'mountain', 'lake', 'hồ', 'park', 'công viên'
        ],
        'plan': [
            'lịch trình', 'kế hoạch', 'plan', 'itinerary', 'schedule',
            'tour', 'chuyến đi', 'trip', 'travel', 'du lịch',
            'ngày', 'day', 'tuần', 'week', 'tháng', 'month'
        ],
        'book': [
            'đặt', 'book', 'booking', 'reservation', 'hotel', 'khách sạn',
            'homestay', 'resort', 'phòng', 'room', 'accommodation',
            'lưu trú', 'nghỉ', 'stay'
        ]
    }
    
    # Count matches for each intent
    intent_scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        intent_scores[intent] = score
    
    # Find best match
    best_intent = max(intent_scores, key=intent_scores.get)
    
    # If no clear match, check for specific patterns
    if intent_scores[best_intent] == 0:
        if any(word in query_lower for word in ['gì', 'what', 'how', 'where', 'khi nào', 'when']):
            return 'other'
        return 'plan'  # Default for travel-related queries
    
    return best_intent

def extract_preferences(query: str) -> Dict[str, str]:
    """Extract user preferences from query"""
    preferences = {}
    query_lower = query.lower()
    
    # Activity preferences
    if any(word in query_lower for word in ['lịch sử', 'history', 'văn hóa', 'culture']):
        preferences['activity_type'] = 'cultural_historical'
    elif any(word in query_lower for word in ['thiên nhiên', 'nature', 'núi', 'mountain', 'biển', 'beach']):
        preferences['activity_type'] = 'nature_outdoor'
    elif any(word in query_lower for word in ['thư giãn', 'relax', 'nghỉ ngơi', 'rest']):
        preferences['activity_type'] = 'relaxation'
    elif any(word in query_lower for word in ['phiêu lưu', 'adventure', 'thể thao', 'sport']):
        preferences['activity_type'] = 'adventure_sports'
    
    # Food preferences
    if any(word in query_lower for word in ['truyền thống', 'traditional', 'đặc sản', 'local']):
        preferences['food_type'] = 'traditional_local'
    elif any(word in query_lower for word in ['đường phố', 'street food', 'bình dân']):
        preferences['food_type'] = 'street_food'
    elif any(word in query_lower for word in ['cao cấp', 'fine dining', 'sang trọng']):
        preferences['food_type'] = 'fine_dining'
    
    # Budget preferences
    if any(word in query_lower for word in ['rẻ', 'cheap', 'tiết kiệm', 'budget']):
        preferences['budget'] = 'budget'
    elif any(word in query_lower for word in ['cao cấp', 'luxury', 'sang trọng']):
        preferences['budget'] = 'luxury'
    else:
        preferences['budget'] = 'mid_range'
    
    return preferences