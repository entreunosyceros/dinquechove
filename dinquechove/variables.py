"""
Variables meteorológicas habituales y etiquetas en español.

Los nombres de variable dentro de las listas (p. ej. temperature_2m) son los que
exige la API Open-Meteo en inglés; no se pueden traducir en la petición HTTP.
"""

# Conjuntos predefinidos de variables horarias para no escribirlas a mano.
PRESETS_HORARIOS: dict[str, list[str]] = {
    "basico": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "weather_code",
    ],
    "viento": [
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
    ],
    "completo": [
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "precipitation",
        "rain",
        "snowfall",
        "cloud_cover",
        "pressure_msl",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "weather_code",
    ],
}

# Conjuntos predefinidos de variables agregadas por día.
PRESETS_DIARIOS: dict[str, list[str]] = {
    "basico": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "weather_code",
    ],
    "viento": [
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",
    ],
    "completo": [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "sunshine_duration",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "uv_index_max",
        "weather_code",
    ],
}

# Texto legible en español para cada clave devuelta por la API.
ETIQUETAS_ES: dict[str, str] = {
    "temperature_2m": "Temperatura (2 m)",
    "apparent_temperature": "Sensación térmica",
    "relative_humidity_2m": "Humedad relativa",
    "precipitation": "Precipitación",
    "rain": "Lluvia",
    "snowfall": "Nieve",
    "cloud_cover": "Nubosidad",
    "pressure_msl": "Presión (nivel del mar)",
    "wind_speed_10m": "Velocidad del viento (10 m)",
    "wind_direction_10m": "Dirección del viento (10 m)",
    "wind_gusts_10m": "Ráfagas (10 m)",
    "weather_code": "Código meteorológico (WMO)",
    "temperature_2m_max": "Tª máxima",
    "temperature_2m_min": "Tª mínima",
    "temperature_2m_mean": "Tª media",
    "precipitation_sum": "Precipitación acumulada",
    "rain_sum": "Lluvia acumulada",
    "snowfall_sum": "Nieve acumulada",
    "sunshine_duration": "Horas de sol",
    "wind_speed_10m_max": "Viento máximo",
    "wind_gusts_10m_max": "Ráfagas máximas",
    "wind_direction_10m_dominant": "Dirección dominante del viento",
    "uv_index_max": "Índice UV máximo",
}

# Traducción de códigos WMO (weather_code) a descripción en español.
CODIGOS_TIEMPO_ES: dict[int, str] = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    71: "Nieve ligera",
    73: "Nieve moderada",
    75: "Nieve fuerte",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos violentos",
    95: "Tormenta",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo fuerte",
}


def etiqueta_de_variable(nombre_variable: str) -> str:
    """
    Devuelve una etiqueta en español para mostrar al usuario.

    Si la variable no está en ETIQUETAS_ES, genera un texto a partir del nombre
    técnico de la API (sustituyendo guiones bajos).
    """
    if nombre_variable in ETIQUETAS_ES:
        return ETIQUETAS_ES[nombre_variable]
    return nombre_variable.replace("_", " ").title()
