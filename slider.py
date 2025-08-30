import pygame

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, title="Slider", unit="n/a", toggle=False):
        #definición de los atributos de la clase slider
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = max(0, min_val)
        self.max_val = max(self.min_val, max_val)
        self.value = max(self.min_val, min(initial_val, self.max_val))
        self.handle_radius = height // 2
        self.handle_pos = self.value_to_pos(self.value)
        self.dragging = False
        self.font = pygame.font.SysFont(None, 24)
        self.title = title
        self.unit = unit
        self.disabled = toggle

    def value_to_pos(self, value):
        # se utiliza un ratio para mapear el valor al rango del slider
        # Esto asegura que el handle se posicione correctamente en función del valor actual
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def pos_to_value(self, pos_x):
        
        # Se utiliza un ratio para mapear la posición del slider al valor correspondiente
        # Esto asegura que el valor se actualice correctamente al mover el slider
        ratio = (pos_x - self.rect.x) / self.rect.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return max(self.min_val, min(self.max_val, value))

    def draw(self, surface, 
             title_font_size=24, 
             value_font_size=24, 
             title_offset_y=55, 
             value_offset_y=30, 
             line_thickness=5, 
             handle_radius=None):
        # Permitir personalizar tamaños y posiciones del slider mediante parámetros
        font_title = pygame.font.SysFont(None, title_font_size)
        font_value = pygame.font.SysFont(None, value_font_size)
        title_text = font_title.render(self.title, True, (0, 0, 0))
        surface.blit(title_text, (self.rect.x, self.rect.y - title_offset_y))
        line_color = (180, 180, 180) if self.disabled else (200, 200, 200)
        handle_color = (120, 120, 180) if self.disabled else (100, 100, 250)
        value_color = (100, 100, 100) if self.disabled else (0, 0, 0)
        pygame.draw.line(surface, line_color, (self.rect.x, self.rect.centery), (self.rect.right, self.rect.centery), line_thickness)
        # Permitir cambiar el radio del handle
        radius = handle_radius if handle_radius is not None else self.handle_radius
        pygame.draw.circle(surface, handle_color, (self.handle_pos, self.rect.centery), radius)
        value_text = font_value.render(f"{self.value:.2f} {self.unit}", True, value_color)
        surface.blit(value_text, (self.rect.x, self.rect.y - value_offset_y))
        if self.disabled:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((200, 200, 200, 80))
            surface.blit(overlay, (self.rect.x, self.rect.y))


    def handle_event(self, event):
        # Si está deshabilitado, ignora eventos
        if self.disabled:
            return
        #se definen los eventos que va a manejar el slider, izqquierda bajar, derecha subir valor
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_over_handle(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_pos = max(self.rect.x, min(event.pos[0], self.rect.right))
                self.value = self.pos_to_value(self.handle_pos)
                self.handle_pos = self.value_to_pos(self.value)  # se actualiza la posición del handle
    def set_disabled(self, toggle):
        #desabilitar el slider
        self.disabled = toggle

    # La función calcula la distancia al cuadrado entre el punto pos y el centro del handle usando la fórmula del círculo
    def is_over_handle(self, pos):
        return (pos[0] - self.handle_pos) ** 2 + (pos[1] - self.rect.centery) ** 2 <= self.handle_radius ** 2
    # Obtener el valor actual del slider
    def get_value(self):
        return self.value, self.unit