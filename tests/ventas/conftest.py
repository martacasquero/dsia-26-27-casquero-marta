"""Fixtures compartidas por los tests de ventas_app."""

from pathlib import Path

import pandas as pd
import pytest

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "ventas.csv"


@pytest.fixture
def ventas_mini():
    """Cuatro ventas en memoria: 2 válidas y 2 inválidas (unidades nula y precio negativo).

        fecha       region  producto  unidades  precio  cliente   importe
        2026-01-01  Norte   A         2         10.0    C1        20.0
        2026-01-02  Sur     B         None      20.0    C2        (inválida)
        2026-01-03  Norte   A         5         -1.0    C1        (inválida)
        2026-01-04  Sur     B         3         20.0    C1        60.0
    """
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "region": ["Norte", "Sur", "Norte", "Sur"],
        "producto": ["A", "B", "A", "B"],
        "unidades": [2, None, 5, 3],
        "precio_unitario": [10.0, 20.0, -1.0, 20.0],
        "cliente_id": ["C1", "C2", "C1", "C1"],
    })


@pytest.fixture
def csv_mini(tmp_path, ventas_mini):
    """Escribe ventas_mini en un CSV temporal y devuelve su ruta."""
    ruta = tmp_path / "ventas.csv"
    ventas_mini.to_csv(ruta, index=False)
    return ruta


@pytest.fixture
def data_file():
    """Ruta al CSV real del curso (para los tests de integración)."""
    return DATA_FILE
