import re

def extract_days(request: str, default_days: int = 2) -> int:
    match = re.search(r'(\d+)\s*(ngày|day)', request, re.IGNORECASE)
    return int(match.group(1)) if match else default_days