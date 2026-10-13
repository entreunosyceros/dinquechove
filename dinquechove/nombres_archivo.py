"""Nombres de archivo seguros a partir del lugar consultado."""

from __future__ import annotations

import re
from pathlib import Path


def sanitizar_nombre_lugar(nombre_lugar: str, longitud_maxima: int = 50) -> str:
    """
    Convierte el nombre del lugar en un fragmento válido para nombres de archivo.

    Sustituye espacios y signos de puntuación por guiones bajos y elimina
    caracteres no permitidos en la mayoría de sistemas de archivos.
    """
    texto = nombre_lugar.strip()
    # Formato "(lat, lon)" al usar --latitud/--longitud sin nombre de ciudad.
    if texto.startswith("(") and "," in texto:
        texto = re.sub(r"[(),\s]+", "_", texto)
    else:
        texto = re.sub(r"[^\w\s\-.]", "", texto, flags=re.UNICODE)
        texto = re.sub(r"\s+", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("_")
    if not texto:
        texto = "lugar"
    return texto[:longitud_maxima]


def construir_ruta_grafico(
    ruta_solicitada: Path,
    nombre_lugar: str,
    *,
    tipo_datos: str,
) -> Path:
    """
    Añade el lugar y el tipo de datos (horario/diario) al nombre del PNG.

    Ejemplo: salida_diaria.png + Madrid -> madrid_salida_diaria_diario.png
    """
    slug = sanitizar_nombre_lugar(nombre_lugar).lower()
    sufijo = ruta_solicitada.suffix or ".png"
    base = ruta_solicitada.stem
    tipo = "horario" if tipo_datos == "hourly" else "diario"
    nombre = f"{slug}_{base}_{tipo}{sufijo}"
    return ruta_solicitada.with_name(nombre)
