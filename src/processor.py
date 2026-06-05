from utils import calculate_remaining_minutes
import requests
from constants import LTA_DATAMALL_API_KEY, BusService, ENDPOINT_TEMPLATE

def process_bus_stop(stop_id: str):
    print(f"Scanning stop: {stop_id}...")

    url = ENDPOINT_TEMPLATE.format(stop_id=stop_id)
    headers = {
        "AccountKey": LTA_DATAMALL_API_KEY, 
        "accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully received data for stop {stop_id}.")
            return data
        else:
            print(f"LTA API returned error code {response.status_code} for stop {stop_id}.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error while scanning stop {stop_id}: {e}")
        return None
    
def parse_bus_data(bus_data) -> dict[str, list[str]]:
    """
    Parses LTA bus data into a dictionary layout.
    Returns: { "67": ["04m", "15m", "26m"], "961M": ["Arr", "12m", "24m"] }
    """

    if bus_data and "Services" in bus_data:
        timings_map: dict[str, list[str]] = {}
        services = bus_data["Services"]
        for service in services:
            bus_service = BusService(service['ServiceNo'])
            if service.get("NextBus") and service["NextBus"].get("EstimatedArrival"):
                bus_service.addTime(calculate_remaining_minutes(service['NextBus']['EstimatedArrival']))
            else:
                bus_service.addTime("--")
            if service.get("NextBus2") and service["NextBus2"].get("EstimatedArrival"):
                bus_service.addTime(calculate_remaining_minutes(service['NextBus2']['EstimatedArrival']))
            else:
                bus_service.addTime("--")
            if service.get("NextBus3") and service["NextBus3"].get("EstimatedArrival"):
                bus_service.addTime(calculate_remaining_minutes(service['NextBus3']['EstimatedArrival']))
            else:
                bus_service.addTime("--")
                
            timings_map[bus_service.id] = bus_service.times
        return timings_map
    else:
        return {}

