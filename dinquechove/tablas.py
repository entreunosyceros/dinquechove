"""Tablas con bordes para mostrar datos en la consola."""

from __future__ import annotations


def _anchos_columnas(encabezados: list[str], filas: list[list[str]]) -> list[int]:
    """Calcula el ancho mínimo de cada columna según cabecera y contenido."""
    anchos = [len(texto) for texto in encabezados]
    for fila in filas:
        for indice, celda in enumerate(fila):
            anchos[indice] = max(anchos[indice], len(celda))
    return anchos


def _celda(texto: str, ancho: int) -> str:
    """Alinea el texto a la izquierda dentro de un ancho fijo."""
    return texto.ljust(ancho)


def _linea_horizontal(esquina_izq: str, cruce: str, esquina_der: str, anchos: list[int]) -> str:
    """Genera una línea horizontal de la tabla (parte superior, separador o inferior)."""
    segmentos = ["─" * (ancho + 2) for ancho in anchos]
    return esquina_izq + cruce.join(segmentos) + esquina_der


def _linea_datos(celdas: list[str], anchos: list[int]) -> str:
    """Genera una fila con bordes verticales y celdas alineadas."""
    partes = [f" {_celda(celdas[i], anchos[i])} " for i in range(len(celdas))]
    return "│" + "│".join(partes) + "│"


def imprimir_tabla(encabezados: list[str], filas: list[list[str]]) -> None:
    """
    Imprime una tabla con bordes en la consola.

    encabezados: nombres de columnas.
    filas: lista de filas; cada fila debe tener el mismo número de columnas que encabezados.
    """
    if not encabezados or not filas:
        return

    anchos = _anchos_columnas(encabezados, filas)

    print(_linea_horizontal("┌", "┬", "┐", anchos))
    print(_linea_datos(encabezados, anchos))
    print(_linea_horizontal("├", "┼", "┤", anchos))
    for fila in filas:
        print(_linea_datos(fila, anchos))
    print(_linea_horizontal("└", "┴", "┘", anchos))
