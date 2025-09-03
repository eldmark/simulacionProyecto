# Simulación de Tubo de Rayos Catódicos (CRT)

## 📖 Descripción

Simulación interactiva de un Tubo de Rayos Catódicos que muestra el comportamiento físico real de los electrones bajo la influencia de campos eléctricos. Incluye visualizaciones 3D, modo manual y modo Lissajous.

## 🚀 Características

### 🎯 Modos de Operación
- **Modo Manual**: Control directo de voltajes de deflexión
- **Modo Lissajous**: Generación de figuras de interferencia sinusoidal

### 👁️ Vistas Implementadas
1. **Vista Lateral**: Muestra deflexión vertical (placas verticales)
2. **Vista Superior**: Muestra deflexión horizontal (placas horizontales)  
3. **Vista Frontal**: Pantalla fosforescente con persistencia

### ⚡ Física Realista
- Cálculo preciso de trayectorias electrónicas
- Campos eléctricos y aceleración perpendicular
- Movimiento parabólico dentro de placas
- Movimiento rectilíneo fuera de placas
- Persistencia fosforescente realista

## 🛠️ Instalación

### Requisitos
```bash
Python 3.8+
Pygame 2.0+
NumPy
SciPy
```

### Instalación de Dependencias
```bash
pip install pygame numpy scipy
```

### Ejecución
```bash
python main.py
```

## 🎮 Controles

### 🔧 Sliders Interactivos
- **V Aceleración**: 500-2000V (Velocidad electrones)
- **V Vertical**: -1000 a +1000V (Deflexión vertical)
- **V Horizontal**: -1000 a +1000V (Deflexión horizontal)
- **Persistencia**: 0.1-5.0s (Tiempo fosforescencia)
- **Frecuencia Vertical**: 0.1-10.0Hz (Modo Lissajous)
- **Frecuencia Horizontal**: 0.1-10.0Hz (Modo Lissajous)

### 🎯 Modo Manual
- Control directo de voltajes
- Visualización en tiempo real
- Actualización instantánea

### 🌊 Modo Lissajous
- Generación de figuras de interferencia
- Control de frecuencias y fases
- Animación suave y continua

## 📁 Estructura del Proyecto

```
CRT_Simulator/
├── main.py              # Aplicación principal
├── calculos.py          # Cálculos físicos y matemáticos
├── visualization.py     # Visualización 3D y renderizado
├── slider.py           # Componentes de UI interactivos
└── README.md           # Documentación
```
