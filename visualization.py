import pygame
import math
from collections import deque
import time
# Importar las funciones de cálculos físicos
from calculos import get_position_by_time, ini_speed, region_time

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
        Ahora usa los cálculos físicos reales de calculos.py
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
        
        # Dibujar placas VERTICALES vistas de canto (líneas verticales)
        plate_x = view_rect.x + 120  # Posición basada en distancias físicas
        plate_top = view_rect.y + 70
        plate_bottom = view_rect.y + 150
        plate_center = view_rect.y + 110
        
        # Placa vertical izquierda (vista de canto - línea vertical)
        pygame.draw.line(surface, self.colors['plates'], 
                        (plate_x, plate_top), (plate_x, plate_bottom), 4)
        # Placa vertical derecha (vista de canto - línea vertical)
        pygame.draw.line(surface, self.colors['plates'], 
                        (plate_x + 40, plate_top), (plate_x + 40, plate_bottom), 4)
        
        # Mostrar polaridad de las placas verticales
        polarity_text = "+" if V_vert > 0 else "-" if V_vert < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_x - 15, plate_center - 10))
        
        polarity_text = "-" if V_vert > 0 else "+" if V_vert < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_x + 45, plate_center - 10))
        
        # Dibujar trayectoria del electrón usando cálculos físicos reales
        self.draw_electron_trajectory_lateral(surface, view_rect, V_acc, V_vert)

    def draw_top_view(self, surface, V_acc=1000, V_horiz=0):
        """
        Dibuja la vista superior del CRT (muestra deflexión horizontal)
        Ahora usa los cálculos físicos reales de calculos.py
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
        
        # Dibujar placas HORIZONTALES vistas de canto (líneas horizontales)
        plate_y = view_rect.y + 100
        plate_left = view_rect.x + 200  # Posición basada en distancias físicas
        plate_right = view_rect.x + 240
        plate_center_x = view_rect.x + 220
        
        # Placa horizontal superior (vista de canto - línea horizontal)
        pygame.draw.line(surface, self.colors['plates'], 
                        (plate_left, plate_y), (plate_right, plate_y), 4)
        # Placa horizontal inferior (vista de canto - línea horizontal)
        pygame.draw.line(surface, self.colors['plates'], 
                        (plate_left, plate_y + 40), (plate_right, plate_y + 40), 4)
        
        # Mostrar polaridad de las placas horizontales
        polarity_text = "+" if V_horiz > 0 else "-" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_center_x - 10, plate_y - 20))
        
        polarity_text = "-" if V_horiz > 0 else "+" if V_horiz < 0 else "0"
        surface.blit(self.font.render(polarity_text, True, self.colors['text']), 
                    (plate_center_x - 10, plate_y + 50))
        
        # Dibujar trayectoria del electrón usando cálculos físicos reales
        self.draw_electron_trajectory_superior(surface, view_rect, V_acc, V_horiz)

    def draw_electron_trajectory_lateral(self, surface, view_rect, V_acc, V_vert):
        """Dibuja la trayectoria del electrón en vista lateral usando calculos.py"""
        if V_acc <= 0:
            return
            
        # Usar las funciones de calculos.py para obtener el tiempo total
        speed = ini_speed(V_acc)
        region_times = region_time(speed)
        total_time = region_times["reach_screen"]
        
        # Generar puntos de la trayectoria usando get_position_by_time
        points = []
        time_steps = 50
        
        for i in range(time_steps + 1):
            t = (i / time_steps) * total_time
            # Usar la función de calculos.py
            pos_data = get_position_by_time(V_acc, V_vert, 0, t)
            depth, deflection = pos_data["lateral_view"]
            
            # Convertir coordenadas físicas a coordenadas de pantalla
            # Distancia total del tubo
            total_distance = 0.05 + 0.05 + 0.03 + 0.05 + 0.15  # Basado en calculos.py
            x_screen = view_rect.x + 40 + (depth / total_distance) * 250
            
            # Escalar deflexión (convertir metros a píxeles)
            deflection_pixels = deflection * 2000  # Factor de escala para visualización
            y_screen = view_rect.y + 110 - deflection_pixels  # Invertir Y
            
            # Limitar a la vista
            x_screen = max(view_rect.x + 40, min(view_rect.x + 320, x_screen))
            y_screen = max(view_rect.y + 50, min(view_rect.y + 190, y_screen))
            
            points.append((int(x_screen), int(y_screen)))
        
        # Dibujar trayectoria
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón en la posición final
        if points:
            pygame.draw.circle(surface, self.colors['electron'], points[-1], 4)

    def draw_electron_trajectory_superior(self, surface, view_rect, V_acc, V_horiz):
        """Dibuja la trayectoria del electrón en vista superior usando calculos.py"""
        if V_acc <= 0:
            return
            
        # Usar las funciones de calculos.py
        speed = ini_speed(V_acc)
        region_times = region_time(speed)
        total_time = region_times["reach_screen"]
        
        # Generar puntos de la trayectoria usando get_position_by_time
        points = []
        time_steps = 50
        
        for i in range(time_steps + 1):
            t = (i / time_steps) * total_time
            # Usar la función de calculos.py
            pos_data = get_position_by_time(V_acc, 0, V_horiz, t)
            depth, deflection = pos_data["superior_view"]
            
            # Convertir coordenadas físicas a coordenadas de pantalla
            total_distance = 0.05 + 0.05 + 0.03 + 0.05 + 0.15  # Basado en calculos.py
            x_screen = view_rect.x + 40 + (depth / total_distance) * 250
            
            # Escalar deflexión horizontal
            deflection_pixels = deflection * 1500  # Factor de escala para visualización
            y_screen = view_rect.y + 120 - deflection_pixels
            
            # Limitar a la vista
            x_screen = max(view_rect.x + 40, min(view_rect.x + 320, x_screen))
            y_screen = max(view_rect.y + 50, min(view_rect.y + 190, y_screen))
            
            points.append((int(x_screen), int(y_screen)))
        
        # Dibujar trayectoria
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['electron_trail'], False, points, 2)
        
        # Dibujar electrón en la posición final
        if points:
            pygame.draw.circle(surface, self.colors['electron'], points[-1], 4)

    def calculate_electron_position(self, V_acc, V_vert, V_horiz, t=None):
        """
        Calcula la posición del electrón en la pantalla usando calculos.py
        Devuelve coordenadas normalizadas (0-1) para la pantalla.
        """
        if V_acc <= 0:
            return 0.5, 0.5
            
        # Si no se especifica tiempo, usar el tiempo final (pantalla)
        if t is None:
            speed = ini_speed(V_acc)
            region_times = region_time(speed)
            t = region_times["reach_screen"]
        
        # Usar la función de calculos.py para obtener posiciones finales
        pos_data = get_position_by_time(V_acc, V_vert, V_horiz, t)
        
        # Deflexión vertical (de vista lateral)
        _, vertical_deflection = pos_data["lateral_view"]
        # Deflexión horizontal (de vista superior)  
        _, horizontal_deflection = pos_data["superior_view"]
        
        # Convertir deflexiones físicas a coordenadas de pantalla normalizadas
        # La pantalla tiene 25cm, centro en (0.5, 0.5)
        screen_size = 0.25  # 25 cm
        
        # Normalizar deflexiones (-1 a 1, luego 0 a 1)
        x_normalized = 0.5 + (horizontal_deflection / (screen_size / 2))
        y_normalized = 0.5 - (vertical_deflection / (screen_size / 2))  # Invertir Y
        
        # Limitar al rango válido
        x_normalized = max(0, min(1, x_normalized))
        y_normalized = max(0, min(1, y_normalized))
        
        return x_normalized, y_normalized

    def draw_screen_view(self, surface, persistence_time=1.0):
        """Dibuja la vista frontal de la pantalla del CRT"""
        view_rect = self.screen_view

        # Fondo negro de la pantalla del CRT
        pygame.draw.rect(surface, (0, 0, 0), view_rect)
        pygame.draw.rect(surface, self.colors['border'], view_rect, 3)

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

    def add_screen_point(self, normalized_x, normalized_y, brightness=1.0):
        """Añade un punto a la pantalla con coordenadas normalizadas (0-1)"""
        # Asegurar que las coordenadas están en el rango válido
        normalized_x = max(0, min(1, normalized_x))
        normalized_y = max(0, min(1, normalized_y))
        
        current_time = time.time()
        self.screen_persistence.append(((normalized_x, normalized_y), current_time, brightness))

    def clear_screen_persistence(self):
        """Limpia todos los puntos persistentes de la pantalla"""
        self.screen_persistence.clear()

    def draw_info_panel(self, surface, V_acc, V_vert, V_horiz, mode_text="Manual"):
        """Dibuja panel de información con valores actuales y datos físicos calculados"""
        info_x = 50
        info_y = 300
        
        # Calcular algunos valores físicos usando calculos.py
        if V_acc > 0:
            speed = ini_speed(V_acc)
            speed_ms = speed / 1000  # Convertir a km/s para legibilidad
            
            region_times = region_time(speed)
            total_time = region_times["reach_screen"] * 1e9  # Convertir a nanosegundos
        else:
            speed_ms = 0
            total_time = 0
        
        info_texts = [
            f"Modo: {mode_text}",
            f"V_aceleración: {V_acc:.0f} V",
            f"V_vertical: {V_vert:.0f} V", 
            f"V_horizontal: {V_horiz:.0f} V",
            f"Velocidad e⁻: {speed_ms:.1f} km/s",
            f"Tiempo total: {total_time:.1f} ns"
        ]
        
        for i, text in enumerate(info_texts):
            rendered_text = self.font.render(text, True, self.colors['text'])
            surface.blit(rendered_text, (info_x, info_y + i * 25))

    def generate_lissajous_point(self, t, freq_v, freq_h, phase_v=0, phase_h=0, amplitude=500):
        """Genera un punto de las Figuras de Lissajous"""
        # Señales sinusoidales para las placas
        V_vert = amplitude * math.sin(2 * math.pi * freq_v * t + phase_v)
        V_horiz = amplitude * math.sin(2 * math.pi * freq_h * t + phase_h)
        
        return V_vert, V_horiz

    def update_lissajous_animation(self, freq_v, freq_h, phase_v=0, phase_h=0, dt=0.016):
        """Actualiza la animación de las Figuras de Lissajous usando cálculos físicos"""
        if not hasattr(self, 'lissajous_time'):
            self.lissajous_time = 0
        
        self.lissajous_time += dt
        
        # Generar voltajes sinusoidales
        V_vert, V_horiz = self.generate_lissajous_point(
            self.lissajous_time, freq_v, freq_h, phase_v, phase_h
        )
        
        # Calcular posición en pantalla usando calculos.py
        x_pos, y_pos = self.calculate_electron_position(1000, V_vert, V_horiz)
        
        # Añadir punto a la pantalla
        self.add_screen_point(x_pos, y_pos, brightness=0.8)
        
        return V_vert, V_horiz

    def simulate_manual_mode(self, V_acc, V_vert, V_horiz):
        """Simula el modo manual usando cálculos físicos de calculos.py"""
        x_pos, y_pos = self.calculate_electron_position(V_acc, V_vert, V_horiz)
        
        # En modo manual, solo mostrar el punto actual
        self.clear_screen_persistence()
        self.add_screen_point(x_pos, y_pos, brightness=1.0)

    def simulate_lissajous_mode(self, freq_v, freq_h, phase_v=0, phase_h=0):
        """Simula el modo Lissajous con señales sinusoidales usando cálculos físicos"""
        return self.update_lissajous_animation(freq_v, freq_h, phase_v, phase_h)

    def draw_all_views(self, surface, V_acc=1000, V_vert=0, V_horiz=0, 
                        persistence_time=1.0, mode_text="Manual"):
        """Función principal que dibuja todas las vistas del CRT"""
        # Limpiar fondo
        surface.fill((255, 255, 255))
        
        # Dibujar las tres vistas usando cálculos físicos
        self.draw_lateral_view(surface, V_acc, V_vert)
        self.draw_top_view(surface, V_acc, V_horiz)
        self.draw_screen_view(surface, persistence_time)
        
        # Panel de información con datos físicos calculados
        self.draw_info_panel(surface, V_acc, V_vert, V_horiz, mode_text)
        
        # Instrucciones para el usuario
        instructions = [
            "Controles:",
            "- Ajustar voltajes con sliders",
            "- Cambiar modo para Lissajous",
            "- Tiempo de persistencia",
            "- Cálculos físicos reales"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.colors['text'])
            surface.blit(text, (50, 520 + i * 20))