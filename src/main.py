import sys
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import requests
import time
from datetime import datetime, timezone, timedelta

current_dir = Path(__file__).resolve().parent
config_path = current_dir.parent / 'config' / 'config.json'

load_dotenv()
LTA_DATAMALL_API_KEY = os.environ.get("LTA_DATAMALL_API_KEY")

with open(config_path, "r") as config_file:
    app_config = json.load(config_file)

class BusStop():
    def __init__(self, name, id):
        self.name = name
        self.id = id

BusStops = [BusStop(stop["name"], stop["id"]) for stop in app_config["stops"]]
ENDPOINT_TEMPLATE = app_config.get("endpoint")

def process_bus_stop(stop_id: int):
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
    
def parse_bus_data(bus_data):
    if bus_data["Services"]:
        services = bus_data["Services"]
        for service in services:
            print(f"Service {service['ServiceNo']}")
            if service["NextBus"]:
                print(f"Time 1: {calculate_remaining_minutes(service['NextBus']['EstimatedArrival'])}")
            if service["NextBus2"]:
                print(f"Time 2: {calculate_remaining_minutes(service['NextBus2']['EstimatedArrival'])}")
            if service["NextBus3"]:
                print(f"Time 3: {calculate_remaining_minutes(service['NextBus3']['EstimatedArrival'])}")

from datetime import datetime, timezone, timedelta

def calculate_remaining_minutes(iso_timestamp: str) -> str:
    """Calculates arrival countdown minutes from an ISO 8601 timestamp string."""
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

def main():
    print(f"Running successfully on Python {sys.version.split()[0]}")
    try:
        while True:
            for stop in BusStops:
                print(f"Processing stop: {stop.name}...")
                bus_data = process_bus_stop(stop.id)

                if bus_data:
                    parse_bus_data(bus_data)

            print("Cycle completed. Sleeping for 60 seconds...")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping the continuous tracker gracefully. Goodbye!")
if __name__ == "__main__":
    main()
