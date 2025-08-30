import pygame
import numpy as np
import sys
from pygame.locals import *

# Inicialización de Pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de CRT - Física 3")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
GRAY = (150, 150, 150)
LIGHT_BLUE = (100, 100, 255)

# Constantes físicas (Persona 1)
e = 1.6e-19  # Carga del electrón (C)
m = 9.11e-31  # Masa del electrón (kg)
L = 0.02  # Longitud de las placas (m)
d = 0.005  # Separación entre placas (m)
D = 0.2  # Distancia desde placas a pantalla (m)
SCREEN_SIZE = 0.3  # Tamaño de la pantalla (m)

# Variables controlables por el usuario (Persona 3)
V_acc = 1000  # Voltaje de aceleración (V)
V_vert = 0    # Voltaje placas verticales (V)
V_horiz = 0   # Voltaje placas horizontales (V)
persistence = 100  # Tiempo de persistencia (frames)
mode = "manual"  # Modo: "manual" o "sinusoidal"
freq_v = 1.0  # Frecuencia vertical (Hz)
freq_h = 1.0  # Frecuencia horizontal (Hz)
phase_v = 0.0  # Fase vertical (rad)
phase_h = 0.0  # Fase horizontal (rad)

# Lista para almacenar puntos (Persona 2)
points = []

# =============================================================================
# PERSONA 1: CÁLCULOS FÍSICOS Y MATEMÁTICOS
# =============================================================================
def calculate_trajectory(V_acc, V_vert, V_horiz, t=0):
    """
    Calcula la posición de impacto del electrón en la pantalla
    basándose en los voltajes aplicados y el tiempo.
    """
    # En modo sinusoidal, ajustar voltajes según el tiempo
    if mode == "sinusoidal":
        V_vert = 50 * np.sin(2 * np.pi * freq_v * t + phase_v)
        V_horiz = 50 * np.sin(2 * np.pi * freq_h * t + phase_h)
    
    # Calcular velocidad inicial
    v0 = np.sqrt(2 * e * abs(V_acc) / m) * (1 if V_acc >= 0 else -1)
    
    if v0 == 0:
        return 0, 0
    
    # Calcular campos eléctricos
    E_vert = V_vert / d
    E_horiz = V_horiz / d
    
    # Aceleraciones
    a_vert = (e * E_vert) / m
    a_horiz = (e * E_horiz) / m
    
    # Tiempo dentro de las placas
    t_inside = L / v0
    
    # Desplazamiento dentro de las placas
    y_inside = 0.5 * a_vert * t_inside**2
    x_inside = 0.5 * a_horiz * t_inside**2
    
    # Velocidades al salir de las placas
    v_vert = a_vert * t_inside
    v_horiz = a_horiz * t_inside
    
    # Tiempo desde placas a pantalla
    t_to_screen = D / v0
    
    # Desplazamiento adicional
    y_additional = v_vert * t_to_screen
    x_additional = v_horiz * t_to_screen
    
    # Desplazamiento total
    y_total = y_inside + y_additional
    x_total = x_inside + x_additional
    
    # Ajustar a los límites de la pantalla
    y_total = max(-SCREEN_SIZE/2, min(SCREEN_SIZE/2, y_total))
    x_total = max(-SCREEN_SIZE/2, min(SCREEN_SIZE/2, x_total))
    
    return x_total, y_total

# =============================================================================
# PERSONA 2: VISUALIZACIÓN Y GRÁFICOS
# =============================================================================
def draw_crt(screen):
    """Dibuja el CRT con sus tres vistas."""
    # Vista frontal (pantalla donde impactan los electrones)
    front_rect = pygame.Rect(650, 50, 300, 300)
    pygame.draw.rect(screen, GRAY, front_rect, 2)
    
    # Dibujar puntos de impacto
    for point in points:
        x, y, age = point
        # Convertir coordenadas físicas a píxeles
        px = 800 + int(x * 300 / SCREEN_SIZE)
        py = 200 + int(y * 300 / SCREEN_SIZE)
        # La intensidad disminuye con la edad
        intensity = max(0, 255 * age / persistence)
        color = (intensity, intensity, intensity)
        pygame.draw.circle(screen, color, (px, py), 2)
    
    # Vista lateral (para ver deflexión vertical)
    pygame.draw.line(screen, WHITE, (100, 500), (300, 500), 2)  # Base
    pygame.draw.line(screen, WHITE, (200, 400), (200, 600), 2)  # Tubo
    pygame.draw.line(screen, RED, (200, 490), (200, 510), 4)  # Placas verticales
    
    # Vista superior (para ver deflexión horizontal)
    pygame.draw.line(screen, WHITE, (400, 500), (600, 500), 2)  # Base
    pygame.draw.circle(screen, WHITE, (500, 500), 80, 2)  # Tubo (vista superior)
    pygame.draw.line(screen, BLUE, (490, 500), (510, 500), 4)  # Placas horizontales

def update_points(x, y):
    """Actualiza la lista de puntos con el nuevo impacto y maneja la persistencia."""
    points.append((x, y, persistence))
    
    # Envejecer todos los puntos y eliminar los demasiado viejos
    for i in range(len(points)):
        x, y, age = points[i]
        points[i] = (x, y, age-1)
    
    # Eliminar puntos con persistencia agotada
    points[:] = [p for p in points if p[2] > 0]

# =============================================================================
# PERSONA 3: INTERFAZ DE USUARIO Y CONTROLES
# =============================================================================
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.label = label
        self.dragging = False
        
    def draw(self, screen):
        # Dibujar la barra del slider
        pygame.draw.rect(screen, GRAY, self.rect, 2)
        
        # Calcular posición del indicador
        pos_x = self.rect.x + int((self.value - self.min) / (self.max - self.min) * self.rect.width)
        
        # Dibujar indicador
        pygame.draw.circle(screen, WHITE, (pos_x, self.rect.y + self.rect.height//2), 8)
        
        # Dibujar texto
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{self.label}: {self.value:.1f}", True, WHITE)
        screen.blit(text, (self.rect.x, self.rect.y - 25))
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == MOUSEMOTION and self.dragging:
            # Calcular nuevo valor basado en la posición del ratón
            relative_x = event.pos[0] - self.rect.x
            self.value = self.min + (relative_x / self.rect.width) * (self.max - self.min)
            self.value = max(self.min, min(self.max, self.value))
            return True
            
        return False

# Crear sliders
sliders = [
    Slider(50, 50, 200, 20, 500, 2000, V_acc, "Voltaje Aceleración (V)"),
    Slider(50, 100, 200, 20, -100, 100, V_vert, "Voltaje Vertical (V)"),
    Slider(50, 150, 200, 20, -100, 100, V_horiz, "Voltaje Horizontal (V)"),
    Slider(50, 200, 200, 20, 10, 300, persistence, "Persistencia"),
    Slider(50, 250, 200, 20, 0.1, 5, freq_v, "Frecuencia Vertical (Hz)"),
    Slider(50, 300, 200, 20, 0.1, 5, freq_h, "Frecuencia Horizontal (Hz)"),
]

def draw_ui(screen):
    """Dibuja la interfaz de usuario con todos los controles."""
    # Dibujar sliders
    for slider in sliders:
        slider.draw(screen)
    
    # Dibujar botón de modo
    font = pygame.font.SysFont(None, 30)
    mode_text = font.render(f"Modo: {mode.capitalize()}", True, WHITE)
    screen.blit(mode_text, (50, 350))
    
    mode_button = pygame.Rect(50, 380, 150, 40)
    pygame.draw.rect(screen, LIGHT_BLUE, mode_button, 2)
    
    button_text = font.render("Cambiar Modo", True, WHITE)
    screen.blit(button_text, (60, 390))
    
    return mode_button

def handle_ui_events(event, mode_button):
    """Maneja los eventos de la interfaz de usuario."""
    # Actualizar sliders
    for slider in sliders:
        if slider.handle_event(event):
            # Actualizar variables globales
            globals()[slider.label.split(":")[0].lower().replace(" ", "_")] = slider.value
    
    # Cambiar modo si se hace clic en el botón
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        if mode_button.collidepoint(event.pos):
            return "toggle_mode"
    
    return None

# =============================================================================
# PERSONA 4: INTEGRACIÓN Y GESTIÓN GENERAL
# =============================================================================
def main():
    global V_acc, V_vert, V_horiz, persistence, mode, freq_v, freq_h
    
    clock = pygame.time.Clock()
    time_elapsed = 0.0
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time en segundos
        time_elapsed += dt
        
        # Manejar eventos
        mode_button = None
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            mode_button = draw_ui(screen)  # Necesario para obtener la posición del botón
            result = handle_ui_events(event, mode_button)
            
            if result == "toggle_mode":
                mode = "sinusoidal" if mode == "manual" else "manual"
        
        # Actualizar sliders con valores globales
        sliders[0].value = V_acc
        sliders[1].value = V_vert
        sliders[2].value = V_horiz
        sliders[3].value = persistence
        sliders[4].value = freq_v
        sliders[5].value = freq_h
        
        # Calcular la posición del electrón
        x, y = calculate_trajectory(V_acc, V_vert, V_horiz, time_elapsed)
        
        # Actualizar puntos
        update_points(x, y)
        
        # Dibujar
        screen.fill(BLACK)
        draw_crt(screen)
        draw_ui(screen)
        
        # Actualizar pantalla
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()