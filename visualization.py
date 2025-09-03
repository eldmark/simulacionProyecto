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
        
        # Variables para la simulación
        self.electron_trail = deque(maxlen=100)  # Trail del electrón
        self.screen_persistence = deque(maxlen=1000)  # Puntos persistentes en pantalla
        self.current_electron_pos = [0, 0, 0]  # x, y, z del electrón
        self.electron_velocity = [0, 0, 0]  # vx, vy, vz
        
        # Colores
        self.colors = {
            'background': (240, 240, 240),
            'crt_body': (100, 100, 100),
            'plates': (150, 150, 150),
            'electron_trail': (0, 255, 0),
            'electron': (255, 255, 0),
            'screen_glow': (0, 255, 100),
            'text': (0, 0, 0),
            'border': (50, 50, 50)
        }
        
        # Fuentes
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 18, bold=True)

    def draw_lateral_view(self, surface, V_acc=1000, V_vert=0):
        """
        Dibuja la vista lateral del CRT (muestra deflexión vertical)
        """

        view_rect = self.lateral_view
        pygame.draw.rect(surface, self.colors['background'], view_rect)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 2)
        
        # Título
        title = self.title_font.render("Vista Lateral", True, self.colors['text'])
        surface.blit(title, (view_rect.x + 10, view_rect.y + 5))
        
        # Dibujar el tubo del CRT
        tube_rect = pygame.Rect(view_rect.x + 30, view_rect.y + 80, 280, 60)
        pygame.draw.rect(surface, self.colors['crt_body'], tube_rect, 2)
        
        # Dibujar placas de deflexión vertical
        plate_y_top = view_rect.y + 70
        plate_y_bottom = view_rect.y + 150
        plate_x = view_rect.x + 200
        
        # Placa superior
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_x, plate_y_top, 40, 8), 0)
        # Placa inferior  
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_x, plate_y_bottom, 40, 8), 0)
        
        # Mostrar polaridad de las placas
        polarity_text = "+" if V_vert > 0 else "-" if V_vert < 0 else "0"
        text_pos = surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                                (plate_x + 45, plate_y_top - 5))
        
        polarity_text = "-" if V_vert > 0 else "+" if V_vert < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_x + 45, plate_y_bottom + 10))
        
        # Dibujar trayectoria del electrón (simplificada para esta vista)
        start_x = view_rect.x + 50
        start_y = view_rect.y + 110
        
        # Calcular deflexión aproximada basada en V_vert
        deflection = (V_vert / 1000) * 30  # Escalado para visualización
        
        # Trayectoria en tres segmentos
        points = [
            (start_x, start_y),  # Inicio
            (plate_x, start_y),  # Antes de las placas
            (plate_x + 40, start_y + deflection),  # Después de las placas
            (view_rect.x + 320, start_y + deflection * 1.5)  # Hacia la pantalla
        ]
        
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón actual
        electron_pos = points[-1]
        pygame.draw.circle(surface, self.colors['electron'], 
                            (int(electron_pos[0]), int(electron_pos[1])), 4)

    def draw_top_view(self, surface, V_horiz=0):
        """
        Dibuja la vista superior del CRT (muestra deflexión horizontal)
        """
        
        view_rect = self.top_view
        pygame.draw.rect(surface, self.colors['background'], view_rect)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 2)
        
        # Título
        title = self.title_font.render("Vista Superior", True, self.colors['text'])
        surface.blit(title, (view_rect.x + 10, view_rect.y + 5))
        
        # Dibujar el tubo del CRT
        tube_rect = pygame.Rect(view_rect.x + 30, view_rect.y + 80, 280, 60)
        pygame.draw.rect(surface, self.colors['crt_body'], tube_rect, 2)
        
        # Dibujar placas de deflexión horizontal
        plate_x_left = view_rect.x + 160
        plate_x_right = view_rect.x + 260
        plate_y = view_rect.y + 105
        
        # Placa izquierda
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_x_left, plate_y, 8, 30), 0)
        # Placa derecha
        pygame.draw.rect(surface, self.colors['plates'], 
                        (plate_x_right, plate_y, 8, 30), 0)
        
        # Mostrar polaridad de las placas
        polarity_text = "+" if V_horiz > 0 else "-" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_x_right + 15, plate_y + 10))
        
        polarity_text = "-" if V_horiz > 0 else "+" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_x_left - 15, plate_y + 10))
        
        # Dibujar trayectoria del electrón
        start_x = view_rect.x + 50
        start_y = view_rect.y + 120
        
        # Calcular deflexión aproximada basada en V_horiz
        deflection = (V_horiz / 1000) * 25  # Escalado para visualización
        
        # Trayectoria en tres segmentos
        points = [
            (start_x, start_y),  # Inicio
            (plate_x_left, start_y),  # Antes de las placas
            (plate_x_right + 8, start_y + deflection),  # Después de las placas
            (view_rect.x + 320, start_y + deflection * 1.3)  # Hacia la pantalla
        ]
        
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón actual
        electron_pos = points[-1]
        pygame.draw.circle(surface, self.colors['electron'], 
                            (int(electron_pos[0]), int(electron_pos[1])), 4)

    def draw_screen_view(self, surface, persistence_time=1.0):
        """
        Dibuja la vista frontal de la pantalla del CRT
        """

        view_rect = self.screen_view

        # Fondo negro de la pantalla del CRT
        pygame.draw.rect(surface, (0, 0, 0), view_rect, border_radius= 15)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 3, border_radius=15)

        # Título
        title = self.title_font.render("Pantalla del CRT", True, self.colors['text'])
        surface.blit(title, (view_rect.x, view_rect.y - 25))

        # Limpiar puntos antiguos basado en el tiempo de persistencia
        current_time = time.time()
        self.screen_persistence = deque([
            (pos, timestamp, brightness) for pos, timestamp, brightness in self.screen_persistence
            if current_time - timestamp < persistence_time
        ], maxlen=1000)

        # Dibujar puntos persistentes con fade-out
        for pos, timestamp, brightness in self.screen_persistence:
            age = current_time - timestamp
            fade_factor = max(0, 1 - (age / persistence_time))
            
            # Color con fade
            color_intensity = int(brightness * fade_factor * 255)
            color = (0, color_intensity, 0)  # Verde fosforescente
            
            screen_x = view_rect.x + int(pos[0] * view_rect.width)
            screen_y = view_rect.y + int(pos[1] * view_rect.height)
            
            # Dibujar punto con glow effect
            if color_intensity > 0:
                pygame.draw.circle(surface, color, (screen_x, screen_y), 2)
                # Efecto de brillo
                glow_color = (0, color_intensity // 3, 0)
                pygame.draw.circle(surface, glow_color, (screen_x, screen_y), 4)

    def draw_coordinate_system(self, surface, view_rect, title):
        """
        Dibuja un sistema de coordenadas para las vistas
        """

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

    def add_screen_point(self, normalized_x, normalized_y, brightness=1.0):
        """
        Añade un punto a la pantalla con coordenadas normalizadas (0-1)
        """

        # Asegurar que las coordenadas estén en el rango válido
        normalized_x = max(0, min(1, normalized_x))
        normalized_y = max(0, min(1, normalized_y))
        
        current_time = time.time()
        self.screen_persistence.append(((normalized_x, normalized_y), current_time, brightness))

    def clear_screen_persistence(self):
        """Limpia todos los puntos persistentes de la pantalla"""
        self.screen_persistence.clear()

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
        """
        Función principal que dibuja todas las vistas del CRT
        """

        # Limpiar fondo
        surface.fill((255, 255, 255))
        
        # Dibujar las tres vistas
        self.draw_lateral_view(surface, V_acc, V_vert)
        self.draw_top_view(surface, V_horiz)
        self.draw_screen_view(surface, persistence_time)
        
        # Panel de información
        self.draw_info_panel(surface, V_acc, V_vert, V_horiz, mode_text)
        
        # Instrucciones para el usuario
        instructions = [
            "Controles:",
            "- Ajustar voltajes con sliders",
            "- Cambiar modo para Lissajous",
            "- Tiempo de persistencia"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.colors['text'])
            surface.blit(text, (50, 450 + i * 20))

    def calculate_electron_position(self, V_acc, V_vert, V_horiz, t=0):
        """
        Calcula la posición del electrón basado en los voltajes usando los cálculos físicos reales.
        """
        # Obtener la posición usando los cálculos físicos
        # Usar los nombres correctos de parámetros que espera calculos.py
        result = get_position_by_time(V_acc, V_vert, V_horiz, t)
        
        lateral_pos = result["lateral_view"]
        superior_pos = result["superior_view"]
        
        max_deflection_x = 0.1
        max_deflection_y = 0.1
        
        x_normalized = 0.5 + (superior_pos[1] / (2 * max_deflection_x))
        y_normalized = 0.5 + (lateral_pos[1] / (2 * max_deflection_y))
        
        x_normalized = max(0, min(1, x_normalized))
        y_normalized = max(0, min(1, y_normalized))
        
        return x_normalized, y_normalized

    def generate_lissajous_point(self, t, freq_v, freq_h, phase_v=0, phase_h=0, amplitude=500):
        """
        Genera un punto de las Figuras de Lissajous
        """
        # Señales sinusoidales para las placas
        V_vert = amplitude * math.sin(2 * math.pi * freq_v * t + phase_v)
        V_horiz = amplitude * math.sin(2 * math.pi * freq_h * t + phase_h)
        
        return V_vert, V_horiz

    def update_lissajous_animation(self, freq_v, freq_h, phase_v=0, phase_h=0, dt=0.016):
        """
        Actualiza la animación de las Figuras de Lissajous
        """
        if not hasattr(self, 'lissajous_time'):
            self.lissajous_time = 0
        
        self.lissajous_time += dt
        
        # Generar voltajes sinusoidales
        V_vert, V_horiz = self.generate_lissajous_point(
            self.lissajous_time, freq_v, freq_h, phase_v, phase_h
        )
        
        # Calcular posición en pantalla
        x_pos, y_pos = self.calculate_electron_position(1000, V_vert, V_horiz)
        
        # Añadir punto a la pantalla
        self.add_screen_point(x_pos, y_pos, brightness=0.8)
        
        return V_vert, V_horiz

    def simulate_manual_mode(self, V_acc, V_vert, V_horiz):
        """
        Simula el modo manual donde el usuario controla directamente los voltajes
        """
        x_pos, y_pos = self.calculate_electron_position(V_acc, V_vert, V_horiz)
        
        # En modo manual, solo mostrar el punto actual
        self.clear_screen_persistence()
        self.add_screen_point(x_pos, y_pos, brightness=1.0)

    def simulate_lissajous_mode(self, freq_v, freq_h, phase_v=0, phase_h=0):
        """
        Simula el modo Lissajous con señales sinusoidales
        """
        return self.update_lissajous_animation(freq_v, freq_h, phase_v, phase_h)