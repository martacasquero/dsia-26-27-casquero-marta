"""Carga del dataset de usuarios."""

from pathlib import Path

import pandas as pd

from users_app.exceptions import (
    ArchivoVacioError,
    FaltanColumnasError,
    NoHayArchivoError,
)

REQUIRED_COLUMNS = [
    "id", "name", "age", "gender", "email", "phone",
    "address", "profile_picture", "created_at", "updated_at",
]


def load_users(path):
    """Lee el CSV de usuarios y lo devuelve como un DataFrame.

    Solo comprueba que el archivo se puede leer y tiene las columnas
    esperadas; las reglas de negocio se comprueban en validator.

    Args:
        path: ruta al archivo CSV (str o Path).

    Returns:
        pd.DataFrame con una fila por usuario.

    Raises:
        NoHayArchivoError: si el archivo no existe.
        ArchivoVacioError: si el archivo está vacío o no tiene filas.
        FaltanColumnasError: si falta alguna columna de REQUIRED_COLUMNS.
    """
    path = Path(path)
    if not path.exists():
        raise NoHayArchivoError(f"No existe el archivo: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as e:
        raise ArchivoVacioError(f"El archivo está vacío: {path}") from e

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise FaltanColumnasError(f"Faltan columnas: {', '.join(missing)}")

    if df.empty:
        raise ArchivoVacioError(f"El archivo no tiene usuarios: {path}")

    return df
