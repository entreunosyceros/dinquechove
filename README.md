# Open-Meteo — práctica de consultas y gráficos

Programa en Python para consultar la [API Open-Meteo](https://open-meteo.com/en/docs) **sin clave API** (tier gratuito para uso no comercial). Permite practicar parámetros de consulta, geocodificación de lugares y visualización de series temporales.

## Requisitos

- Python 3.10+
- Dependencias en `requirements.txt`

```bash
cd /media/entreunosyceros/COP.SEGURIDAD/PROGRAMAS/PYTHON/OpenMeteo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso interactivo

```bash
python main.py --actual --grafico
```

Te pedirá el nombre de una ciudad, mostrará la URL construida (para ver parámetros), un resumen tabular y un gráfico.

## Ejemplos con parámetros

Madrid por coordenadas, preset de viento, 3 días, guardar JSON y PNG:

```bash
python main.py --latitud 40.4168 --longitud -3.7038 \
  --horario viento --dias 3 --actual \
  --json datos.json --grafico grafico.png
  # PNG generado p. ej.: madrid_comunidad_de_madrid_spain_grafico_horario.png
```

Variables personalizadas (nombres exactos de la documentación):

```bash
python main.py --latitud 41.39 --longitud 2.17 \
  --horario temperature_2m,precipitation,wind_speed_10m \
  --diario temperature_2m_max,temperature_2m_min,precipitation_sum \
  --zona-horaria Europe/Madrid --grafico
```

Solo datos diarios:

```bash
python main.py --modo solo-diario --diario completo --grafico salida_diaria.png
# Guarda como: <lugar>_salida_diaria_diario.png
```

## Presets de variables

| Preset     | Uso |
|-----------|-----|
| `basico`  | Temperatura, humedad, precipitación, código WMO |
| `viento`  | Velocidad, dirección y ráfagas |
| `completo`| Conjunto amplio para explorar la API |

Lista completa de parámetros: [documentación oficial](https://open-meteo.com/en/docs).

## Estructura del proyecto

| Módulo | Descripción |
|--------|-------------|
| `open_meteo/client.py` | HTTP, geocodificación y construcción de URLs |
| `open_meteo/variables.py` | Presets y etiquetas en español |
| `open_meteo/charts.py` | Gráficos con Matplotlib |
| `main.py` | CLI principal |

## Uso desde código

```python
from open_meteo import ClienteOpenMeteo

cliente = ClienteOpenMeteo()
datos = cliente.obtener_prevision(
    40.4168, -3.7038,
    variables_horarias=["temperature_2m", "wind_speed_10m"],
    dias_prevision=5,
)
print(cliente.construir_url_prevision(
    latitude=40.4168, longitude=-3.7038,
    hourly=["temperature_2m"], forecast_days=5, timezone="auto",
))
```

## Licencia y uso de la API

Open-Meteo ofrece acceso gratuito para proyectos no comerciales con límites razonables de peticiones. Consulta los términos en [open-meteo.com](https://open-meteo.com/en/docs).
