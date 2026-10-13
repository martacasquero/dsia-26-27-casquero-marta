"""Tests del módulo metrics de ventas (resultados conocidos sobre ventas_mini)."""

import pytest

from ventas_app.metrics import (
    clientes_recurrentes,
    importe_por_producto,
    importe_por_region,
    importe_total,
    resumen_calidad,
    top_productos,
)
from ventas_app.validator import validar_ventas

# ventas_mini válidas: (Norte, A, C1, importe 20.0) y (Sur, B, C1, importe 60.0)


@pytest.fixture
def validos(ventas_mini):
    """Solo las ventas válidas de ventas_mini (ya con la columna importe)."""
    validos, _ = validar_ventas(ventas_mini)
    return validos


def test_importe_total(validos):
    assert importe_total(validos) == 80.0


def test_importe_por_region(validos):
    resultado = importe_por_region(validos)
    assert resultado.to_dict() == {"Sur": 60.0, "Norte": 20.0}
    assert list(resultado.index) == ["Sur", "Norte"]   # de mayor a menor


def test_importe_por_producto(validos):
    assert importe_por_producto(validos).to_dict() == {"B": 60.0, "A": 20.0}


def test_top_productos_limita_n(validos):
    assert top_productos(validos, n=1).to_dict() == {"B": 60.0}


def test_clientes_recurrentes(validos):
    assert clientes_recurrentes(validos).to_dict() == {"C1": 2}


def test_resumen_calidad(ventas_mini):
    validos, errores = validar_ventas(ventas_mini)
    assert resumen_calidad(ventas_mini, validos, errores) == {
        "filas_totales": 4,
        "filas_validas": 2,
        "filas_invalidas": 2,
        "importe_total": 80.0,
    }
