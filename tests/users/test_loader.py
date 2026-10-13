"""Tests del módulo loader."""

import pytest

from users_app.exceptions import ArchivoVacioError, FaltanColumnasError, NoHayArchivoError
from users_app.loader import REQUIRED_COLUMNS, load_users

HEADER = ",".join(REQUIRED_COLUMNS)
ROW = (
    "1,Ana Ruiz,30,Female,ana@mail.com,600111222,"
    '"1 Main St, Springfield, WA 12345",http://img.com/1,'
    "2024-04-22 15:38:34,2024-04-22 15:38:34"
)


@pytest.mark.integration
def test_carga_el_archivo_real(data_file):
    df = load_users(data_file)
    assert len(df) == 10000
    assert list(df.columns) == REQUIRED_COLUMNS


def test_carga_un_csv_pequeno(tmp_path):
    # Arrange: creamos un CSV con un solo usuario
    archivo = tmp_path / "users.csv"
    archivo.write_text(HEADER + "\n" + ROW + "\n")
    # Act: lo cargamos
    df = load_users(archivo)
    # Assert: comprobamos el resultado
    assert len(df) == 1
    assert df.loc[0, "name"] == "Ana Ruiz"


def test_acepta_ruta_como_texto(tmp_path):
    archivo = tmp_path / "users.csv"
    archivo.write_text(HEADER + "\n" + ROW + "\n")
    df = load_users(str(archivo))
    assert len(df) == 1


def test_archivo_inexistente(tmp_path):
    with pytest.raises(NoHayArchivoError):
        load_users(tmp_path / "no_existe.csv")


def test_archivo_vacio(tmp_path):
    archivo = tmp_path / "vacio.csv"
    archivo.write_text("")
    with pytest.raises(ArchivoVacioError):
        load_users(archivo)


def test_solo_cabecera(tmp_path):
    archivo = tmp_path / "solo_cabecera.csv"
    archivo.write_text(HEADER + "\n")
    with pytest.raises(ArchivoVacioError):
        load_users(archivo)


def test_faltan_columnas(tmp_path):
    archivo = tmp_path / "incompleto.csv"
    archivo.write_text("id,name\n1,Ana\n")
    with pytest.raises(FaltanColumnasError) as info:
        load_users(archivo)
    assert "email" in str(info.value)
