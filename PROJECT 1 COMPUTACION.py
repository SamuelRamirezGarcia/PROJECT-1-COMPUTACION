import math
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Funciones matemáticas básicas ---
def declinacion_solar(dia_juliano, latitud):
    # Fórmula de declinación solar (Cooper)
    return math.radians(23.45) * math.sin(math.radians(360 * (284 + dia_juliano) / 365))

def altura_solar(declinacion, hora_solar, latitud):
    # Fórmula de altura solar
    angulo_horario = math.radians(15 * (hora_solar - 12))
    sin_alpha = (math.sin(declinacion) * math.sin(latitud) +
                 math.cos(declinacion) * math.cos(latitud) * math.cos(angulo_horario))
    return math.asin(max(-1, min(1, sin_alpha)))

def acimut_solar(declinacion, altura, hora_solar, latitud):
    # Cálculo aproximado del acimut solar
    angulo_horario = math.radians(15 * (hora_solar - 12))
    cos_azimut = (math.sin(declinacion) - math.sin(altura) * math.sin(latitud)) / (math.cos(altura) * math.cos(latitud))
    cos_azimut = max(-1, min(1, cos_azimut))  # evitar errores numéricos
    azimut = math.acos(cos_azimut)
    if angulo_horario > 0:
        azimut = 2 * math.pi - azimut  # ajuste para la tarde
    return azimut

def simular_nubosidad(hora):
    # Simulación simple de nubosidad
    if 11 <= hora.hour <= 14:
        return 0.7
    elif 16 <= hora.hour <= 17:
        return 0.9
    return 1.0

def calcular_potencia(irradiancia, area_panel, eficiencia, temperatura, hora):
    # Aplicar nubosidad
    factor_nubosidad = simular_nubosidad(hora)
    irradiancia *= factor_nubosidad

    # Corrección por temperatura
    correccion_temp = 1 - 0.004 * max(0, temperatura - 25)

    # Pérdidas del sistema
    perdidas_sistema = 0.85

    potencia = irradiancia * area_panel * eficiencia * correccion_temp * perdidas_sistema
    return max(0, potencia)

# --- Parámetros de entrada ---
latitud = math.radians(4.711)  # Bogotá en radianes
area_panel = 15   # m²
eficiencia = 0.18
fecha = datetime(2025, 4, 2)

# --- Crear la serie temporal ---
tiempos = pd.date_range(start=fecha, end=fecha + timedelta(days=1), freq="10min")

# --- Listas para guardar resultados ---
potencias = []
irradiancias = []
energias = []
energia_total = 0

# --- Cálculos principales ---
for t in tiempos:
    dia_juliano = t.timetuple().tm_yday
    declinacion = declinacion_solar(dia_juliano, latitud)
    hora_decimal = t.hour + t.minute / 60
    altura = altura_solar(declinacion, hora_decimal, latitud)

    if altura > 0:
        # Radiación directa simple
        dni = 900 * math.sin(altura)
        # Radiación difusa aproximada
        dhi = 0.3 * dni
        irradiancia = dni + dhi
    else:
        irradiancia = 0

    potencia = calcular_potencia(irradiancia, area_panel, eficiencia, temperatura=22, hora=t)

    potencias.append(potencia)
    irradiancias.append(irradiancia)

    # Energía en 10 minutos -> Wh
    energia = potencia * (10/60)
    energias.append(energia)
    energia_total += energia

# --- Resultados básicos ---
print("Energía total generada en el día:", round(energia_total, 2), "Wh")
print("Potencia máxima:", round(max(potencias), 2), "W")

# --- Gráficas ---
plt.figure(figsize=(10,5))
plt.plot(tiempos, potencias, label="Potencia (W)", color="orange")
plt.xlabel("Hora")
plt.ylabel("Potencia (W)")
plt.title("Potencia FV a lo largo del día (modelo simple)")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10,5))
plt.plot(tiempos, irradiancias, label="Irradiancia (W/m²)", color="blue")
plt.xlabel("Hora")
plt.ylabel("W/m²")
plt.title("Irradiancia solar en superficie horizontal (simplificada)")
plt.legend()
plt.grid(True)
plt.show()

