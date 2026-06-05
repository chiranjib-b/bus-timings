import pygame
import threading
import sys
from datetime import datetime, timezone, timedelta

class LCDDisplay:
    def __init__(self, width=1280, height=800):
        self.width = width
        self.height = height
        
        # We now pass the RAW dictionary status payload directly, not the console text string
        self.status_data = {}
        self.is_running = True
        
        self.thread = threading.Thread(target=self._run_display_loop, daemon=True)
        self.thread.start()

    def _run_display_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("LTA Transit Live Dashboard")
        clock = pygame.time.Clock()
        
        # Clean, modern sans-serif fonts for clear readability on a 10-inch LCD
        font_title = pygame.font.SysFont("Arial", 28, bold=True)
        font_header = pygame.font.SysFont("Arial", 24, bold=True)
        font_body = pygame.font.SysFont("Arial", 22, bold=False)
        font_bus = pygame.font.SysFont("Arial", 22, bold=True)
        font_footer = pygame.font.SysFont("Arial", 16)

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.is_running = False
            
            # 1. Base UI Palette Colors (Deep Matte Tech Theme)
            BACKGROUND_CLR = (15, 18, 26)
            CARD_CLR = (24, 30, 43)
            TEXT_PRIMARY = (240, 244, 255)
            TEXT_MUTED = (140, 155, 175)
            ACCENT_GREEN = (0, 230, 135)
            BORDER_CLR = (40, 52, 74)
            
            screen.fill(BACKGROUND_CLR)
            
            # 2. Draw Top Header Bar Geometry
            pygame.draw.rect(screen, CARD_CLR, (30, 30, self.width - 60, 70), border_radius=8)
            pygame.draw.rect(screen, BORDER_CLR, (30, 30, self.width - 60, 70), 2, border_radius=8)
            
            title_surf = font_title.render("LTA LIVE TRANSIT FEED", True, TEXT_PRIMARY)
            screen.blit(title_surf, (50, 48))
            
            # 3. Dynamic Column Parsing Layout Calculation
            active_columns = sorted(list(self.status_data.keys()))
            
            if not active_columns:
                # Fallback loading screen state
                loading_surf = font_header.render("Waiting for live API data packet sync...", True, TEXT_MUTED)
                screen.blit(loading_surf, (50, 150))
            else:
                # Calculate columns layout dynamically based on dictionary keys count
                num_cols = len(active_columns)
                margin = 30
                spacing = 20
                total_avail_width = self.width - (margin * 2) - (spacing * (num_cols - 1))
                col_width = total_avail_width // num_cols
                
                # Extract unique bus identifiers across all directional blocks
                all_buses = set()
                for col in active_columns:
                    all_buses.update(self.status_data[col].keys())
                all_bus_rows = sorted(list(all_buses))
                
                # 4. Draw Columns Layout Panels
                for col_idx, col_name in enumerate(active_columns):
                    col_x = margin + col_idx * (col_width + spacing)
                    col_y = 120
                    col_height = self.height - col_y - 80 # leave room for footer
                    
                    # Draw solid background cards for each travel direction column
                    pygame.draw.rect(screen, CARD_CLR, (col_x, col_y, col_width, col_height), border_radius=8)
                    pygame.draw.rect(screen, BORDER_CLR, (col_x, col_y, col_width, col_height), 2, border_radius=8)
                    
                    # Render Column Headers Text
                    head_surf = font_header.render(str(col_name).upper(), True, ACCENT_GREEN)
                    screen.blit(head_surf, (col_x + 20, col_y + 20))
                    pygame.draw.line(screen, BORDER_CLR, (col_x + 15, col_y + 60), (col_x + col_width - 15, col_y + 60), 2)
                    
                    # 5. Populate rows within this specific column layout block
                    row_start_y = col_y + 80
                    row_height = 45
                    
                    for row_idx, bus_id in enumerate(all_bus_rows):
                        current_row_y = row_start_y + (row_idx * row_height)
                        
                        # Alternating micro-shading row bands for high structural scannability
                        if row_idx % 2 == 0:
                            pygame.draw.rect(screen, (32, 40, 57), (col_x + 10, current_row_y - 5, col_width - 20, 36), border_radius=4)
                        
                        # Draw Bus Identifier Number Tag
                        bus_surf = font_bus.render(f"Bus {bus_id}", True, TEXT_PRIMARY)
                        screen.blit(bus_surf, (col_x + 20, current_row_y))
                        
                        # Check arrivals dictionary safely
                        col_data = self.status_data[col_name]
                        if bus_id in col_data and col_data[bus_id]:
                            timing_text = "  |  ".join(col_data[bus_id])
                            timing_surf = font_body.render(timing_text, True, ACCENT_GREEN)
                        else:
                            timing_surf = font_body.render("--", True, TEXT_MUTED)
                            
                        # Align timings text tracking nicely to the right section of the data row cell bounds
                        screen.blit(timing_surf, (col_x + 140, current_row_y))

            # 6. Render Dashboard Live Clock Footer Layout Block
            sg_time = datetime.now(timezone(timedelta(hours=8))).strftime("%I:%M:%S %p")
            footer_text = f"Singapore Live Transit Datastream — Last Updated: {sg_time}"
            footer_surf = font_footer.render(footer_text, True, TEXT_MUTED)
            screen.blit(footer_surf, (35, self.height - 45))
            
            pygame.display.flip()
            clock.tick(30)
            
        pygame.quit()

    def update_data(self, real_status_dict):
        """Pass your RAW live status dictionary straight here from main.py"""
        self.status_data = real_status_dict

    def check_active(self):
        return self.is_running

    def close(self):
        self.is_running = False
