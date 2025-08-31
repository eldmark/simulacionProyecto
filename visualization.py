import pygame
import math
from collections import deque
import time

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