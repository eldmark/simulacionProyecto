import pygame
from pygame.locals import *
from slider import Slider
from visualization import CRTVisualizer
from grid_component import FrequencyGrid, LissajousPreview
import numpy as np
import math

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
frequency_grid = None
lissajous_preview = None

def draw_ui(screen):
    """Dibuja la interfaz de usuario con todos los controles."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, mode
    
    # Fondo del panel de control mejorado
    panel_rect = pygame.Rect(10, 10, 370, 800)  # Aumentar altura para el grid
    
    # Sombra del panel
    shadow_rect = pygame.Rect(12, 12, 370, 800)
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
    buttons_y = 350  # Mover botones más arriba para hacer espacio al grid
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
    status_y = 430
    font_section = pygame.font.SysFont('Arial', 20, bold=True)
    section_title = font_section.render("ESTADO", True, (60, 70, 80))
    screen.blit(section_title, (30, status_y))
    
    # Estado del modo con indicador visual
    mode_status = "LISSAJOUS" if mode else "MANUAL"
    mode_color = (46, 125, 50) if mode else (211, 47, 47)
    
    font_status = pygame.font.SysFont('Arial', 18, bold=True)
    mode_text = font_status.render(f"MODO: {mode_status}", True, mode_color)
    screen.blit(mode_text, (30, status_y + 25))
    
    # Valores actuales en una caja
    values_rect = pygame.Rect(25, status_y + 50, 330, 140)
    pygame.draw.rect(screen, (240, 245, 250), values_rect, border_radius=6)
    pygame.draw.rect(screen, (200, 210, 220), values_rect, 1, border_radius=6)
    
    font_values = pygame.font.SysFont('Arial', 14)
    values_text = [
        f"Aceleración: {V_acc:.0f} V",
        f"Vertical: {V_vert:.1f} V",
        f"Horizontal: {V_horiz:.1f} V", 
        f"Persistencia: {persistence:.1f} s",
        f"Freq V: {freq_v:.1f} Hz",
        f"Freq H: {freq_h:.1f} Hz"
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
        
        # Título
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
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, phase_v, phase_h, mode, simulation_time
    
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
    simulation_time = 0  # Reset simulation time
    
    # Actualizar sliders a los valores por defecto
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
    
    # Actualizar texto del botón de modo
    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
    for button in buttons:
        if button['id'] == 'mode':
            button_text = "Modo Lissajous" if not mode else "Modo Manual"
            button['text'] = font_btn.render(button_text, True, (255, 255, 255))
    
    # Limpiar pantalla del visualizador
    visualizer.clear_all_points()
    
    # Reset grid selection
    if frequency_grid:
        frequency_grid.selected_combo = None

def handle_ui_events(event):
    """Maneja los eventos de la interfaz de usuario."""
    global V_acc, V_vert, V_horiz, persistence, freq_v, freq_h, mode
    
    # Manejar eventos del grid de frecuencias
    if frequency_grid and mode:  # Solo activo en modo Lissajous
        selected_combo = frequency_grid.handle_event(event)
        if selected_combo:
            freq_h = selected_combo['freq_h']
            freq_v = selected_combo['freq_v']
            
            # Actualizar sliders de frecuencia
            for slider in sliders:
                if "Frecuencia Horizontal" in slider.title:
                    slider.value = freq_h
                elif "Frecuencia Vertical" in slider.title:
                    slider.value = freq_v
            
            # Actualizar preview
            if lissajous_preview:
                lissajous_preview.update_preview(freq_h, freq_v, phase_h, phase_v)
    
    for slider in sliders:
        if slider.handle_event(event):
            slider_name = slider.title.split(":")[0].lower().replace(" ", "_")
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
                if lissajous_preview:
                    lissajous_preview.update_preview(freq_h, freq_v, phase_h, phase_v)
            elif slider_name == "frecuencia_horizontal":
                freq_h = slider.value
                if lissajous_preview:
                    lissajous_preview.update_preview(freq_h, freq_v, phase_h, phase_v)
    
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        for button in buttons:
            if button['rect'].collidepoint(event.pos):
                if button['id'] == 'mode':
                    mode = not mode
                    # Actualizar texto del botón
                    font_btn = pygame.font.SysFont('Arial', 16, bold=True)
                    button_text = "Modo Manual" if mode else "Modo Lissajous"
                    button['text'] = font_btn.render(button_text, True, (255, 255, 255))
                    
                    # Actualizar estado de sliders según el modo
                    for slider in sliders:
                        if slider.title.startswith(("V Vertical", "V Horizontal")):
                            slider.set_disabled(mode)
                        elif slider.title.startswith("Frecuencia"):
                            slider.set_disabled(not mode)
                            
                elif button['id'] == 'reset':
                    reset_values()
                    
                return True
    
    if event.type == KEYDOWN and event.key == K_SPACE:
        global paused
        paused = not paused
    
    return False

def main():
    global V_acc, V_vert, V_horiz, persistence, mode, freq_v, freq_h, sliders, buttons, visualizer, paused
    global frequency_grid, lissajous_preview, simulation_time

    # Inicializar pygame
    pygame.init()
    screen = pygame.display.set_mode((1400, 900))
    pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
    
    # Inicializar visualizador CRT
    visualizer = CRTVisualizer()
    
    # Ajustar las posiciones de las vistas
    visualizer.lateral_view = pygame.Rect(400, 50, 340, 230)  
    visualizer.top_view = pygame.Rect(800, 50, 340, 230)       
    visualizer.screen_view = pygame.Rect(650, 420, 250, 250)
    
    # Inicializar componentes de frecuencia
    frequency_grid = FrequencyGrid(1000, 400, 350, 250, "Ratios de Frecuencia")
    lissajous_preview = LissajousPreview(1000, 680, 150)
    
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
        'rect': pygame.Rect(30, 370, 140, 38),
        'text': font_btn.render(button_text, True, (255, 255, 255))
    })
    
    buttons.append({
        'id': 'reset',
        'rect': pygame.Rect(180, 370, 140, 38),
        'text': font_btn.render("Reset", True, (255, 255, 255))
    })
    
    # Configurar estado inicial de sliders
    for slider in sliders:
        if slider.title.startswith("Frecuencia"):
            slider.set_disabled(True)  # Inicialmente deshabilitados
    
    clock = pygame.time.Clock()
    running = True
    paused = False
    
    # FIXED: Initialize simulation time properly
    simulation_time = 0.0
    last_manual_update = 0.0
    
    # Actualizar preview inicial
    lissajous_preview.update_preview(freq_h, freq_v, phase_h, phase_v)
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time en segundos
        
        # Fondo con gradiente simulado
        screen.fill((235, 240, 245))
        
        # Dibujar etiquetas de las vistas
        draw_view_labels(screen)
        
        # FIXED: Set visualizer mode properly
        mode_text = "Lissajous" if mode else "Manual"
        visualizer.set_mode(mode_text)
        
        # Dibujar las vistas del CRT
        visualizer.draw_all_views(screen, V_acc, V_vert, V_horiz, persistence, mode_text)
        
        # Dibujar displays de voltaje
        draw_voltage_displays(screen, V_vert, V_horiz)
        
        # Dibujar la interfaz de usuario
        draw_ui(screen)
        
        # Dibujar grid de frecuencias y preview solo en modo Lissajous
        if mode:
            frequency_grid.draw(screen)
            lissajous_preview.draw(screen)
        
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused
                elif event.key == K_r:  # Tecla R para reset
                    reset_values()
            else:
                handle_ui_events(event)
        
        # Actualizar estado de los sliders según el modo
        for slider in sliders:
            if "Aceleración" in slider.title:
                V_acc = slider.value
            elif "Vertical" in slider.title and not mode:
                V_vert = slider.value
            elif "Horizontal" in slider.title and not mode:
                V_horiz = slider.value
            elif "Persistencia" in slider.title:
                persistence = slider.value
            elif "Frecuencia Vertical" in slider.title and mode:
                freq_v = slider.value
            elif "Frecuencia Horizontal" in slider.title and mode:
                freq_h = slider.value
        
        # FIXED: Proper simulation updates
        if not paused:
            simulation_time += dt
            
            if mode:  # Modo Lissajous
                # Generate sinusoidal voltages with proper amplitude
                amplitude = 800  # Maximum voltage for plates
                
                V_vert = amplitude * math.sin(2 * math.pi * freq_v * simulation_time + phase_v)
                V_horiz = amplitude * math.sin(2 * math.pi * freq_h * simulation_time + phase_h)
                
                # Calculate electron position at current time
                x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz, 0)
                
                # FIXED: Add points more frequently for smoother curves
                if simulation_time - getattr(visualizer, 'last_lissajous_point_time', 0) > 0.01:  # Every 10ms
                    visualizer.add_screen_point(x_pos, y_pos, brightness=0.9, mode="lissajous")
                    visualizer.last_lissajous_point_time = simulation_time
                
            else:  # Modo manual
                # Calculate position based on current voltage settings
                x_pos, y_pos = visualizer.calculate_electron_position(V_acc, V_vert, V_horiz, 0)
                
                # FIXED: Add points when voltages change or periodically
                if (simulation_time - last_manual_update > 0.05 or  # Every 50ms
                    not hasattr(visualizer, 'last_manual_pos') or
                    abs(x_pos - getattr(visualizer, 'last_manual_pos', (0,0))[0]) > 0.001 or
                    abs(y_pos - getattr(visualizer, 'last_manual_pos', (0,0))[1]) > 0.001):
                    
                    visualizer.add_screen_point(x_pos, y_pos, brightness=1.0, mode="manual")
                    visualizer.last_manual_pos = (x_pos, y_pos)
                    last_manual_update = simulation_time
        
        # Indicador de pausa mejorado
        if paused:
            font = pygame.font.SysFont('Arial', 28, bold=True)
            pause_text = font.render("PAUSADO - Presiona ESPACIO para continuar", True, (211, 47, 47))
            
            # Fondo semi-transparente para el texto
            text_rect = pause_text.get_rect(center=(700, 25))
            bg_rect = pygame.Rect(text_rect.x - 8, text_rect.y - 4, 
                                text_rect.width + 16, text_rect.height + 8)
            pygame.draw.rect(screen, (255, 255, 255, 200), bg_rect, border_radius=6)
            pygame.draw.rect(screen, (211, 47, 47), bg_rect, 2, border_radius=6)
            
            screen.blit(pause_text, text_rect)
        
        # Instrucciones en la parte inferior - ACTUALIZADO
        instructions = [
            "Controles: ESPACIO = Pausa/Resume, R = Reset, Start/Stop = Control simulación",
            f"Modo: {'Lissajous (curvas automáticas)' if mode else 'Manual (mover sliders para ver efecto)'}"
        ]
        
        font_instructions = pygame.font.SysFont('Arial', 12)
        for i, instruction in enumerate(instructions):
            text = font_instructions.render(instruction, True, (60, 70, 80))
            screen.blit(text, (400, screen.get_height() - 40 + i * 15))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()