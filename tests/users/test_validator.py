"""Tests del módulo validator."""

import pytest

from users_app.exceptions import (
    DireccionInvalidaError,
    EdadInvalidaError,
    EmailInvalidoError,
    GeneroInvalidoError,
    IdDuplicadoError,
    ValidacionError,
    ValoresNulosError,
)
from users_app.loader import load_users
from users_app.validator import separar_validos, validate_users


# ---------- Modo estricto: validate_users ----------

def test_df_valido_pasa(df_valido):
    assert validate_users(df_valido) is df_valido


def test_phone_vacio_esta_permitido(df_valido):
    df_valido.loc[0, "phone"] = None
    validate_users(df_valido)  # si no lanza ningún error, el test pasa


def test_nulo_en_columna_obligatoria(df_valido):
    df_valido.loc[1, "name"] = None
    with pytest.raises(ValoresNulosError, match="vacíos"):
        validate_users(df_valido)


def test_id_duplicado(df_valido):
    df_valido.loc[2, "id"] = 1
    with pytest.raises(IdDuplicadoError):
        validate_users(df_valido)


@pytest.mark.parametrize("email", ["sin-arroba.com", "ana@", "ana@mail", "a na@mail.com"])
def test_email_mal_formado(df_valido, email):
    df_valido.loc[0, "email"] = email
    with pytest.raises(EmailInvalidoError, match="formato"):
        validate_users(df_valido)


def test_email_repetido(df_valido):
    df_valido.loc[1, "email"] = "ana@mail.com"
    with pytest.raises(EmailInvalidoError, match="repetido"):
        validate_users(df_valido)


@pytest.mark.parametrize("edad", [17, 66, 0, -1, "treinta"])
def test_edad_invalida(df_valido, edad):
    df_valido["age"] = df_valido["age"].astype(object)
    df_valido.loc[0, "age"] = edad
    with pytest.raises(EdadInvalidaError):
        validate_users(df_valido)


def test_genero_invalido(df_valido):
    df_valido.loc[0, "gender"] = "Woman"
    with pytest.raises(GeneroInvalidoError):
        validate_users(df_valido)


def test_direccion_sin_codigo_postal(df_valido):
    df_valido.loc[0, "address"] = "1 Main St, Springfield"
    with pytest.raises(DireccionInvalidaError):
        validate_users(df_valido)


def test_todas_heredan_de_validacion_error(df_valido):
    df_valido.loc[0, "gender"] = "Woman"
    with pytest.raises(ValidacionError):
        validate_users(df_valido)


def test_mensaje_incluye_el_id(df_valido):
    df_valido.loc[2, "age"] = 99
    with pytest.raises(EdadInvalidaError, match="ids: 3"):
        validate_users(df_valido)


# ---------- Modo fila a fila: separar_validos ----------

def test_separar_todo_valido(df_valido):
    validos, invalidos = separar_validos(df_valido)
    assert len(validos) == 3
    assert len(invalidos) == 0


def test_separar_filas_validas_e_invalidas(df_valido):
    df_valido.loc[0, "gender"] = "Woman"
    df_valido.loc[2, "address"] = "sin codigo postal"
    validos, invalidos = separar_validos(df_valido)
    assert validos["id"].tolist() == [2]
    assert invalidos["id"].tolist() == [1, 3]


@pytest.mark.parametrize("edad", [0, -1, 17, 66, None])
def test_bordes_de_edad_invalidos(df_valido, edad):
    df_valido["age"] = df_valido["age"].astype(object)
    df_valido.loc[0, "age"] = edad
    validos, invalidos = separar_validos(df_valido)
    assert len(invalidos) == 1
    assert len(validos) == 2


@pytest.mark.parametrize("edad", [18, 65])
def test_bordes_de_edad_validos(df_valido, edad):
    df_valido.loc[0, "age"] = edad
    _, invalidos = separar_validos(df_valido)
    assert len(invalidos) == 0


def test_motivo_acumula_varias_reglas(df_valido):
    df_valido.loc[0, "gender"] = "Woman"
    df_valido.loc[0, "age"] = 99
    _, invalidos = separar_validos(df_valido)
    motivo = invalidos.loc[0, "motivo"]
    assert "edad" in motivo
    assert "género" in motivo


def test_separar_no_modifica_el_original(df_valido):
    columnas_antes = list(df_valido.columns)
    separar_validos(df_valido)
    assert list(df_valido.columns) == columnas_antes


# ---------- Integración con el CSV real ----------

@pytest.mark.integration
def test_datos_reales(data_file):
    df = load_users(data_file)
    validos, invalidos = separar_validos(df)
    assert len(validos) == 10000
    assert len(invalidos) == 0
    assert validate_users(df) is df
