
import pygame
from pygame.locals import *
from slider import Slider

# Inicializar modo global
mode = False


sliders = []
def draw_ui(screen, color_mode, xpos, ypos):
    #xpos y ypos son las coordenadas donde se va a dibujar el boton
    #color mode: es una lista con todos los colores que se van a usar en la interfaz
    """Dibuja la interfaz de usuario con todos los controles."""
    # Dibujar sliders
    for slider in sliders:
        slider.draw(screen, title_font_size=30, value_font_size=30, title_offset_y=70, value_offset_y=40, line_thickness=8, handle_radius=20) # los parametros se pueden cambiar para 
    
    # Dibujar botón de modo
    font = pygame.font.SysFont(None, 30)
    if not mode:
        mode_text = font.render(f"Modo: Manual", True, color_mode[0])
    else:
        mode_text = font.render(f"Modo: Toggle", True, color_mode[0])
    screen.blit(mode_text, (50, 350))
    #aqui estan las coordenadas del boton
    mode_button = pygame.Rect(ypos, xpos, 170, 40)
    pygame.draw.rect(screen, color_mode[1], mode_button, 2)
    # cambiar de modo
    button_text = font.render("Cambiar Modo", True, color_mode[0])
    screen.blit(button_text, (60, 390))
    
    return mode_button

def handle_ui_events(event, mode_button):
    """Maneja los eventos de la interfaz de usuario."""
 
    for slider in sliders:
        if slider.handle_event(event):
            # Actualizar variables globales
            # recordar que el label del slider debe tener el formato "Nombre: unidad"
            # las variables globales se van a declarar cuando Julian integre los cálculos
            globals()[slider.label.split(":")[0].lower().replace(" ", "_")] = slider.value # Cambiar esto si es necesario pq se puede hacer con diccionarios o algo más elegante (Julian Clutch)
    
    # Cambiar modo si se hace clic en el botón
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        if mode_button.collidepoint(event.pos):
            global mode
            mode = not mode
            return
    
    return None



def main():
    global V_acc, V_vert, V_horiz, persistence, mode, freq_v, freq_h

    running = True
    screen = pygame.display.set_mode((1200, 700))
    color_mode = [(0,0,0), (0,120,255)]
    sliders.clear()
    sliders.append(Slider(50, 80, 500, 40, 0, 100, 50, title="Frecuencia", unit="Hz", toggle=mode))
    clock = pygame.time.Clock()
    while running:
        screen.fill((255, 255, 255))
        mode_button = draw_ui(screen, color_mode)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_ui_events(event, mode_button)
        # Actualizar estado de los sliders según el modo
        for slider in sliders:
            slider.set_disabled(mode)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
clock = pygame.time.Clock()


if __name__ == "__main__":
    main()
