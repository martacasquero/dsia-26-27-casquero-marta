"""Validación de ventas: separa filas válidas e inválidas con reglas explícitas.

Reglas (las del ejercicio E1 del curso):
    - `unidades` numérica y > 0
    - `precio_unitario` numérico y > 0
A las válidas se les añade `importe = unidades * precio_unitario`.

Checkpoint con data/ventas.csv: 140 válidas y 10 inválidas.
"""

import pandas as pd

from ventas_app.exceptions import ValidationError

MIN_UNIDADES = 0          # las unidades deben ser estrictamente mayores
MIN_PRECIO_UNITARIO = 0   # el precio debe ser estrictamente mayor


def _motivos(unidades, precio):
    """Devuelve una serie con el motivo de invalidez de cada fila ("" si es válida)."""
    motivos = pd.Series("", index=unidades.index)
    reglas = [
        (unidades.isna(), "unidades no numéricas o vacías"),
        (unidades <= MIN_UNIDADES, "unidades <= 0"),
        (precio.isna(), "precio no numérico o vacío"),
        (precio <= MIN_PRECIO_UNITARIO, "precio <= 0"),
    ]
    for mascara, texto in reglas:
        motivos[mascara] = motivos[mascara] + texto + "; "
    return motivos.str.rstrip("; ")


def validar_ventas(frame: pd.DataFrame, estricto: bool = False):
    """Separa las ventas en válidas e inválidas.

    No modifica el DataFrame original (trabaja sobre una copia).

    Args:
        frame: DataFrame devuelto por el loader.
        estricto: si es True, lanza ValidationError cuando hay alguna fila inválida.

    Returns:
        Tupla (validos, errores):
            validos: filas que cumplen las reglas, con la columna `importe`.
            errores: filas que no las cumplen, con la columna `motivo`.

    Raises:
        ValidationError: solo en modo estricto, si hay filas inválidas.
    """
    work = frame.copy()
    work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
    work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

    ok = (
        work["unidades"].notna()
        & (work["unidades"] > MIN_UNIDADES)
        & work["precio_unitario"].notna()
        & (work["precio_unitario"] > MIN_PRECIO_UNITARIO)
    )

    validos = work.loc[ok].copy()
    errores = work.loc[~ok].copy()
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]
    errores["motivo"] = _motivos(errores["unidades"], errores["precio_unitario"])

    if estricto and not errores.empty:
        raise ValidationError(f"{len(errores)} filas no cumplen las reglas de validación")

    return validos, errores
