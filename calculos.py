# Universidad del Valle de Guatemala
# Física 3
# Julián Divas
# 24687

from typing import Final
import numpy as np
from scipy.constants import electron_mass, e
import math

# Constantes físicas del CRT (según el proyecto)
# CORREGIDO: Definir todas las distancias correctamente
db_plates_canyon: Final = 0.05  # Distancia del cañón a placas verticales (5 cm)
lon_plates: Final = 0.05  # Longitud de las placas deflectoras (5 cm)
plates_a: Final = lon_plates**2  # Área de las placas deflectoras
d_plates: Final = 0.02  # Distancia de separación de las placas (2 cm)
db_between_plates: Final = 0.03  # Distancia entre placas verticales y horizontales (3 cm)
db_plates_screen: Final = 0.15  # Distancia desde las placas horizontales a la pantalla (15 cm)

def ini_speed(e_accel):
    """Calcula la velocidad inicial del electrón después de la aceleración."""
    return np.sqrt((2 * e * e_accel) / electron_mass)

def electric_field(plates_v):
    """Calcula la magnitud del campo eléctrico uniforme entre placas."""
    return plates_v / d_plates 

def e_field_accel(electric_field_val):
    """Calcula la aceleración causada por el campo eléctrico."""
    return (e * electric_field_val) / electron_mass

def region_time(ini_speed_val):
    """Define los tiempos límite para las diferentes regiones de la trayectoria del electrón."""
    return {
        "time_0": 0.0,
        "start_vplates": db_plates_canyon / ini_speed_val,
        "end_vplates": (db_plates_canyon + lon_plates) / ini_speed_val,
        "start_hplates": (db_plates_canyon + lon_plates + db_between_plates) / ini_speed_val,
        "end_hplates": (db_plates_canyon + lon_plates + db_between_plates + lon_plates) / ini_speed_val,
        "reach_screen": (db_plates_canyon + lon_plates + db_between_plates + lon_plates + db_plates_screen) / ini_speed_val
    }

def get_position_normal_mode(accel_vol, hplates_V, vplates_V, ini_speed_val):
    # Tiempo entre placas
    time = total_time(ini_speed_val)

    time_post_plate = db_plates_screen / ini_speed_val

    #Aceleración horizontal (placas verticales)
    helectric_field = electric_field(hplates_V)
    h_acc = e_field_accel(helectric_field)

    # Aceleración vertical (placas horizontales)
    velectric_field = electric_field(vplates_V)
    v_acc = e_field_accel(velectric_field)
    
    # Velocidad a la que llega el electron
    ini_speed = ini_speed(accel_vol)

    x_position = (1/2) * h_acc * time**2
    y_position = (1/2) * v_acc * time**2
    
    # PLano ZY (Z es horizontal, Y es vertical)
    vfy = v_acc * time_post_plate
    final_y_position = y_position + (vfy *time_post_plate)

    vfx = h_acc * time_post_plate
    final_x_position = x_position + (vfx *time_post_plate)

    z_position = ini_speed*time

    return (x_position, y_position, z_position)

def sinusoidal_signal(time, freq, amplitude, phase):
    return amplitude*np.sin(2 * np.pi * freq * time + phase)

# Time between plates
def total_time(ini_speed_val):
    return db_plates_screen / ini_speed_val

def position_sinusoidal_mode(ini_speed_val, e_accel, h_freq, v_freq, amplitude, phase):
        # Tiempo entre placas
    time = total_time(ini_speed_val)

    time_post_plate = db_plates_screen / ini_speed_val

    #Aceleración horizontal (placas verticales)
    hplates_V = sinusoidal_signal(time, h_freq, amplitude, phase)
    helectric_field = electric_field(hplates_V)
    h_acc = e_field_accel(helectric_field)

    # Aceleración vertical (placas horizontales)
    vplates_V = sinusoidal_signal(time, v_freq, amplitude, phase)
    velectric_field = electric_field(vplates_V)
    v_acc = e_field_accel(velectric_field)
    
    # Velocidad a la que llega el electron
    ini_speed = ini_speed(e_accel)

    x_position = (1/2) * h_acc * time**2
    y_position = (1/2) * v_acc * time**2
    
    # PLano ZY (Z es horizontal, Y es vertical)
    vfy = v_acc * time_post_plate
    final_y_position = y_position + (vfy *time_post_plate)

    vfx = h_acc * time_post_plate
    final_x_position = x_position + (vfx *time_post_plate)

    z_position = ini_speed*time

    return (x_position, y_position, z_position)

def determine_region(time, times):
    """Determina en qué región del CRT se encuentra el electrón en un tiempo dado."""
    if time <= times["time_0"]:
        return "in_canyon"
    elif time <= times["start_vplates"]:
        return "before_vertical_plates"
    elif time <= times["end_vplates"]:
        return "in_vertical_plates"
    elif time <= times["start_hplates"]:
        return "between_plates"
    elif time <= times["end_hplates"]:
        return "in_horizontal_plates"
    elif time <= times["reach_screen"]:
        return "after_horizontal_plates"
    else:
        return "in_screen"

def get_position_by_time(e_accel, v_vertical, v_horizontal, time):
    """
    FUNCIÓN PRINCIPAL CORREGIDA: Calcula la posición del electrón en un tiempo dado.
    """
    speed = ini_speed(e_accel)
    region_times = region_time(speed)

    return {
        "lateral_view": get_lateral_view_position(v_vertical, speed, time, region_times),
        "superior_view": get_superior_view_position(v_horizontal, speed, time, region_times),
        "tiempo": time,
        "region": determine_region(time, region_times)
    }

def get_lateral_view_position(plates_voltage, ini_speed_val, time, region_times):
    """
    CORREGIDO: Calcula la posición para la vista lateral (deflexión vertical).
    """
    # Profundidad (coordenada Z) - siempre avanza
    depth = ini_speed_val * time

    # Antes de las placas verticales - sin deflexión
    if time <= region_times["start_vplates"]:
        return (depth, 0.0)

    # Durante el paso por las placas verticales
    elif time <= region_times["end_vplates"]:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_in_plates = time - region_times["start_vplates"]
        
        # Movimiento parabólico durante las placas
        vertical_displacement = 0.5 * e_field_accel_val * time_in_plates**2
        return (depth, vertical_displacement)
    
    # Después de las placas verticales - movimiento rectilíneo uniforme
    else:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        
        # Tiempo total dentro de las placas
        time_in_plates = region_times["end_vplates"] - region_times["start_vplates"]
        
        # Desplazamiento y velocidad al salir de las placas
        displacement_in_plates = 0.5 * e_field_accel_val * time_in_plates**2
        exit_velocity = e_field_accel_val * time_in_plates
        
        # Tiempo después de salir de las placas
        time_after_plates = time - region_times["end_vplates"]
        
        # Posición final = posición al salir + velocidad × tiempo adicional
        final_displacement = displacement_in_plates + (exit_velocity * time_after_plates)
        return (depth, final_displacement)

def get_superior_view_position(plates_voltage, ini_speed_val, time, region_times):
    """
    CORREGIDO: Calcula la posición para la vista superior (deflexión horizontal).
    """
    # Profundidad (coordenada Z) - siempre avanza
    depth = ini_speed_val * time

    # Antes de las placas horizontales - sin deflexión
    if time <= region_times["start_hplates"]:
        return (depth, 0.0)

    # Durante el paso por las placas horizontales
    elif time <= region_times["end_hplates"]:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_in_plates = time - region_times["start_hplates"]
        
        # Movimiento parabólico durante las placas
        horizontal_displacement = 0.5 * e_field_accel_val * time_in_plates**2
        return (depth, horizontal_displacement)

    # Después de las placas horizontales - movimiento rectilíneo uniforme
    else:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        
        # Tiempo total dentro de las placas
        time_in_plates = region_times["end_hplates"] - region_times["start_hplates"]
        
        # Desplazamiento y velocidad al salir de las placas
        displacement_in_plates = 0.5 * e_field_accel_val * time_in_plates**2
        exit_velocity = e_field_accel_val * time_in_plates
        
        # Tiempo después de salir de las placas
        time_after_plates = time - region_times["end_hplates"]
        
        # Posición final = posición al salir + velocidad × tiempo adicional
        final_displacement = displacement_in_plates + (exit_velocity * time_after_plates)
        return (depth, final_displacement)

def sinusoidal_signal(time, freq, amplitude, fase):
    """Genera una señal sinusoidal."""
    return amplitude * np.sin(2 * np.pi * freq * time + fase)

def lissajous_position_by_time(e_accel, h_freq, v_freq, time, amplitude, fase_h=0, fase_v=0):
    """
    CORREGIDO: Calcula la posición para figuras de Lissajous con fases independientes.
    """
    v_voltage = sinusoidal_signal(time, v_freq, amplitude, fase_v)
    h_voltage = sinusoidal_signal(time, h_freq, amplitude, fase_h)

    return get_position_by_time(e_accel, v_voltage, h_voltage, time)

def get_final_screen_position(e_accel, v_vertical, v_horizontal):
    """
    NUEVA FUNCIÓN: Calcula la posición final del electrón en la pantalla.
    Esta función es útil para obtener directamente donde golpea el electrón.
    """
    speed = ini_speed(e_accel)
    region_times = region_time(speed)
    
    # Usar el tiempo cuando el electrón llega a la pantalla
    screen_time = region_times["reach_screen"]
    
    # Obtener posiciones en ambas vistas
    lateral_pos = get_lateral_view_position(v_vertical, speed, screen_time, region_times)
    superior_pos = get_superior_view_position(v_horizontal, speed, screen_time, region_times)
    
    return {
        "x_displacement": superior_pos[1],  # Desplazamiento horizontal
        "y_displacement": lateral_pos[1],   # Desplazamiento vertical
        "time_to_screen": screen_time
    }

# NUEVAS FUNCIONES PARA DEBUGGING Y VALIDACIÓN
def validate_crt_geometry():
    """Valida que la geometría del CRT sea consistente."""
    total_length = db_plates_canyon + lon_plates + db_between_plates + lon_plates + db_plates_screen
    print(f"Longitud total del CRT: {total_length:.3f} m")
    print(f"Cañón a placas V: {db_plates_canyon:.3f} m")
    print(f"Placas V: {lon_plates:.3f} m")
    print(f"Entre placas: {db_between_plates:.3f} m") 
    print(f"Placas H: {lon_plates:.3f} m")
    print(f"Placas a pantalla: {db_plates_screen:.3f} m")
    
    return total_length

def debug_electron_trajectory(e_accel, v_vertical, v_horizontal, num_points=10):
    """Función de debug para imprimir la trayectoria del electrón."""
    speed = ini_speed(e_accel)
    region_times = region_time(speed)
    
    print(f"\nTrayectoria del electrón:")
    print(f"Velocidad inicial: {speed:.2e} m/s")
    print(f"Tiempos de región: {region_times}")
    
    max_time = region_times["reach_screen"]
    for i in range(num_points + 1):
        t = (i / num_points) * max_time
        result = get_position_by_time(e_accel, v_vertical, v_horizontal, t)
        
        print(f"t={t:.6f}s: Región={result['region']}, "
              f"Lateral={result['lateral_view']}, Superior={result['superior_view']}")

if __name__ == "__main__":
    # Código de prueba
    print("=== VALIDACIÓN DE LA GEOMETRÍA DEL CRT ===")
    validate_crt_geometry()
    
    print("\n=== PRUEBA DE TRAYECTORIA ===")
    debug_electron_trajectory(1000, 500, -300, 5)