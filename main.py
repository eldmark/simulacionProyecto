import pygame
from pygame.locals import *
from slider import Slider
from visualization import CRTVisualizer
import numpy as np

# Inicializar modo global
mode = False

# Variables globales para los controles
V_acc = 1000
V_vert = 0
V_horiz = 0
persistence = 1.0
freq_v = 1.0
freq_h = 1.0
phase_v = 0
phase_h = 0

sliders = []
buttons = []

def draw_ui(screen):
    """Dibuja la interfaz de usuario con todos los controles."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, mode
    
    # Fondo del panel de control mejorado
    panel_rect = pygame.Rect(10, 10, 370, 670)
    
    # Sombra del panel
    shadow_rect = pygame.Rect(12, 12, 370, 670)
    pygame.draw.rect(screen, (200, 200, 210), shadow_rect, border_radius=8)
    
    # Panel principal con gradiente simulado
    pygame.draw.rect(screen, (245, 248, 252), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (180, 190, 200), panel_rect, 2, border_radius=8)
    
    # Barra superior del panel
    header_rect = pygame.Rect(10, 10, 370, 50)
    pygame.draw.rect(screen, (65, 105, 225), header_rect, border_top_left_radius=8, border_top_right_radius=8)
    
    # Título del panel
    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    title = font_title.render("CONTROLES CRT", True, (255, 255, 255))
    title_x = header_rect.centerx - title.get_width() // 2
    screen.blit(title, (title_x, 25))
    
    # Dibujar sliders
    for slider in sliders:
        slider.draw(screen, title_font_size=18, value_font_size=16, 
                   title_offset_y=22, value_offset_y=12, line_thickness=4, handle_radius=8)
    
    # Sección de botones 
    buttons_y = 400
    font_section = pygame.font.SysFont('Arial', 20, bold=True)
    section_title = font_section.render("ACCIONES", True, (60, 70, 80))
    screen.blit(section_title, (30, buttons_y - 25))
    
    # Dibujar botones
    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
    for i, button in enumerate(buttons):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button['rect'].collidepoint(mouse_pos)
        
        # Colores según el tipo de botón y estado
        if button['id'] == 'mode':
            base_color = (46, 125, 50) if not mode else (255, 152, 0)
            hover_color = (56, 142, 60) if not mode else (255, 167, 38)
        else:  # reset button
            base_color = (211, 47, 47)
            hover_color = (229, 57, 53)
        
        btn_color = hover_color if is_hovered else base_color
        
        # Sombra del botón
        shadow_rect = pygame.Rect(button['rect'].x + 2, button['rect'].y + 2, 
                                button['rect'].width, button['rect'].height)
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=6)
        
        # Botón principal
        pygame.draw.rect(screen, btn_color, button['rect'], border_radius=6)
        
        # Borde del botón
        border_color = (255, 255, 255, 100) if is_hovered else (0, 0, 0, 50)
        pygame.draw.rect(screen, border_color, button['rect'], 2, border_radius=6)
        
        # Texto centrado
        text_rect = button['text'].get_rect(center=button['rect'].center)
        screen.blit(button['text'], text_rect)
    
    # Información de estado 
    status_y = 480
    font_section = pygame.font.SysFont('Arial', 20, bold=True)
    section_title = font_section.render("ESTADO", True, (60, 70, 80))
    screen.blit(section_title, (30, status_y))
    
    # Estado del modo con indicador visual
    mode_status = "LISSAJOUS" if mode else "MANUAL"
    mode_color = (46, 125, 50) if mode else (211, 47, 47)
    
    font_status = pygame.font.SysFont('Arial', 18, bold=True)
    mode_text = font_status.render(f"MODO: {mode_status}", True, mode_color)
    screen.blit(mode_text, (30, status_y + 25))
    
    # Valores actuales en una caja - ACTUALIZAR CON LAS VARIABLES GLOBALES
    values_rect = pygame.Rect(25, status_y + 50, 330, 120)  # Aumentar altura
    pygame.draw.rect(screen, (240, 245, 250), values_rect, border_radius=6)
    pygame.draw.rect(screen, (200, 210, 220), values_rect, 1, border_radius=6)
    
    font_values = pygame.font.SysFont('Arial', 14)
    values_text = [
        f"Aceleración: {V_acc:.0f} V",
        f"Vertical: {V_vert:.1f} V",
        f"Horizontal: {V_horiz:.1f} V", 
        f"Persistencia: {persistence:.1f} s"
    ]
    
    for i, text in enumerate(values_text):
        value = font_values.render(text, True, (60, 70, 80))
        screen.blit(value, (35, status_y + 65 + i * 20))


def draw_voltage_displays(screen, V_vert, V_horiz):
    """Dibuja displays de voltaje para las vistas con mejor diseño."""
    font = pygame.font.SysFont('Arial', 20, bold=True)
    small_font = pygame.font.SysFont('Arial', 14, bold=True)
    
    # Posiciones ajustadas para las vistas
    displays = [
        {"rect": pygame.Rect(480, 310, 200, 55), "title": "Vista Lateral", "value": V_vert, "color": (46, 125, 50)},
        {"rect": pygame.Rect(880, 310, 200, 55), "title": "Vista Superior", "value": V_horiz, "color": (255, 152, 0)}
    ]
    
    for display in displays:
        rect = display["rect"]
        
        # Sombra
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 30), shadow_rect, border_radius=8)
        
        # Fondo del display
        pygame.draw.rect(screen, (245, 248, 252), rect, border_radius=8)
        pygame.draw.rect(screen, display["color"], rect, 3, border_radius=8)
        
        # Tí­tulo
        title = small_font.render(display["title"], True, (60, 70, 80))
        title_rect = title.get_rect(centerx=rect.centerx, y=rect.y + 8)
        screen.blit(title, title_rect)
        
        # Valor
        value_text = f"{display['value']:.1f} V"
        value = font.render(value_text, True, display["color"])
        value_rect = value.get_rect(centerx=rect.centerx, y=rect.y + 26)
        screen.blit(value, value_rect)

def draw_view_labels(screen):
    """Dibuja etiquetas mejoradas para las vistas."""
    font = pygame.font.SysFont('Arial', 16, bold=True)
    
    # Etiquetas con fondo
    labels = [
        {"text": "Vista Lateral", "pos": (470, 25), "color": (46, 125, 50)},
        {"text": "Vista Superior", "pos": (720, 25), "color": (255, 152, 0)},
        {"text": "Pantalla del CRT", "pos": (560, 420), "color": (65, 105, 225)}
    ]
    
    for label in labels:
        text = font.render(label["text"], True, label["color"])
        
        # Fondo semi-transparente
        bg_rect = pygame.Rect(label["pos"][0] - 5, label["pos"][1] - 2, 
                             text.get_width() + 10, text.get_height() + 4)
        pygame.draw.rect(screen, (255, 255, 255, 200), bg_rect, border_radius=4)
        pygame.draw.rect(screen, label["color"], bg_rect, 2, border_radius=4)
        
        screen.blit(text, label["pos"])
        
def reset_values():
    """Resetea todos los valores a sus valores por defecto."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, phase_v, phase_h, mode
    
    # Valores por defecto
    V_acc = 1000
    V_vert = 0
    V_horiz = 0
    persistence = 1.0
    freq_v = 1.0
    freq_h = 1.0
    phase_v = 0
    phase_h = 0
    mode = False
    
    # Actualizar sliders
    for slider in sliders:
        if "Aceleración" in slider.title:
            slider.value = V_acc
        elif "Vertical" in slider.title:
            slider.value = V_vert
        elif "Horizontal" in slider.title:
            slider.value = V_horiz
        elif "Persistencia" in slider.title:
            slider.value = persistence
        elif "Frecuencia Vertical" in slider.title:
            slider.value = freq_v
        elif "Frecuencia Horizontal" in slider.title:
            slider.value = freq_h
    
    # Actualizar botón de modo
    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
    for button in buttons:
        if button['id'] == 'mode':
            button_text = "Modo Lissajous" if not mode else "Modo Manual"
            button['text'] = font_btn.render(button_text, True, (255, 255, 255))
    
    # Resetear tiempos y limpiar pantalla
    if hasattr(visualizer, 'manual_time'):
        visualizer.manual_time = 0
    if hasattr(visualizer, 'lissajous_time'):
        visualizer.lissajous_time = 0
    visualizer.clear_screen_persistence()

def handle_ui_events(event):
    """Maneja los eventos de la interfaz de usuario."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, mode
    
    slider_changed = False
    
    for slider in sliders:
        if slider.handle_event(event):
            slider_changed = True
            if "Aceleración" in slider.title:
                V_acc = slider.value
            elif "Vertical" in slider.title:
                V_vert = slider.value
            elif "Horizontal" in slider.title:
                V_horiz = slider.value
            elif "Persistencia" in slider.title:
                persistence = slider.value
            elif "Frecuencia Vertical" in slider.title:
                freq_v = slider.value
            elif "Frecuencia Horizontal" in slider.title:
                freq_h = slider.value
    
    # Forzar reset del tiempo manual si se movió un slider relevante
    if slider_changed and not mode:
        if hasattr(visualizer, 'manual_time'):
            visualizer.manual_time = 0
    
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        for button in buttons:
            if button['rect'].collidepoint(event.pos):
                if button['id'] == 'mode':
                    mode = not mode
                    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
                    button_text = "Modo Manual" if mode else "Modo Lissajous"
                    button['text'] = font_btn.render(button_text, True, (255, 255, 255))
                    
                    for slider in sliders:
                        if "Vertical" in slider.title or "Horizontal" in slider.title:
                            slider.set_disabled(mode)
                    
                    # Resetear tiempos al cambiar modo
                    if hasattr(visualizer, 'manual_time'):
                        visualizer.manual_time = 0
                    if hasattr(visualizer, 'lissajous_time'):
                        visualizer.lissajous_time = 0
                    visualizer.clear_screen_persistence()
                    
                elif button['id'] == 'reset':
                    reset_values()
                    
                return True
    
    if event.type == KEYDOWN:
        if event.key == K_SPACE:
            global paused
            paused = not paused
        elif event.key == K_r:
            reset_values()
    
    return False

def main():
    global V_acc, V_vert, V_horiz, persistence, mode, freq_v, freq_h, sliders, buttons, visualizer, paused

    # Inicializar pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
    
    # Inicializar visualizador CRT
    visualizer = CRTVisualizer()
    
    # INICIALIZAR TIEMPOS
    visualizer.manual_time = 0
    visualizer.lissajous_time = 0
    
    # Ajustar las posiciones de las vistas
    visualizer.lateral_view = pygame.Rect(400, 50, 340, 230)  
    visualizer.top_view = pygame.Rect(800, 50, 340, 230)       
    visualizer.screen_view = pygame.Rect(650, 420, 250, 250) 
    
    # Crear sliders con mejor espaciado para evitar superposición
    sliders.clear()
    y_start = 85
    spacing = 44 
    
    sliders.append(Slider(30, y_start, 310, 15, 500, 2000, V_acc, title="V Aceleración", unit="V"))
    sliders.append(Slider(30, y_start + spacing, 310, 15, -1000, 1000, V_vert, title="V Vertical", unit="V"))
    sliders.append(Slider(30, y_start + spacing*2, 310, 15, -1000, 1000, V_horiz, title="V Horizontal", unit="V"))
    sliders.append(Slider(30, y_start + spacing*3, 310, 15, 0.1, 5.0, persistence, title="Persistencia", unit="s"))
    sliders.append(Slider(30, y_start + spacing*4, 310, 15, 0.1, 10.0, freq_v, title="Frecuencia Vertical", unit="Hz"))
    sliders.append(Slider(30, y_start + spacing*5, 310, 15, 0.1, 10.0, freq_h, title="Frecuencia Horizontal", unit="Hz"))
    
    # Crear botones
    buttons.clear()
    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
    
    button_text = "Modo Lissajous" if not mode else "Modo Manual"
    buttons.append({
        'id': 'mode',
        'rect': pygame.Rect(30, 420, 140, 38),  # Movido mÃ¡s abajo
        'text': font_btn.render(button_text, True, (255, 255, 255))
    })
    
    buttons.append({
        'id': 'reset',
        'rect': pygame.Rect(180, 420, 140, 38),
        'text': font_btn.render("Reset Pantalla", True, (255, 255, 255))
    })
    
    clock = pygame.time.Clock()
    running = True
    paused = False
    
    # Para el modo Lissajous
    lissajous_time = 0
    
    simulation_time = 0
    
    while running:
        # Fondo con gradiente simulado
        screen.fill((235, 240, 245))
        
        # Dibujar etiquetas de las vistas
        draw_view_labels(screen)
        
        # Dibujar las vistas del CRT
        mode_text = "Lissajous" if mode else "Manual"
        visualizer.draw_all_views(screen, V_acc, V_vert, V_horiz, persistence, mode_text)
        
        # Dibujar displays de voltaje
        draw_voltage_displays(screen, V_vert, V_horiz)
        
        # Dibujar la interfaz de usuario
        draw_ui(screen)
        
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_ui_events(event)
            
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                paused = not paused
            elif event.key == K_r:  # Tecla R para reset
                reset_values()
        
        # Actualizar estado de los sliders según el modo
        simulation_time += 0.016 if not paused else 0
        if not paused:
            if mode:  # Modo Lissajous
                lissajous_time += 0.016
                V_vert_liss, V_horiz_liss = visualizer.generate_lissajous_point(
                    lissajous_time, freq_v, freq_h
                )
                
                # Actualizar también las variables globales para la UI
                V_vert = V_vert_liss
                V_horiz = V_horiz_liss
                
                # Actualizar visualmente los sliders
                for slider in sliders:
                    if "Vertical" in slider.title:
                        slider.value = V_vert
                    elif "Horizontal" in slider.title:
                        slider.value = V_horiz
                
                x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz, simulation_time)
                visualizer.add_screen_point(x_pos, y_pos, brightness=0.8)
                
            else:  # Modo manual
                # RESETEAR el tiempo cuando se mueven los sliders para ver cambios inmediatos
                slider_moved = any(slider.dragging for slider in sliders if "Vertical" in slider.title or "Horizontal" in slider.title)
                
                if not hasattr(visualizer, 'manual_time') or slider_moved:
                    visualizer.manual_time = 0
                    # Limpiar pantalla para ver el nuevo punto inmediatamente
                    visualizer.clear_screen_persistence()
                
                visualizer.manual_time += 0.016 if not paused else 0
                    
                # Calcular posición con los valores ACTUALES de los sliders
                x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz, visualizer.manual_time)
                visualizer.add_screen_point(x_pos, y_pos, brightness=1.0)
                
        # Indicador de pausa mejorado y reposicionado
        if paused:
            font = pygame.font.SysFont('Arial', 28, bold=True)
            pause_text = font.render("PAUSADO", True, (211, 47, 47))
            
            # Fondo semi-transparente para el texto
            text_rect = pause_text.get_rect(center=(600, 25))
            bg_rect = pygame.Rect(text_rect.x - 8, text_rect.y - 4, 
                                text_rect.width + 16, text_rect.height + 8)
            pygame.draw.rect(screen, (255, 255, 255, 200), bg_rect, border_radius=6)
            pygame.draw.rect(screen, (211, 47, 47), bg_rect, 2, border_radius=6)
            
            screen.blit(pause_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()