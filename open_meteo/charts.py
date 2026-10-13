"""Gráficos a partir de respuestas JSON de Open-Meteo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from open_meteo.fechas import formato_eje_grafico, parsear_marca_tiempo
from open_meteo.variables import etiqueta_de_variable


def _analizar_marcas_tiempo(marcas: list[str]) -> list:
    """Convierte las marcas ISO de la API en objetos datetime para el gráfico."""
    return [parsear_marca_tiempo(marca) for marca in marcas]


def _configurar_eje_tiempo(
    eje,
    es_horario: bool,
    *,
    mostrar_nombre_eje: bool = True,
) -> None:
    """
    Activa formato de fechas en el eje X y fija marcas y etiquetas visibles.

    Con sharex=True, Matplotlib oculta las fechas en los subgráficos superiores;
    hay que forzar labelbottom en cada eje.
    """
    eje.xaxis_date()
    localizador = mdates.AutoDateLocator(minticks=4, maxticks=10)
    formateador = mdates.DateFormatter(formato_eje_grafico(es_horario))
    eje.xaxis.set_major_locator(localizador)
    eje.xaxis.set_major_formatter(formateador)
    if mostrar_nombre_eje:
        eje.set_xlabel("Fecha y hora" if es_horario else "Fecha")
    eje.tick_params(axis="x", labelsize=8, rotation=35, labelbottom=True)
    for etiqueta in eje.get_xticklabels():
        etiqueta.set_visible(True)


def graficar_series(
    datos: dict[str, Any],
    seccion: str,
    variables: list[str],
    *,
    titulo: str | None = None,
    archivo_salida: Path | None = None,
    mostrar: bool = True,
) -> None:
    """
    Dibuja una o más series temporales (hourly o daily) en subgráficos apilados.

    datos: respuesta completa de obtener_prevision.
    seccion: 'hourly' o 'daily' (claves del JSON de Open-Meteo).
    variables: nombres técnicos de campos a representar (máximo recomendado: 4).
    archivo_salida: si se indica, guarda PNG sin mostrar ventana (según `mostrar`).
    """
    bloque = datos.get(seccion)
    if not bloque or "time" not in bloque:
        raise ValueError(f"No hay datos '{seccion}' en la respuesta.")

    fechas = _analizar_marcas_tiempo(bloque["time"])
    unidades = datos.get(f"{seccion}_units") or {}
    es_horario = seccion == "hourly"

    figura, ejes = plt.subplots(
        len(variables), 1, figsize=(11, 3 * len(variables)), sharex=True
    )
    if len(variables) == 1:
        ejes = [ejes]

    for eje, nombre_variable in zip(ejes, variables):
        valores = bloque.get(nombre_variable)
        if valores is None:
            eje.set_title(f"{etiqueta_de_variable(nombre_variable)} (sin datos)")
            continue
        unidad = unidades.get(nombre_variable, "")
        etiqueta_y = (
            f"{etiqueta_de_variable(nombre_variable)} ({unidad})"
            if unidad
            else etiqueta_de_variable(nombre_variable)
        )
        eje.plot(fechas, valores, marker="o", markersize=4, linewidth=1.5)
        eje.set_ylabel(etiqueta_y)
        eje.grid(True, alpha=0.3)

    for indice, eje in enumerate(ejes):
        es_ultimo = indice == len(ejes) - 1
        _configurar_eje_tiempo(eje, es_horario, mostrar_nombre_eje=es_ultimo)

    if titulo:
        figura.suptitle(titulo, fontsize=13, y=0.995)
    else:
        zona = datos.get("timezone", "")
        figura.suptitle(f"Open-Meteo — {seccion} ({zona})", fontsize=13, y=0.995)

    # Espacio vertical extra: cada subgráfico muestra sus propias fechas en el eje X.
    figura.subplots_adjust(left=0.1, right=0.98, top=0.93, bottom=0.06, hspace=0.62)
    figura.canvas.draw()

    if archivo_salida:
        archivo_salida.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(
            archivo_salida,
            dpi=120,
            bbox_inches="tight",
            pad_inches=0.2,
        )
    if mostrar:
        plt.show()
    plt.close(figura)
