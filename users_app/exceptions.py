"""Excepciones de dominio del proyecto users.

Jerarquía:
    UsersError
    ├── NoHayArchivoError
    ├── ArchivoVacioError
    ├── FaltanColumnasError
    └── ValidacionError
        ├── ValoresNulosError
        ├── IdDuplicadoError
        ├── EmailInvalidoError
        ├── EdadInvalidaError
        ├── GeneroInvalidoError
        └── DireccionInvalidaError
"""


class UsersError(Exception):
    """Error base: todas las excepciones del proyecto heredan de esta."""


# --- Errores de carga (loader) ---

class NoHayArchivoError(UsersError):
    """El archivo de datos no existe en la ruta indicada."""


class ArchivoVacioError(UsersError):
    """El archivo existe pero no contiene ningún usuario."""


class FaltanColumnasError(UsersError):
    """Al archivo le faltan columnas obligatorias."""


# --- Errores de validación (validator) ---

class ValidacionError(UsersError):
    """Error base de validación: los datos no cumplen una regla."""


class ValoresNulosError(ValidacionError):
    """Hay celdas vacías en columnas obligatorias."""


class IdDuplicadoError(ValidacionError):
    """Hay ids repetidos."""


class EmailInvalidoError(ValidacionError):
    """Hay emails con formato incorrecto o repetidos."""


class EdadInvalidaError(ValidacionError):
    """Hay edades que no son números o están fuera de rango."""


class GeneroInvalidoError(ValidacionError):
    """Hay valores de género no permitidos."""


class DireccionInvalidaError(ValidacionError):
    """Hay direcciones sin estado y código postal."""
