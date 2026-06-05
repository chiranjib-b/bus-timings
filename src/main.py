import sys
from pathlib import Path
import time
from typing import get_args
import pygame
import sys

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from constants import DIRECTIONS, BusStop, STOPS, API_CALL_INTERVAL_SECONDS
from processor import process_bus_stop, parse_bus_data
from print import print_dashboard_table
from display import LCDDisplay

def main():
    print(f"Running successfully on Python {sys.version.split()[0]}")
    display = LCDDisplay(width=1280, height=800)
    target_directions = get_args(DIRECTIONS)
    last_api_call_time = 0
    try:
        while display.check_active():
            current_time = time.time()
            if current_time - last_api_call_time >= API_CALL_INTERVAL_SECONDS:
                try:
                    status: dict[DIRECTIONS, dict[str, list[str]]] = {}
                    for direction in target_directions:
                        stop_data = STOPS.get(direction)
                        if not stop_data:
                            print(f"Warning: Direction key '{direction}' configuration details missing.")
                            continue
                            
                        stop = BusStop(stop_data["name"], stop_data["id"])
                        print(f"Processing stop ({direction}): {stop.name}...")
                        
                        bus_data = process_bus_stop(stop.id)
                        status[direction] = parse_bus_data(bus_data)
                    
                    print_dashboard_table(status)
                    display.update_data(status)
                    
                except Exception as error:
                    display.update_text([
                        "⚠️ NETWORK ERROR OCCURRED",
                        f"Details: {str(error)}",
                        "Retrying next cycle..."
                    ])
                
                # Update time tracker benchmark
                last_api_call_time = current_time
            time.sleep(0.2)    
            
    except KeyboardInterrupt:
        print("\nStopping the continuous tracker gracefully. Goodbye!")

if __name__ == "__main__":
    main()
