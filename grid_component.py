import pygame
import math

class FrequencyGrid:
    def __init__(self, x, y, width, height, title="Frequency Grid"):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.SysFont('Arial', 16, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Grid parameters
        self.grid_cols = 10
        self.grid_rows = 10
        self.cell_width = (width - 40) // self.grid_cols
        self.cell_height = (height - 60) // self.grid_rows
        
        # Frequency ranges (1:1, 1:2, 2:1, 2:3, 3:2, etc.)
        self.freq_combinations = []
        self.selected_combo = None
        self.hovered_combo = None
        
        # Generate frequency combinations
        self._generate_frequency_combinations()
        
        # Colors
        self.colors = {
            'background': (245, 248, 252),
            'border': (180, 190, 200),
            'header': (65, 105, 225),
            'cell_normal': (255, 255, 255),
            'cell_hover': (220, 230, 255),
            'cell_selected': (100, 150, 255),
            'text': (60, 70, 80),
            'text_light': (255, 255, 255)
        }
    
    def _generate_frequency_combinations(self):
        """Generate common frequency ratio combinations for Lissajous figures"""
        ratios = [
            (1, 1), (1, 2), (2, 1), (1, 3), (3, 1),
            (2, 3), (3, 2), (1, 4), (4, 1), (3, 4),
            (4, 3), (2, 5), (5, 2), (3, 5), (5, 3),
            (4, 5), (5, 4), (1, 6), (6, 1), (5, 6)
        ]
        
        base_freq = 1.0
        for i, (freq_h_ratio, freq_v_ratio) in enumerate(ratios):
            if i < len(ratios):
                freq_h = base_freq * freq_h_ratio
                freq_v = base_freq * freq_v_ratio
                
                # Calculate grid position
                row = i // self.grid_cols
                col = i % self.grid_cols
                
                if row < self.grid_rows:
                    self.freq_combinations.append({
                        'freq_h': freq_h,
                        'freq_v': freq_v,
                        'ratio_text': f"{freq_h_ratio}:{freq_v_ratio}",
                        'row': row,
                        'col': col,
                        'index': i
                    })
    
    def get_cell_rect(self, row, col):
        """Get the rectangle for a specific grid cell"""
        x = self.rect.x + 20 + col * self.cell_width
        y = self.rect.y + 40 + row * self.cell_height
        return pygame.Rect(x, y, self.cell_width - 2, self.cell_height - 2)
    
    def get_cell_from_pos(self, pos):
        """Get the cell coordinates from a mouse position"""
        if not self.rect.collidepoint(pos):
            return None
        
        rel_x = pos[0] - (self.rect.x + 20)
        rel_y = pos[1] - (self.rect.y + 40)
        
        if rel_x < 0 or rel_y < 0:
            return None
        
        col = rel_x // self.cell_width
        row = rel_y // self.cell_height
        
        if row < self.grid_rows and col < self.grid_cols:
            return (row, col)
        return None
    
    def handle_event(self, event):
        """Handle mouse events for the grid"""
        if event.type == pygame.MOUSEMOTION:
            cell = self.get_cell_from_pos(event.pos)
            self.hovered_combo = None
            
            if cell:
                row, col = cell
                for combo in self.freq_combinations:
                    if combo['row'] == row and combo['col'] == col:
                        self.hovered_combo = combo
                        break
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self.get_cell_from_pos(event.pos)
            
            if cell:
                row, col = cell
                for combo in self.freq_combinations:
                    if combo['row'] == row and combo['col'] == col:
                        self.selected_combo = combo
                        return combo  # Return the selected combination
        
        return None
    
    def draw(self, surface):
        """Draw the frequency grid"""
        # Main panel background
        pygame.draw.rect(surface, self.colors['background'], self.rect, border_radius=8)
        pygame.draw.rect(surface, self.colors['border'], self.rect, 2, border_radius=8)
        
        # Header
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
        pygame.draw.rect(surface, self.colors['header'], header_rect, 
                        border_top_left_radius=8, border_top_right_radius=8)
        
        # Title
        title_text = self.font.render(self.title, True, self.colors['text_light'])
        title_x = header_rect.centerx - title_text.get_width() // 2
        surface.blit(title_text, (title_x, header_rect.y + 8))
        
        # Draw grid cells
        for combo in self.freq_combinations:
            cell_rect = self.get_cell_rect(combo['row'], combo['col'])
            
            # Determine cell color
            if self.selected_combo and combo['index'] == self.selected_combo['index']:
                cell_color = self.colors['cell_selected']
                text_color = self.colors['text_light']
            elif self.hovered_combo and combo['index'] == self.hovered_combo['index']:
                cell_color = self.colors['cell_hover']
                text_color = self.colors['text']
            else:
                cell_color = self.colors['cell_normal']
                text_color = self.colors['text']
            
            # Draw cell
            pygame.draw.rect(surface, cell_color, cell_rect, border_radius=4)
            pygame.draw.rect(surface, self.colors['border'], cell_rect, 1, border_radius=4)
            
            # Draw ratio text
            ratio_text = self.small_font.render(combo['ratio_text'], True, text_color)
            text_rect = ratio_text.get_rect(center=cell_rect.center)
            surface.blit(ratio_text, text_rect)
        
        # Draw current selection info
        if self.selected_combo:
            info_y = self.rect.bottom + 10
            info_text = f"Selected: {self.selected_combo['ratio_text']} " \
                       f"(H: {self.selected_combo['freq_h']:.1f} Hz, V: {self.selected_combo['freq_v']:.1f} Hz)"
            info_surface = self.small_font.render(info_text, True, self.colors['text'])
            surface.blit(info_surface, (self.rect.x, info_y))
    
    def get_selected_frequencies(self):
        """Get the currently selected frequency combination"""
        if self.selected_combo:
            return self.selected_combo['freq_h'], self.selected_combo['freq_v']
        return 1.0, 1.0  # Default 1:1 ratio


class LissajousPreview:
    def __init__(self, x, y, size=150):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.font = pygame.font.SysFont('Arial', 14, bold=True)
        
        # Preview parameters
        self.points = []
        self.max_points = 200
        
    def update_preview(self, freq_h, freq_v, phase_h=0, phase_v=0):
        """Update the Lissajous preview with given frequencies"""
        self.points.clear()
        
        # Generate points for the Lissajous curve
        for i in range(self.max_points):
            t = i * 2 * math.pi / 50  # Time parameter
            
            # Lissajous equations
            x = math.sin(freq_h * t + phase_h)
            y = math.sin(freq_v * t + phase_v)
            
            # Convert to screen coordinates
            screen_x = self.rect.centerx + int(x * (self.size - 20) / 2)
            screen_y = self.rect.centery + int(y * (self.size - 20) / 2)
            
            self.points.append((screen_x, screen_y))
    
    def draw(self, surface):
        """Draw the Lissajous preview"""
        # Background
        pygame.draw.rect(surface, (0, 0, 0), self.rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=8)
        
        # Title
        title = self.font.render("Preview", True, (255, 255, 255))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw axes
        center_x, center_y = self.rect.center
        pygame.draw.line(surface, (50, 50, 50), 
                        (self.rect.x + 10, center_y), 
                        (self.rect.right - 10, center_y), 1)
        pygame.draw.line(surface, (50, 50, 50), 
                        (center_x, self.rect.y + 25), 
                        (center_x, self.rect.bottom - 10), 1)
        
        # Draw Lissajous curve
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                alpha = int(255 * (i / len(self.points)))  # Fade effect
                color = (0, alpha, 0)  # Green with fade
                if alpha > 10:  # Only draw visible points
                    pygame.draw.line(surface, color, self.points[i], self.points[i + 1], 2)