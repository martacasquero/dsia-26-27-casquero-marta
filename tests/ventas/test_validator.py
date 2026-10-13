"""Tests del módulo validator de ventas."""

import pandas as pd
import pytest

from ventas_app.exceptions import ValidationError
from ventas_app.loader import cargar_ventas
from ventas_app.validator import validar_ventas


def _una_venta(unidades, precio):
    """DataFrame de una sola venta con las unidades y el precio indicados."""
    return pd.DataFrame({
        "fecha": ["2026-01-01"], "region": ["Norte"], "producto": ["A"],
        "unidades": [unidades], "precio_unitario": [precio], "cliente_id": ["C1"],
    })


def test_validar_ventas_cuenta_validos_e_invalidos(ventas_mini):
    validos, errores = validar_ventas(ventas_mini)
    assert len(validos) == 2
    assert len(errores) == 2


def test_validos_tienen_importe(ventas_mini):
    validos, _ = validar_ventas(ventas_mini)
    assert validos["importe"].tolist() == [20.0, 60.0]


def test_errores_tienen_motivo(ventas_mini):
    _, errores = validar_ventas(ventas_mini)
    assert errores["motivo"].tolist() == ["unidades no numéricas o vacías", "precio <= 0"]


def test_motivo_acumula_varias_reglas():
    _, errores = validar_ventas(_una_venta(0, -1.0))
    assert errores["motivo"].iloc[0] == "unidades <= 0; precio <= 0"


def test_no_modifica_el_original(ventas_mini):
    original = ventas_mini.copy()
    validar_ventas(ventas_mini)
    pd.testing.assert_frame_equal(ventas_mini, original)


@pytest.mark.parametrize("unidades", [0, -1, None, "na", "abc"])
def test_unidades_no_validas_van_a_errores(unidades):
    validos, errores = validar_ventas(_una_venta(unidades, 10.0))
    assert len(validos) == 0
    assert len(errores) == 1


@pytest.mark.parametrize("precio", [0, -1, -32.0, None])
def test_precio_no_positivo_no_es_valido(precio):
    validos, errores = validar_ventas(_una_venta(5, precio))
    assert len(validos) == 0
    assert len(errores) == 1


@pytest.mark.parametrize(
    ("unidades", "precio", "importe"),
    [(1, 0.01, 0.01), ("3", "19.5", 58.5), (25, 120.0, 3000.0)],
)
def test_bordes_validos_y_su_importe(unidades, precio, importe):
    validos, errores = validar_ventas(_una_venta(unidades, precio))
    assert len(errores) == 0
    assert validos["importe"].iloc[0] == pytest.approx(importe)


def test_modo_estricto_lanza_validationerror(ventas_mini):
    with pytest.raises(ValidationError, match="2 filas"):
        validar_ventas(ventas_mini, estricto=True)


def test_modo_estricto_sin_errores_no_lanza():
    validos, errores = validar_ventas(_una_venta(5, 10.0), estricto=True)
    assert len(validos) == 1
    assert len(errores) == 0


@pytest.mark.integration
def test_checkpoint_csv_del_curso(data_file):
    """Checkpoint del enunciado: 140 válidas y 10 inválidas."""
    validos, errores = validar_ventas(cargar_ventas(data_file))
    assert len(validos) == 140
    assert len(errores) == 10
