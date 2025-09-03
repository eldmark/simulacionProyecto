import pygame
import math
from collections import deque
import time
from calculos import get_position_by_time

class CRTVisualizer:
    def __init__(self, screen_width=1200, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Definir áreas de las tres vistas
        self.lateral_view = pygame.Rect(50, 50, 350, 200)
        self.top_view = pygame.Rect(450, 50, 350, 200)
        self.screen_view = pygame.Rect(450, 300, 300, 300)
        
        # Parámetros físicos del CRT (valores fijos como especifica el proyecto)
        self.screen_size = 0.25  # 25 cm (pantalla cuadrada)
        self.plate_area = 0.01   # 1 cm²
        self.plate_separation = 0.02  # 2 cm
        self.distance_gun_to_vert_plates = 0.05  # 5 cm
        self.distance_vert_to_horiz_plates = 0.03  # 3 cm
        self.distance_plates_to_screen = 0.15  # 15 cm
        
        # FIXED: Separate collections for different modes
        self.electron_trail = deque(maxlen=100)
        self.screen_persistence = deque(maxlen=2000)  # Manual mode points (green)
        self.lissajous_points = deque(maxlen=10000)   # Lissajous mode points (yellow)
        self.current_electron_pos = [0, 0, 0]
        self.electron_velocity = [0, 0, 0]
        self.current_mode = "manual"
        
        # FIXED: Improved colors for better visibility
        self.colors = {
            'background': (240, 240, 240),
            'crt_body': (100, 100, 100),
            'plates': (150, 150, 150),
            'electron_trail': (0, 255, 0),
            'electron': (255, 255, 0),
            'screen_glow': (0, 255, 100),
            'lissajous_points': (255, 255, 0),  # Bright yellow
            'lissajous_glow': (255, 255, 150),  # Light yellow for glow
            'manual_points': (0, 255, 0),       # Bright green
            'manual_glow': (100, 255, 100),     # Light green for glow
            'text': (0, 0, 0),
            'border': (50, 50, 50)
        }
        
        # Fuentes
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 18, bold=True)

    def set_mode(self, mode):
        """FIXED: Properly set mode and handle transitions"""
        new_mode = mode.lower()
        
        # Only clear points if mode actually changed
        if hasattr(self, 'current_mode') and self.current_mode != new_mode:
            if new_mode == "lissajous":
                self.screen_persistence.clear()  # Clear manual points
            else:
                self.lissajous_points.clear()    # Clear lissajous points
        
        self.current_mode = new_mode

    def draw_lateral_view(self, surface, V_acc=1000, V_vert=0):
        """Dibuja la vista lateral del CRT (muestra deflexión vertical)"""
        view_rect = self.lateral_view
        pygame.draw.rect(surface, self.colors['background'], view_rect)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 2)
        
        # Título
        title = self.title_font.render("Vista Lateral", True, self.colors['text'])
        surface.blit(title, (view_rect.x + 10, view_rect.y + 5))
        
        # Dibujar el tubo del CRT
        tube_rect = pygame.Rect(view_rect.x + 30, view_rect.y + 80, 280, 60)
        pygame.draw.rect(surface, self.colors['crt_body'], tube_rect, 2)
        
        # CORREGIDO: Placas de deflexión vertical en la posición física correcta
        total_length = 0.23  # 23 cm total (5+5+3+15 cm)
        tube_start_x = view_rect.x + 30
        
        plate_start_x = tube_start_x + int((self.distance_gun_to_vert_plates / total_length) * 280)
        plate_end_x = plate_start_x + int((0.05 / total_length) * 280)  # 5 cm de longitud de placa
        
        plate_y_top = view_rect.y + 70
        plate_y_bottom = view_rect.y + 150
        plate_width = plate_end_x - plate_start_x
        
        # Placa superior
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_start_x, plate_y_top, plate_width, 8), 0)
        # Placa inferior  
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_start_x, plate_y_bottom, plate_width, 8), 0)
        
        # Mostrar polaridad de las placas
        polarity_text = "+" if V_vert > 0 else "-" if V_vert < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_end_x + 5, plate_y_top - 5))
        
        polarity_text = "-" if V_vert > 0 else "+" if V_vert < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_end_x + 5, plate_y_bottom + 10))
        
        # Dibujar trayectoria del electrón (simplificada para esta vista)
        start_x = view_rect.x + 50
        start_y = view_rect.y + 110
        
        # Calcular deflexión aproximada basada en V_vert
        deflection = (V_vert / 1000) * 30  # Escalado para visualización
        
        # Trayectoria en segmentos que corresponden a las regiones físicas
        points = [
            (start_x, start_y),  # Inicio (cañón)
            (plate_start_x, start_y),  # Antes de las placas verticales
            (plate_end_x, start_y + deflection * 0.5),  # Durante las placas (deflexión parcial)
            (view_rect.x + 320, start_y + deflection)  # Después de las placas (deflexión completa)
        ]
        
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón actual
        electron_pos = points[-1]
        pygame.draw.circle(surface, self.colors['electron'], 
                            (int(electron_pos[0]), int(electron_pos[1])), 4)

    def draw_top_view(self, surface, V_acc=1000, V_horiz=0):
        """Dibuja la vista superior del CRT (muestra deflexión horizontal)"""
        view_rect = self.top_view
        pygame.draw.rect(surface, self.colors['background'], view_rect)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 2)
        
        # Título
        title = self.title_font.render("Vista Superior", True, self.colors['text'])
        surface.blit(title, (view_rect.x + 10, view_rect.y + 5))
        
        # Dibujar el tubo del CRT
        tube_rect = pygame.Rect(view_rect.x + 30, view_rect.y + 80, 280, 60)
        pygame.draw.rect(surface, self.colors['crt_body'], tube_rect, 2)
        
        # CORREGIDO: Placas de deflexión horizontal en la posición física correcta
        total_length = 0.23  # 23 cm total
        tube_start_x = view_rect.x + 30
        
        plate_start_pos = self.distance_gun_to_vert_plates + 0.05 + self.distance_vert_to_horiz_plates  # 13 cm
        plate_start_x = tube_start_x + int((plate_start_pos / total_length) * 280)
        plate_end_x = plate_start_x + int((0.05 / total_length) * 280)  # 5 cm de longitud de placa
        
        plate_y_center = view_rect.y + 110
        plate_height = 25
        
        # Placa superior (en vista superior se ve como líneas horizontales)
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_start_x, plate_y_center - plate_height//2 - 5, 
                         plate_end_x - plate_start_x, 8), 0)
        # Placa inferior
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_start_x, plate_y_center + plate_height//2 - 3, 
                         plate_end_x - plate_start_x, 8), 0)
        
        # Mostrar polaridad de las placas
        polarity_text = "+" if V_horiz > 0 else "-" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_end_x + 5, plate_y_center + plate_height//2 - 8))
        
        polarity_text = "-" if V_horiz > 0 else "+" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_end_x + 5, plate_y_center - plate_height//2 - 5))
        
        # Dibujar trayectoria del electrón
        start_x = view_rect.x + 50
        start_y = view_rect.y + 110
        
        # Calcular deflexión aproximada basada en V_horiz
        deflection = (V_horiz / 1000) * 25  # Escalado para visualización
        
        # Trayectoria en segmentos que corresponden a las regiones físicas
        points = [
            (start_x, start_y),  # Inicio (cañón)
            (plate_start_x, start_y),  # Antes de las placas horizontales
            (plate_end_x, start_y + deflection * 0.5),  # Durante las placas (deflexión parcial)
            (view_rect.x + 320, start_y + deflection)  # Después de las placas (deflexión completa)
        ]
        
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón actual
        electron_pos = points[-1]
        pygame.draw.circle(surface, self.colors['electron'], 
                            (int(electron_pos[0]), int(electron_pos[1])), 4)

    def draw_screen_view(self, surface, persistence_time=1.0):
        """FIXED: Enhanced screen view with better point visibility"""
        view_rect = self.screen_view

        # Fondo negro de la pantalla del CRT
        pygame.draw.rect(surface, (0, 0, 0), view_rect, border_radius=15)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 3, border_radius=15)

        # Título con indicador del modo
        mode_indicator = f"({self.current_mode.upper()})"
        title_text = f"Pantalla del CRT {mode_indicator}"
        title = self.title_font.render(title_text, True, self.colors['text'])
        surface.blit(title, (view_rect.x, view_rect.y - 25))

        current_time = time.time()

        # FIXED: Better Lissajous rendering
        if self.current_mode == "lissajous":
            # Draw all lissajous points (they are persistent)
            points_drawn = 0
            for pos, timestamp, brightness in self.lissajous_points:
                screen_x = view_rect.x + int(pos[0] * view_rect.width)
                screen_y = view_rect.y + int(pos[1] * view_rect.height)
                
                # Ensure coordinates are within screen bounds
                if (view_rect.x <= screen_x < view_rect.right and 
                    view_rect.y <= screen_y < view_rect.bottom):
                    
                    # Bright yellow points for Lissajous
                    color_intensity = min(255, int(brightness * 255))
                    point_color = (color_intensity, color_intensity, 0)  # Yellow
                    glow_color = (color_intensity // 3, color_intensity // 3, 0)  # Dimmer yellow
                    
                    # Draw glow effect first (larger, dimmer)
                    pygame.draw.circle(surface, glow_color, (screen_x, screen_y), 3)
                    # Draw bright center point
                    pygame.draw.circle(surface, point_color, (screen_x, screen_y), 1)
                    points_drawn += 1

        else:  # Manual mode
            # Clean up old points based on persistence time
            self.screen_persistence = deque([
                (pos, timestamp, brightness) for pos, timestamp, brightness in self.screen_persistence
                if current_time - timestamp < persistence_time
            ], maxlen=2000)

            # Draw manual mode points with fade
            points_drawn = 0
            for pos, timestamp, brightness in self.screen_persistence:
                age = current_time - timestamp
                fade_factor = max(0, 1 - (age / persistence_time))
                
                screen_x = view_rect.x + int(pos[0] * view_rect.width)
                screen_y = view_rect.y + int(pos[1] * view_rect.height)
                
                # Ensure coordinates are within screen bounds
                if (view_rect.x <= screen_x < view_rect.right and 
                    view_rect.y <= screen_y < view_rect.bottom):
                    
                    # Green color with fade
                    color_intensity = min(255, int(brightness * fade_factor * 255))
                    if color_intensity > 10:  # Only draw visible points
                        point_color = (0, color_intensity, 0)  # Green
                        glow_color = (0, color_intensity // 4, 0)  # Dimmer green
                        
                        # Draw glow effect first (larger, dimmer)
                        pygame.draw.circle(surface, glow_color, (screen_x, screen_y), 4)
                        # Draw bright center point
                        pygame.draw.circle(surface, point_color, (screen_x, screen_y), 2)
                        points_drawn += 1

        # Show point count and mode info
        info_color = self.colors['lissajous_points'] if self.current_mode == "lissajous" else self.colors['manual_points']
        count_text = f"Puntos: {len(self.lissajous_points) if self.current_mode == 'lissajous' else len(self.screen_persistence)}"
        count_surface = pygame.font.SysFont('Arial', 12).render(count_text, True, info_color)
        surface.blit(count_surface, (view_rect.x + 5, view_rect.y + 5))

    def add_screen_point(self, normalized_x, normalized_y, brightness=1.0, mode="manual"):
        """FIXED: Enhanced point addition with better coordinate handling"""
        # Clamp coordinates to valid range
        normalized_x = max(0.0, min(1.0, normalized_x))
        normalized_y = max(0.0, min(1.0, normalized_y))
        
        current_time = time.time()
        point_data = ((normalized_x, normalized_y), current_time, brightness)
        
        # Add to appropriate collection
        if mode.lower() == "lissajous" or self.current_mode == "lissajous":
            self.lissajous_points.append(point_data)
        else:
            self.screen_persistence.append(point_data)

    def clear_screen_persistence(self):
        """Clear points for current mode"""
        if self.current_mode == "lissajous":
            self.lissajous_points.clear()
        else:
            self.screen_persistence.clear()

    def clear_all_points(self):
        """Clear ALL points from both modes"""
        self.screen_persistence.clear()
        self.lissajous_points.clear()

    def draw_coordinate_system(self, surface, view_rect, title):
        """Dibuja un sistema de coordenadas para las vistas"""
        # Ejes
        center_x = view_rect.centerx
        center_y = view_rect.centery
        
        # Eje X
        pygame.draw.line(surface, (100, 100, 100), 
                        (view_rect.x + 20, center_y), 
                        (view_rect.right - 20, center_y), 1)
        # Eje Y
        pygame.draw.line(surface, (100, 100, 100), 
                        (center_x, view_rect.y + 30), 
                        (center_x, view_rect.bottom - 20), 1)

    def draw_info_panel(self, surface, V_acc, V_vert, V_horiz, mode_text="Manual"):
        """Dibuja panel de información con valores actuales"""
        info_x = 50
        info_y = 300
        
        info_texts = [
            f"Modo: {mode_text}",
            f"V_aceleración: {V_acc:.0f} V",
            f"V_vertical: {V_vert:.0f} V", 
            f"V_horizontal: {V_horiz:.0f} V"
        ]
        
        for i, text in enumerate(info_texts):
            rendered_text = self.font.render(text, True, self.colors['text'])
            surface.blit(rendered_text, (info_x, info_y + i * 25))

    def draw_all_views(self, surface, V_acc=1000, V_vert=0, V_horiz=0, 
                        persistence_time=1.0, mode_text="Manual"):
        """FIXED: Main drawing function with proper mode handling"""
        # Update mode
        self.set_mode(mode_text)
        
        # Clear background
        surface.fill((255, 255, 255))
        
        # Draw all three views
        self.draw_lateral_view(surface, V_acc, V_vert)
        self.draw_top_view(surface, V_acc, V_horiz)
        self.draw_screen_view(surface, persistence_time)
        
        # Info panel
        self.draw_info_panel(surface, V_acc, V_vert, V_horiz, mode_text)
        
        # UPDATED instructions
        instructions = [
            "Controles:",
            "- Ajustar voltajes con sliders",
            "- Cambiar modo para Lissajous",
            "- Modo Lissajous: Puntos AMARILLOS permanentes", 
            "- Modo Manual: Puntos VERDES con fade"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.colors['text'])
            surface.blit(text, (50, 450 + i * 20))

    def calculate_electron_position(self, V_acc, V_vert, V_horiz, t=0):
        """MEJORADO: Cálculo de posición que responde correctamente a voltajes"""
        try:
            # NUEVO: Mapeo directo y más intuitivo de voltajes a posición
            # Para modo manual, usar mapeo directo sin física compleja
            if self.current_mode == "manual":
                # Mapear voltajes directamente a posición de pantalla
                # V_horiz controla movimiento horizontal (X)
                # V_vert controla movimiento vertical (Y)
                
                max_voltage = 1000.0  # Voltaje máximo según sliders
                
                # Convertir voltaje a posición normalizada (0 a 1)
                # Voltaje 0 = centro (0.5), voltaje positivo = derecha/arriba, voltaje negativo = izquierda/abajo
                x_normalized = 0.5 + (V_horiz / (2 * max_voltage))  # Horizontal
                y_normalized = 0.5 - (V_vert / (2 * max_voltage))   # Vertical (invertido para que + sea arriba)
                
                # Asegurar que esté en rango válido
                x_normalized = max(0.0, min(1.0, x_normalized))
                y_normalized = max(0.0, min(1.0, y_normalized))
                
                return x_normalized, y_normalized
            
            else:  # Modo Lissajous - usar cálculos físicos
                # Use physics calculations for Lissajous mode
                result = get_position_by_time(V_acc, V_vert, V_horiz, t)
                
                lateral_pos = result["lateral_view"]
                superior_pos = result["superior_view"]
                
                # Scale deflections appropriately for Lissajous
                max_deflection_x = 0.12
                max_deflection_y = 0.12
                
                # Convert to normalized screen coordinates (0 to 1)
                x_normalized = 0.5 + (superior_pos[1] / (2 * max_deflection_x))
                y_normalized = 0.5 + (lateral_pos[1] / (2 * max_deflection_y))
                
                # Clamp to screen bounds
                x_normalized = max(0.0, min(1.0, x_normalized))
                y_normalized = max(0.0, min(1.0, y_normalized))
                
                return x_normalized, y_normalized
            
        except Exception as e:
            # Fallback to center if calculation fails
            print(f"Position calculation error: {e}")
            return 0.5, 0.5