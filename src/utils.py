from datetime import datetime, timezone, timedelta

def calculate_remaining_minutes(iso_timestamp: str) -> str:
    if not iso_timestamp:
        return "--"
        
    try:
        arrival_time = datetime.fromisoformat(iso_timestamp)
        sg_timezone = timezone(timedelta(hours=8))
        now = datetime.now(sg_timezone)
        time_delta = arrival_time - now
        remaining_minutes = int(round(time_delta.total_seconds() / 60))
        
        if remaining_minutes <= 0:
            return "Arr"
        return f"{remaining_minutes:02d}m"
        
    except Exception as e:
        print(f"Error parsing timestamp '{iso_timestamp}': {e}")
        return "--"