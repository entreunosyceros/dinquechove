#!/usr/bin/env python3
"""
dinquechove — consultas a Open-Meteo (sin API key, uso no comercial).

Documentación: https://open-meteo.com/en/docs
Geocodificación: https://open-meteo.com/en/docs/geocoding-api
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dinquechove.charts import graficar_series
from dinquechove.client import ClienteOpenMeteo, ErrorOpenMeteo
from dinquechove.fechas import formatear_marca_tiempo, parsear_marca_tiempo
from dinquechove.muestreo_horario import seleccionar_filas_horarias
from dinquechove.nombres_archivo import construir_ruta_grafico
from dinquechove.tablas import imprimir_tabla
from dinquechove.variables import (
    CODIGOS_TIEMPO_ES,
    PRESETS_DIARIOS,
    PRESETS_HORARIOS,
    etiqueta_de_variable,
)

# Variables de tiempo actual que se piden si el usuario activa --actual.
VARIABLES_TIEMPO_ACTUAL = [
    "temperature_2m",
    "relative_humidity_2m",
    "weather_code",
    "wind_speed_10m",
]


def imprimir_cabecera(texto: str) -> None:
    """Muestra un título de sección subrayado con guiones en consola."""
    print("\n" + texto)
    print("-" * len(texto))


def elegir_lugar(cliente: ClienteOpenMeteo) -> tuple[float, float, str]:
    """
    Pide al usuario un nombre de lugar y devuelve latitud, longitud y etiqueta.

    Si hay varios resultados de geocodificación, permite elegir uno por número.
    """
    while True:
        nombre_introducido = input("\nCiudad o lugar (nombre): ").strip()
        if not nombre_introducido:
            print("Introduce un nombre.")
            continue
        try:
            coincidencias = cliente.buscar_lugar(nombre_introducido)
        except ErrorOpenMeteo as error:
            print(f"Error: {error}")
            continue
        if not coincidencias:
            print("No se encontraron resultados. Prueba otro nombre.")
            continue
        if len(coincidencias) == 1:
            lugar = coincidencias[0]
            print(
                f"Usando: {lugar.nombre_mostrar} "
                f"({lugar.latitud}, {lugar.longitud})"
            )
            return lugar.latitud, lugar.longitud, lugar.nombre_mostrar

        print("\nResultados:")
        for indice, lugar in enumerate(coincidencias, start=1):
            print(
                f"  {indice}. {lugar.nombre_mostrar} — "
                f"lat {lugar.latitud}, lon {lugar.longitud}"
            )
        opcion = input("Elige número (Enter = 1): ").strip() or "1"
        if not opcion.isdigit() or not (1 <= int(opcion) <= len(coincidencias)):
            print("Opción no válida.")
            continue
        lugar = coincidencias[int(opcion) - 1]
        return lugar.latitud, lugar.longitud, lugar.nombre_mostrar


def obtener_coordenadas(argumentos: argparse.Namespace) -> tuple[float, float, str]:
    """
    Obtiene coordenadas desde --latitud/--longitud o mediante búsqueda interactiva.
    """
    if argumentos.latitud is not None and argumentos.longitud is not None:
        return (
            argumentos.latitud,
            argumentos.longitud,
            f"({argumentos.latitud}, {argumentos.longitud})",
        )
    cliente = ClienteOpenMeteo()
    return elegir_lugar(cliente)


def analizar_lista_variables(
    texto: str | None,
    presets: dict[str, list[str]],
    preset_predeterminado: str,
) -> list[str]:
    """
    Interpreta --horario o --diario: preset (basico, viento…) o lista separada por comas.

    Si no se pasa texto, usa el preset predeterminado (por defecto 'basico').
    """
    if not texto:
        return list(presets[preset_predeterminado])
    if texto in presets:
        return list(presets[texto])
    return [variable.strip() for variable in texto.split(",") if variable.strip()]


def mostrar_tiempo_actual(datos: dict) -> None:
    """Imprime las variables del bloque 'current' con unidades y códigos WMO traducidos."""
    actual = datos.get("current")
    if not actual:
        return
    imprimir_cabecera("Tiempo actual")
    unidades = datos.get("current_units") or {}
    filas: list[list[str]] = []
    for clave, valor in actual.items():
        if clave == "time":
            filas.append(["Momento", formatear_marca_tiempo(str(valor))])
            continue
        unidad = unidades.get(clave, "")
        etiqueta = etiqueta_de_variable(clave)
        if clave == "weather_code" and valor is not None:
            descripcion = CODIGOS_TIEMPO_ES.get(int(valor), str(valor))
            filas.append([etiqueta, f"{descripcion} ({valor})"])
        else:
            sufijo = f" {unidad}" if unidad else ""
            filas.append([etiqueta, f"{valor}{sufijo}"])
    imprimir_tabla(["Variable", "Valor"], filas)


def mostrar_tabla_resumen(datos: dict, seccion: str, filas_maximas: int = 8) -> None:
    """
    Muestra datos en tabla: horarios (muestra por franjas del día) o diarios (primeras filas).

    seccion debe ser 'hourly' o 'daily' según el JSON de la API.
    """
    bloque = datos.get(seccion)
    if not bloque:
        return
    marcas_tiempo = bloque.get("time", [])
    nombres_variables = [clave for clave in bloque.keys() if clave != "time"]
    if not marcas_tiempo:
        return

    filas: list[list[str]] = []
    if seccion == "hourly":
        dia = parsear_marca_tiempo(marcas_tiempo[0]).strftime("%d-%m-%Y")
        imprimir_cabecera(
            f"Datos horarios ({dia}): 4 h madrugada, 4 h mañana, "
            f"4 h tarde y 4 h noche"
        )
        encabezados = ["Franja", "Fecha"] + [
            etiqueta_de_variable(nombre) for nombre in nombres_variables
        ]
        for nombre_franja, indice in seleccionar_filas_horarias(marcas_tiempo):
            fila = [nombre_franja, formatear_marca_tiempo(marcas_tiempo[indice])]
            for nombre_variable in nombres_variables:
                valor = bloque[nombre_variable][indice]
                if nombre_variable == "weather_code" and valor is not None:
                    valor = CODIGOS_TIEMPO_ES.get(int(valor), valor)
                fila.append(str(valor))
            filas.append(fila)
    else:
        imprimir_cabecera(f"Datos diarios (primeras {filas_maximas} filas)")
        encabezados = ["Fecha"] + [
            etiqueta_de_variable(nombre) for nombre in nombres_variables
        ]
        for indice in range(min(filas_maximas, len(marcas_tiempo))):
            fila = [formatear_marca_tiempo(marcas_tiempo[indice])]
            for nombre_variable in nombres_variables:
                valor = bloque[nombre_variable][indice]
                if nombre_variable == "weather_code" and valor is not None:
                    valor = CODIGOS_TIEMPO_ES.get(int(valor), valor)
                fila.append(str(valor))
            filas.append(fila)

    imprimir_tabla(encabezados, filas)


def ejecutar_programa(argumentos: argparse.Namespace) -> int:
    """
    Flujo principal: ubicación, petición a la API, resumen en consola y opcionalmente gráfico/JSON.

    Devuelve 0 si todo fue bien, 1 si hubo error de API o red.
    """
    cliente = ClienteOpenMeteo()
    latitud, longitud, nombre_lugar = obtener_coordenadas(argumentos)

    print("\nPresets horarios:", ", ".join(PRESETS_HORARIOS))
    print("Presets diarios:", ", ".join(PRESETS_DIARIOS))
    variables_horarias = analizar_lista_variables(
        argumentos.horario, PRESETS_HORARIOS, "basico"
    )
    incluir_diario = argumentos.diario or argumentos.modo != "solo-horario"
    variables_diarias = (
        analizar_lista_variables(argumentos.diario, PRESETS_DIARIOS, "basico")
        if incluir_diario
        else []
    )

    if argumentos.modo == "solo-diario":
        variables_horarias = []
    if argumentos.modo == "solo-horario":
        variables_diarias = []

    dias_prevision = argumentos.dias
    zona_horaria = argumentos.zona_horaria

    try:
        datos = cliente.obtener_prevision(
            latitud,
            longitud,
            variables_horarias=variables_horarias or None,
            variables_diarias=variables_diarias or None,
            tiempo_actual=VARIABLES_TIEMPO_ACTUAL if argumentos.actual else None,
            dias_prevision=dias_prevision,
            dias_pasados=argumentos.dias_pasados,
            zona_horaria=zona_horaria,
        )
    except ErrorOpenMeteo as error:
        print(f"\nError al consultar: {error}", file=sys.stderr)
        return 1

    url_consulta = cliente.construir_url_prevision(
        latitude=latitud,
        longitude=longitud,
        hourly=variables_horarias or None,
        daily=variables_diarias or None,
        current=VARIABLES_TIEMPO_ACTUAL if argumentos.actual else None,
        forecast_days=dias_prevision,
        past_days=argumentos.dias_pasados,
        timezone=zona_horaria,
    )
    imprimir_cabecera("URL de la consulta (parámetros visibles)")
    print(url_consulta)

    metadatos = {
        "lugar": nombre_lugar,
        "latitud": datos.get("latitude"),
        "longitud": datos.get("longitude"),
        "elevacion": datos.get("elevation"),
        "zona_horaria": datos.get("timezone"),
    }
    imprimir_cabecera("Metadatos")
    imprimir_tabla(
        ["Campo", "Valor"],
        [[clave, str(valor)] for clave, valor in metadatos.items()],
    )

    if argumentos.actual:
        mostrar_tiempo_actual(datos)
    if variables_horarias:
        mostrar_tabla_resumen(datos, "hourly")
    if variables_diarias:
        mostrar_tabla_resumen(datos, "daily")

    if argumentos.archivo_json:
        ruta_json = Path(argumentos.archivo_json)
        ruta_json.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nJSON guardado en: {ruta_json.resolve()}")

    if argumentos.grafico is not None:
        variables_grafico = variables_horarias if variables_horarias else variables_diarias
        seccion = "hourly" if variables_horarias else "daily"
        if not variables_grafico:
            print("\nNo hay variables para graficar.")
        else:
            # Los códigos WMO no son una magnitud continua; no tienen sentido en línea.
            variables_grafico = [
                v for v in variables_grafico if v != "weather_code"
            ]
            if variables_grafico:
                es_mostrar = argumentos.grafico == "mostrar"
                if es_mostrar:
                    ruta_grafico = None
                else:
                    ruta_grafico = construir_ruta_grafico(
                        Path(argumentos.grafico),
                        nombre_lugar,
                        tipo_datos=seccion,
                    )
                graficar_series(
                    datos,
                    seccion,
                    variables_grafico[:4],
                    titulo=f"{nombre_lugar} — previsión",
                    archivo_salida=ruta_grafico,
                    mostrar=es_mostrar,
                )
                if ruta_grafico:
                    print(f"\nGráfico guardado en: {ruta_grafico.resolve()}")

    return 0


def crear_parser() -> argparse.ArgumentParser:
    """Define los argumentos de línea de comandos (nombres y ayuda en español)."""
    parser = argparse.ArgumentParser(
        description="dinquechove: consultas a Open-Meteo sin clave (uso no comercial).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--latitud", type=float, help="Latitud WGS84 (evita la geocodificación interactiva)"
    )
    parser.add_argument("--longitud", type=float, help="Longitud WGS84")
    parser.add_argument(
        "--horario",
        help="Variables horarias (preset o lista separada por comas): "
        + ", ".join(PRESETS_HORARIOS),
    )
    parser.add_argument(
        "--diario",
        help="Variables diarias (preset o lista separada por comas): "
        + ", ".join(PRESETS_DIARIOS),
    )
    parser.add_argument(
        "--modo",
        choices=("ambos", "solo-horario", "solo-diario"),
        default="ambos",
        help="Qué bloques de datos solicitar a la API",
    )
    parser.add_argument("--dias", type=int, default=7, help="Días de previsión (máx. 16)")
    parser.add_argument(
        "--dias-pasados", type=int, default=0, help="Días ya transcurridos a incluir"
    )
    parser.add_argument(
        "--zona-horaria", default="auto", help="Zona horaria (p. ej. Europe/Madrid)"
    )
    parser.add_argument(
        "--actual", action="store_true", help="Incluir el bloque de tiempo actual"
    )
    parser.add_argument("--json", dest="archivo_json", metavar="ARCHIVO", help="Guardar JSON")
    parser.add_argument(
        "--grafico",
        nargs="?",
        const="mostrar",
        metavar="ARCHIVO",
        help="Mostrar gráfico (sin valor) o guardar PNG; el nombre final incluye el lugar",
    )
    return parser


def main() -> None:
    """Punto de entrada: parsea argumentos y ejecuta el flujo principal."""
    parser = crear_parser()
    argumentos = parser.parse_args()
    if (argumentos.latitud is None) ^ (argumentos.longitud is None):
        parser.error("--latitud y --longitud deben usarse juntos.")
    sys.exit(ejecutar_programa(argumentos))


if __name__ == "__main__":
    main()
