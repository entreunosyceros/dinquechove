"""Formato de fechas europeo (día-mes-año) para consola y gráficos."""

from __future__ import annotations

from datetime import datetime

# Patrones strftime: día-mes-año, estilo habitual en España/Europa.
FORMATO_SOLO_FECHA = "%d-%m-%Y"
FORMATO_FECHA_HORA = "%d-%m-%Y %H:%M"


def parsear_marca_tiempo(marca: str) -> datetime:
    """
    Convierte una marca temporal ISO de Open-Meteo en datetime.

    Ejemplos de entrada: '2026-10-13T14:00' o '2026-10-13' (datos diarios).
    """
    if "T" in marca:
        return datetime.fromisoformat(marca)
    return datetime.fromisoformat(marca + "T00:00:00")


def formatear_marca_tiempo(marca: str) -> str:
    """
    Muestra la fecha en formato europeo dd-mm-aaaa (y hora si la trae la API).

    Sustituye el orden año-mes-día (ISO) que devuelve Open-Meteo.
    """
    instante = parsear_marca_tiempo(marca)
    if "T" in marca:
        return instante.strftime(FORMATO_FECHA_HORA)
    return instante.strftime(FORMATO_SOLO_FECHA)


def formato_eje_grafico(es_horario: bool) -> str:
    """Cadena strftime para el eje X de Matplotlib (europeo con año)."""
    return FORMATO_FECHA_HORA if es_horario else FORMATO_SOLO_FECHA
