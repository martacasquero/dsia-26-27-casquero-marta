"""Métricas de negocio sobre ventas ya validadas (necesitan la columna `importe`)."""

import pandas as pd


def importe_total(validos: pd.DataFrame) -> float:
    """Suma del importe de todas las ventas válidas."""
    return round(float(validos["importe"].sum()), 2)


def importe_por_region(validos: pd.DataFrame) -> pd.Series:
    """Importe total por región, de mayor a menor."""
    return validos.groupby("region")["importe"].sum().round(2).sort_values(ascending=False)


def importe_por_producto(validos: pd.DataFrame) -> pd.Series:
    """Importe total por producto, de mayor a menor."""
    return validos.groupby("producto")["importe"].sum().round(2).sort_values(ascending=False)


def top_productos(validos: pd.DataFrame, n: int = 3) -> pd.Series:
    """Los `n` productos con más importe."""
    return importe_por_producto(validos).head(n)


def clientes_recurrentes(validos: pd.DataFrame) -> pd.Series:
    """Clientes con más de una compra válida y su número de compras (de más a menos)."""
    compras = validos["cliente_id"].value_counts()
    return compras[compras > 1]


def resumen_calidad(frame: pd.DataFrame, validos: pd.DataFrame, errores: pd.DataFrame) -> dict:
    """Resumen de calidad de datos (el contenido de calidad_datos.json del E1)."""
    return {
        "filas_totales": int(len(frame)),
        "filas_validas": int(len(validos)),
        "filas_invalidas": int(len(errores)),
        "importe_total": importe_total(validos),
    }
