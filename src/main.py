import sys
from pathlib import Path
import time
from typing import get_args

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from constants import DIRECTIONS, BusStop, STOPS
from processor import process_bus_stop, parse_bus_data
from print import print_dashboard_table

def main():
    print(f"Running successfully on Python {sys.version.split()[0]}")
    target_directions = get_args(DIRECTIONS)
    try:
        while True:
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
            
            print("\n[VERIFICATION RAW DATA DUMP]:")
            print(status)
            print("==========================================================================================")

            print_dashboard_table(status)

            print("Cycle completed. Sleeping for 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nStopping the continuous tracker gracefully. Goodbye!")

if __name__ == "__main__":
    main()
