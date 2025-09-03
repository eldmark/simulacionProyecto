# Universidad del Valle de Guatemala
# Física 3
# Julián Divas
# 24687

from typing import Final
import numpy as n
from scipy.constants import electron_mass, e


# Longitud de las placas deflectoras
lon_plates: Final = 0.05
# Ancho de las placas deflectoras
wid_plates: Final = 0.05


# Área de las placas deflectoras
plates_a: Final = lon_plates * wid_plates
# Distancia de separación de las placas
d_plates: Final = 0.02
# Distancia desde las placas verticales a las horizontales
db_plates: Final = 0.03
# Distancia desde las placas horizontales a la pantalla
db_plates_screen: Final = 0.15
# Distancia total desde el cañón a las placas verticales
db_plates_canyon: Final = 0.05

# Electron's initial speed 
def ini_speed(e_accel):
    return n.sqrt((2*n.e*e_accel)/electron_mass)

# Uniform electric field magnitude between plates
# plates_v: Voltage applied to the plates 
def electric_field(plates_v):
    return plates_v / d_plates 

# Acceleration caused by the electric field
def e_field_accel(electric_field_val):
    return (e * electric_field_val) / electron_mass

# Time between plates
def total_time(ini_speed_val):
    return db_plates_screen / ini_speed_val

# Delimits time regions for the electron's trajectory
def region_time(ini_speed_val):
    return {
        "time_0": 0.0,
        "start_vplates": db_plates_canyon / ini_speed_val,
        "end_vplates": (db_plates_canyon + lon_plates) / ini_speed_val,
        "start_hplates": (db_plates_canyon + lon_plates + db_plates) / ini_speed_val,
        "end_hplates": (db_plates_canyon + lon_plates + db_plates + lon_plates) / ini_speed_val,
        "reach_screen": (db_plates_canyon + lon_plates + db_plates + lon_plates + db_plates_screen) / ini_speed_val
    }

def determine_region(time, times):
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
    
# Función corregida que acepta voltajes vertical y horizontal por separado
def get_position_by_time(e_accel, v_vertical, v_horizontal, time):
    speed = ini_speed(e_accel)
    region_times = region_time(speed)

    return {
        "lateral_view": get_lateral_view_position(v_vertical, speed, time, region_times),
        "superior_view": get_superior_view_position(v_horizontal, speed, time, region_times),
        "tiempo": time,
        "region": determine_region(time, region_times)
    }

def get_lateral_view_position(plates_voltage, ini_speed_val, time, region_times):
    depth = ini_speed_val * time

    if time <= region_times["start_vplates"]:
        return (depth, 0.0)

    elif time <= region_times["end_vplates"]:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_vplates = time - region_times["start_vplates"]
        movement = (1/2) * e_field_accel_val * time_vplates**2
        return (depth, movement)
    
    else:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_vplates = region_times["end_vplates"] - region_times["start_vplates"]
        movement_bplates = (1/2) * e_field_accel_val * time_vplates**2
        exit_speed = e_field_accel_val * time_vplates
        time_after_vplates = time - region_times["end_vplates"]
        final_movement = movement_bplates + (exit_speed * time_after_vplates)
        return (depth, final_movement)
    
def get_superior_view_position(plates_voltage, ini_speed_val, time, region_times):
    depth = ini_speed_val * time

    if time <= region_times["start_hplates"]:
        return (depth, 0.0)

    elif time <= region_times["end_hplates"]:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_hplates = time - region_times["start_hplates"]
        movement = (1/2) * e_field_accel_val * time_hplates**2
        return (depth, movement)

    else:
        electric_field_val = electric_field(plates_voltage)
        e_field_accel_val = e_field_accel(electric_field_val)
        time_hplates = region_times["end_hplates"] - region_times["start_hplates"]
        movement_bplates = (1/2) * e_field_accel_val * time_hplates**2
        exit_speed = e_field_accel_val * time_hplates
        time_after_hplates = time - region_times["end_hplates"]
        final_movement = movement_bplates + (exit_speed * time_after_hplates)
        return (depth, final_movement)