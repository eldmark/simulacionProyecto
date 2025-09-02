import pygame
from pygame.locals import *
from slider import Slider
from visualization import CRTVisualizer

# Inicializar modo global
mode = False

# Variables globales para los controles
V_acc = 1000
V_vert = 0
V_horiz = 0
persistence = 1.0
freq_v = 1.0
freq_h = 1.0

sliders = []

def draw_ui(screen, color_mode, xpos=50, ypos=350):
    """Dibuja la interfaz de usuario con todos los controles."""
    # Dibujar sliders
    for slider in sliders:
        slider.draw(screen, title_font_size=30, value_font_size=30, title_offset_y=70, value_offset_y=40, line_thickness=8, handle_radius=20)
    
    # Dibujar botón de modo
    font = pygame.font.SysFont(None, 30)
    if not mode:
        mode_text = font.render(f"Modo: Manual", True, color_mode[0])
    else:
        mode_text = font.render(f"Modo: Toggle", True, color_mode[0])
    screen.blit(mode_text, (50, 350))
    
    # Aquí están las coordenadas del botón
    mode_button = pygame.Rect(ypos, xpos, 170, 40)
    pygame.draw.rect(screen, color_mode[1], mode_button, 2)
    
    # Cambiar de modo
    button_text = font.render("Cambiar Modo", True, color_mode[0])
    screen.blit(button_text, (60, 390))
    
    return mode_button

def handle_ui_events(event, mode_button):
    """Maneja los eventos de la interfaz de usuario."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, mode

    for slider in sliders:
        if slider.handle_event(event):
            # Actualizar variables globales según el slider
            slider_name = slider.label.split(":")[0].lower().replace(" ", "_")
            if slider_name == "v_aceleración":
                V_acc = slider.value
            elif slider_name == "v_vertical":
                V_vert = slider.value
            elif slider_name == "v_horizontal":
                V_horiz = slider.value
            elif slider_name == "persistencia":
                persistence = slider.value
            elif slider_name == "frecuencia_vertical":
                freq_v = slider.value
            elif slider_name == "frecuencia_horizontal":
                freq_h = slider.value
    
    # Cambiar modo si se hace clic en el botón
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        if mode_button.collidepoint(event.pos):
            global mode
            mode = not mode
            return
    
    return None

def main():
    global V_acc, V_vert, V_horiz, persistence, mode, freq_v, freq_h, sliders

    # Inicializar pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
    
    # Inicializar visualizador CRT
    visualizer = CRTVisualizer()
    
    # Configurar colores
    color_mode = [(0, 0, 0), (0, 120, 255)]
    
    # Crear sliders
    sliders.clear()
    sliders.append(Slider(50, 80, 500, 40, 500, 2000, V_acc, title="V Aceleración", unit="V", toggle=mode))
    sliders.append(Slider(50, 150, 500, 40, -1000, 1000, V_vert, title="V Vertical", unit="V", toggle=mode))
    sliders.append(Slider(50, 220, 500, 40, -1000, 1000, V_horiz, title="V Horizontal", unit="V", toggle=mode))
    sliders.append(Slider(700, 80, 400, 40, 0.1, 5.0, persistence, title="Persistencia", unit="s", toggle=mode))
    sliders.append(Slider(700, 150, 400, 40, 0.1, 10.0, freq_v, title="Frecuencia Vertical", unit="Hz", toggle=mode))
    sliders.append(Slider(700, 220, 400, 40, 0.1, 10.0, freq_h, title="Frecuencia Horizontal", unit="Hz", toggle=mode))
    
    clock = pygame.time.Clock()
    running = True
    
    # Para el modo Lissajous
    lissajous_time = 0
    
    while running:
        screen.fill((255, 255, 255))
        
        # Dibujar UI y obtener el botón de modo
        mode_button = draw_ui(screen, color_mode)
        
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_ui_events(event, mode_button)
        
        # Actualizar estado de los sliders según el modo
        for slider in sliders:
            slider.set_disabled(mode)
        
        # Actualizar simulación según el modo
        if mode:  # Modo Lissajous
            # Actualizar tiempo para animación
            lissajous_time += 0.016  # Aproximadamente 60 FPS
            
            # Generar voltajes sinusoidales
            V_vert, V_horiz = visualizer.generate_lissajous_point(
                lissajous_time, freq_v, freq_h
            )
            
            # Calcular posición en pantalla
            x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz)
            
            # Añadir punto a la pantalla
            visualizer.add_screen_point(x_pos, y_pos, brightness=0.8)
        else:  # Modo manual
            # Calcular posición en pantalla basada en voltajes manuales
            x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz)
            
            # En modo manual, mostrar solo el punto actual
            visualizer.clear_screen_persistence()
            visualizer.add_screen_point(x_pos, y_pos, brightness=1.0)
        
        # Dibujar todas las vistas del CRT
        mode_text = "Lissajous" if mode else "Manual"
        visualizer.draw_all_views(screen, V_acc, V_vert, V_horiz, persistence, mode_text)
        
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()