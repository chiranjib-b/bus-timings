import os
from datetime import datetime, timezone, timedelta
from constants import DIRECTIONS

def print_dashboard_table(status: dict[DIRECTIONS, dict[str, list[str]]]):
    """
    Generates an n-column terminal layout table based on the status dictionary.
    Determines columns dynamically using dictionary keys, using keys as headers.
    """
    # 1. Dynamically extract structural columns from the dictionary keys
    active_columns = sorted(list(status.keys()))
    if not active_columns:
        print("Dashboard Error: No directional columns detected in status map.")
        return

    # 2. Gather all unique bus row services visible across all available column slots
    all_buses = set()
    for col in active_columns:
        all_buses.update(status[col].keys())
    all_bus_rows = sorted(list(all_buses))

    # 3. Determine column sizing parameters dynamically
    # Fixed cell dimensions: 'Bus 961M  : Arr / 12m / 24m' takes up about 27 characters.
    # We assign 32 characters to give a safe padding margin.
    col_width = 32
    
    # Mathematical boundary width calculation: 
    # Total width = (width * number of columns) + interior vertical borders '| '
    border_overhead = (len(active_columns) * 3) + 1
    total_line_width = (col_width * len(active_columns)) + border_overhead
    divider_line = "=" * total_line_width

    # Clear terminal space to trigger frame execution refresh swap
    os.system('cls' if os.name == 'nt' else 'clear')

    # ==================== RENDERING GENERATOR ENGINE ====================
    
    # 1. Generate Header Rows (Using the dictionary keys directly as column titles)
    print(divider_line)
    header_cells = [f"{col:^{col_width}}" for col in active_columns]
    print(f"| {' | '.join(header_cells)} |")
    print(divider_line)

    # 2. Generate Data Body Rows Dynamically
    for bus in all_bus_rows:
        row_cells = []
        for col in active_columns:
            col_data = status[col]
            
            if bus in col_data and col_data[bus]:
                # Combine up to 3 parsed countdown arrival window elements cleanly
                timing_string = " / ".join(col_data[bus])
                cell_text = f"Bus {bus:<5} : {timing_string}"
            else:
                # Text structural spacing layout placeholder fallback
                cell_text = f"Bus {bus:<5} : --"
                
            # Pad the string to the exact width block constraint
            row_cells.append(f"{cell_text:<{col_width}}")
            
        print(f"| {' | '.join(row_cells)} |")

    # 3. Generate Status Dashboard Footer
    print(divider_line)
    sg_time = datetime.now(timezone(timedelta(hours=8))).strftime("%I:%M:%S %p")
    footer_text = f"LTA Live Transit Feed — Last Updated: {sg_time}"
    print(f"| {footer_text:^{total_line_width - 4}} |")
    print(divider_line)
