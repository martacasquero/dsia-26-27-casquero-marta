"""Tests del módulo loader de ventas."""

import pytest

from ventas_app.exceptions import DataLoadError, VentasError
from ventas_app.loader import COLUMNAS_OBLIGATORIAS, CsvSalesRepository, cargar_ventas


def test_load_csv_ok(csv_mini):
    # Arrange
    repo = CsvSalesRepository(csv_mini)
    # Act
    frame = repo.load()
    # Assert
    assert len(frame) == 4
    assert list(frame.columns) == COLUMNAS_OBLIGATORIAS


def test_cargar_ventas_atajo(csv_mini):
    assert len(cargar_ventas(csv_mini)) == 4


def test_load_path_inexistente_raises_dataloaderror(tmp_path):
    with pytest.raises(DataLoadError, match="No existe"):
        CsvSalesRepository(tmp_path / "no_existe.csv").load()


def test_load_fichero_vacio(tmp_path):
    ruta = tmp_path / "vacio.csv"
    ruta.write_text("", encoding="utf-8")
    with pytest.raises(DataLoadError, match="vacío"):
        cargar_ventas(ruta)


def test_load_solo_cabecera(tmp_path):
    ruta = tmp_path / "cabecera.csv"
    ruta.write_text(",".join(COLUMNAS_OBLIGATORIAS) + "\n", encoding="utf-8")
    with pytest.raises(DataLoadError, match="no tiene ventas"):
        cargar_ventas(ruta)


def test_load_faltan_columnas(tmp_path):
    ruta = tmp_path / "incompleto.csv"
    ruta.write_text("unidades,precio_unitario\n1,10\n", encoding="utf-8")
    with pytest.raises(DataLoadError, match="region"):
        cargar_ventas(ruta)


def test_dataloaderror_es_ventaserror():
    assert issubclass(DataLoadError, VentasError)


@pytest.mark.integration
def test_load_csv_del_curso(data_file):
    frame = cargar_ventas(data_file)
    assert frame.shape == (150, 6)
