"""Selección de horas representativas del día para las tablas horarias."""

from __future__ import annotations

from open_meteo.fechas import parsear_marca_tiempo

# Cuatro horas por franja del día (hora local de la respuesta de Open-Meteo).
FRANJAS_DEL_DIA: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("Primera hora", (0, 1, 2, 3)),
    ("Mañana", (8, 9, 10, 11)),
    ("Tarde", (14, 15, 16, 17)),
    ("Noche", (20, 21, 22, 23)),
)


def seleccionar_filas_horarias(
    marcas_tiempo: list[str],
) -> list[tuple[str, int]]:
    """
    Elige 16 instantes del primer día disponible: 4 por cada franja del día.

    Devuelve pares (nombre_franja, índice) en el orden en que deben mostrarse.
    Si falta alguna hora en la API, se omite esa fila.
    """
    if not marcas_tiempo:
        return []

    instantes = [parsear_marca_tiempo(marca) for marca in marcas_tiempo]
    dia_referencia = instantes[0].date()

    indice_por_hora: dict[int, int] = {}
    for indice, instante in enumerate(instantes):
        if instante.date() != dia_referencia:
            continue
        if instante.hour not in indice_por_hora:
            indice_por_hora[instante.hour] = indice

    filas_seleccionadas: list[tuple[str, int]] = []
    for nombre_franja, horas in FRANJAS_DEL_DIA:
        for hora in horas:
            indice = indice_por_hora.get(hora)
            if indice is not None:
                filas_seleccionadas.append((nombre_franja, indice))
    return filas_seleccionadas
