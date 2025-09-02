# Universidad del Valle de Guatemala
# Física 3
# Julián Divas
# 24687

from typing import Final
import numpy as n
from scipy.constants import electron_mass, e


# Longitud de las placas deflectoras
l_plates: Final = 5
# Ancho de las placas deflectoras
w_plates: Final = 5
# Área de las placas deflectoras
plates_a: Final = l_plates * w_plates
# Distancia de separación de las placas
d_plates: Final = 5
# Distancia desde las placas verticales a las horizontales
db_plates: Final = 8

# Electron's initial speed 
def ini_speed(e_accel):
    return n.sqrt((2*n.e*e_accel)/electron_mass)

# Uniform electric field between plates
# plates_v: Voltage applied to the plates 
def electric_field(plates_v):
    return plates_v /d_plates 

# Electric field's  force applied to the electron
def f_force(electric_field):
    return e*electric_field

# Acceleration caused by the electric field
def e_field_accel(electric_field):
    return (e*electric_field)/electron_mass

# Time between plates
def time_bplates(ini_speed):
    return l_plates/ini_speed
