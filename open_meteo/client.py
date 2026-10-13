"""Peticiones HTTP a Open-Meteo y geocodificación de lugares."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests

# Endpoints públicos de la API (documentación oficial Open-Meteo).
URL_PREVISION = "https://api.open-meteo.com/v1/forecast"
URL_GEOCODIFICACION = "https://geocoding-api.open-meteo.com/v1/search"
TIEMPO_ESPERA_PREDETERMINADO = 30


class ErrorOpenMeteo(Exception):
    """Se lanza cuando falla la red o la API devuelve un error JSON."""


@dataclass(frozen=True)
class ResultadoGeocodificacion:
    """Un lugar encontrado al buscar por nombre."""

    nombre: str
    latitud: float
    longitud: float
    pais: str
    region: str | None
    zona_horaria: str | None

    @property
    def nombre_mostrar(self) -> str:
        """Nombre completo para consola: ciudad, región y país."""
        partes = [self.nombre]
        if self.region:
            partes.append(self.region)
        if self.pais:
            partes.append(self.pais)
        return ", ".join(partes)


class ClienteOpenMeteo:
    """
    Cliente sin autenticación para el plan gratuito no comercial.

    Encapsula las peticiones GET y la validación básica de respuestas.
    """

    def __init__(self, tiempo_espera: int = TIEMPO_ESPERA_PREDETERMINADO) -> None:
        """
        Crea el cliente reutilizando una sesión HTTP.

        tiempo_espera: segundos máximos de espera por petición.
        """
        self.tiempo_espera = tiempo_espera
        self._sesion = requests.Session()
        self._sesion.headers.update(
            {"User-Agent": "OpenMeteo-Python-Practice/1.0 (educational)"}
        )

    def buscar_lugar(self, nombre: str, cantidad: int = 5) -> list[ResultadoGeocodificacion]:
        """
        Busca coordenadas a partir del nombre de una ciudad o lugar.

        Usa la API de geocodificación de Open-Meteo. Devuelve hasta `cantidad`
        resultados ordenados por relevancia.
        """
        parametros = {
            "name": nombre.strip(),
            "count": cantidad,
            "language": "es",
            "format": "json",
        }
        datos = self._obtener_json(URL_GEOCODIFICACION, parametros)
        resultados: list[ResultadoGeocodificacion] = []
        for elemento in datos.get("results") or []:
            resultados.append(
                ResultadoGeocodificacion(
                    nombre=elemento.get("name", ""),
                    latitud=float(elemento["latitude"]),
                    longitud=float(elemento["longitude"]),
                    pais=elemento.get("country", ""),
                    region=elemento.get("admin1"),
                    zona_horaria=elemento.get("timezone"),
                )
            )
        return resultados

    def obtener_prevision(
        self,
        latitud: float,
        longitud: float,
        *,
        variables_horarias: list[str] | None = None,
        variables_diarias: list[str] | None = None,
        tiempo_actual: list[str] | None = None,
        dias_prevision: int = 7,
        dias_pasados: int = 0,
        zona_horaria: str = "auto",
        unidad_temperatura: str = "celsius",
        unidad_viento: str = "kmh",
        unidad_precipitacion: str = "mm",
    ) -> dict[str, Any]:
        """
        Obtiene la previsión meteorológica para unas coordenadas WGS84.

        variables_horarias / variables_diarias / tiempo_actual: listas con nombres
        de campos de la API (en inglés). Al menos uno de los tres bloques debe
        indicarse. dias_prevision puede ir de 1 a 16; dias_pasados incluye días
        ya transcurridos en la misma respuesta.
        """
        parametros: dict[str, Any] = {
            "latitude": latitud,
            "longitude": longitud,
            "forecast_days": dias_prevision,
            "past_days": dias_pasados,
            "timezone": zona_horaria,
            "temperature_unit": unidad_temperatura,
            "wind_speed_unit": unidad_viento,
            "precipitation_unit": unidad_precipitacion,
        }
        if variables_horarias:
            parametros["hourly"] = ",".join(variables_horarias)
        if variables_diarias:
            parametros["daily"] = ",".join(variables_diarias)
        if tiempo_actual:
            parametros["current"] = ",".join(tiempo_actual)

        if not variables_horarias and not variables_diarias and not tiempo_actual:
            raise ErrorOpenMeteo(
                "Debes solicitar al menos variables horarias, diarias o tiempo actual."
            )

        return self._obtener_json(URL_PREVISION, parametros)

    def construir_url_prevision(self, **argumentos: Any) -> str:
        """
        Construye la URL de previsión con parámetros visibles (para aprendizaje).

        Acepta los mismos nombres que usarías en la query string de la API.
        Las listas de variables se unen con comas. Se omiten valores None.
        """
        parametros = {clave: valor for clave, valor in argumentos.items() if valor is not None}
        for clave in ("hourly", "daily", "current"):
            if clave in parametros and isinstance(parametros[clave], list):
                parametros[clave] = ",".join(parametros[clave])
        return f"{URL_PREVISION}?{urlencode(parametros)}"

    def _obtener_json(self, url: str, parametros: dict[str, Any]) -> dict[str, Any]:
        """
        Ejecuta GET, comprueba el código HTTP y parsea JSON.

        Si la API responde con {"error": true, "reason": "..."}, lanza ErrorOpenMeteo.
        """
        try:
            respuesta = self._sesion.get(url, params=parametros, timeout=self.tiempo_espera)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except requests.RequestException as error:
            raise ErrorOpenMeteo(f"Error de red: {error}") from error

        if datos.get("error"):
            raise ErrorOpenMeteo(datos.get("reason", "Error desconocido de la API"))
        return datos
