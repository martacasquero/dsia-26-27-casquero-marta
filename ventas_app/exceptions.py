"""Excepciones de dominio del pipeline de ventas.

Jerarquía:
    VentasError
    ├── DataLoadError     no se pudo cargar el archivo de ventas
    └── ValidationError   los datos no cumplen las reglas de negocio
"""


class VentasError(Exception):
    """Error base: todas las excepciones del pipeline de ventas heredan de esta."""


class DataLoadError(VentasError):
    """Error al cargar los datos de origen (archivo inexistente, vacío o sin columnas)."""


class ValidationError(VentasError):
    """Los datos no cumplen las reglas de negocio (se usa en el modo estricto)."""
