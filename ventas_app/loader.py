"""Carga de los datos de ventas.

Sigue el patrón Repository visto en clase: el resto del código solo pide
"dame las ventas" (`load()`) y no sabe de dónde vienen.
"""

from pathlib import Path
from typing import Protocol

import pandas as pd

from ventas_app.exceptions import DataLoadError

COLUMNAS_OBLIGATORIAS = [
    "fecha", "region", "producto", "unidades", "precio_unitario", "cliente_id",
]


class SalesRepository(Protocol):
    """Contrato de cualquier fuente de ventas: devuelve un DataFrame o lanza DataLoadError."""

    def load(self) -> pd.DataFrame: ...


class CsvSalesRepository:
    """Lee las ventas desde un archivo CSV."""

    def __init__(self, path):
        """Args: path: ruta al CSV (str o Path)."""
        self._path = Path(path)

    def load(self) -> pd.DataFrame:
        """Lee el CSV y comprueba que tiene las columnas obligatorias.

        Returns:
            DataFrame con una fila por venta, sin validar todavía.

        Raises:
            DataLoadError: si el archivo no existe, está vacío, no tiene filas
                o le falta alguna columna de COLUMNAS_OBLIGATORIAS.
        """
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")

        try:
            frame = pd.read_csv(self._path)
        except pd.errors.EmptyDataError as e:
            raise DataLoadError(f"El fichero está vacío: {self._path}") from e

        faltan = [col for col in COLUMNAS_OBLIGATORIAS if col not in frame.columns]
        if faltan:
            raise DataLoadError(f"Faltan columnas: {', '.join(faltan)}")

        if frame.empty:
            raise DataLoadError(f"El fichero no tiene ventas: {self._path}")

        return frame


def cargar_ventas(path) -> pd.DataFrame:
    """Atajo para leer un CSV de ventas: CsvSalesRepository(path).load()."""
    return CsvSalesRepository(path).load()
