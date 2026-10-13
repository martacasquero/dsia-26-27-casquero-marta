"""Tests del módulo metrics (con datos en memoria y resultados conocidos)."""

import pytest

from users_app.metrics import (
    ETIQUETAS_TRAMOS,
    InformeUsuarios,
    edad_media_por_genero,
    extraer_estado,
    top_dominios_email,
    usuarios_por_estado,
    usuarios_por_genero,
    usuarios_por_tramo_edad,
)

# Recordatorio de df_valido (definido en conftest.py):
#   id  age  gender  email            estado
#   1   30   Female  ana@mail.com     WA
#   2   18   Man     luis@gmail.com   DE
#   3   65   Female  eva@gmail.com    WA


def test_extraer_estado(df_valido):
    assert extraer_estado(df_valido).tolist() == ["WA", "DE", "WA"]


def test_usuarios_por_estado(df_valido):
    resultado = usuarios_por_estado(df_valido)
    assert resultado.to_dict() == {"WA": 2, "DE": 1}


def test_usuarios_por_estado_top(df_valido):
    resultado = usuarios_por_estado(df_valido, top=1)
    assert resultado.to_dict() == {"WA": 2}


def test_usuarios_por_genero(df_valido):
    assert usuarios_por_genero(df_valido).to_dict() == {"Female": 2, "Man": 1}


def test_edad_media_por_genero(df_valido):
    resultado = edad_media_por_genero(df_valido)
    assert resultado["Female"] == 47.5   # (30 + 65) / 2
    assert resultado["Man"] == 18


@pytest.mark.parametrize(
    "edad, tramo",
    [(18, "18-24"), (24, "18-24"), (25, "25-34"), (44, "35-44"), (55, "55-65"), (65, "55-65")],
)
def test_tramo_de_cada_edad(df_valido, edad, tramo):
    df_valido.loc[0, "age"] = edad
    df = df_valido.iloc[[0]]          # nos quedamos solo con esa fila
    resultado = usuarios_por_tramo_edad(df)
    assert resultado[tramo] == 1
    assert resultado.sum() == 1


def test_tramos_salen_todos_y_en_orden(df_valido):
    resultado = usuarios_por_tramo_edad(df_valido)
    assert list(resultado.index) == ETIQUETAS_TRAMOS
    assert resultado.to_dict() == {"18-24": 1, "25-34": 1, "35-44": 0, "45-54": 0, "55-65": 1}


def test_top_dominios_email(df_valido):
    assert top_dominios_email(df_valido).to_dict() == {"gmail.com": 2, "mail.com": 1}


def test_informe_desde_dataframe(df_valido):
    informe = InformeUsuarios.desde_dataframe(df_valido)
    assert informe.total == 3
    assert informe.edad_media == pytest.approx(37.7)   # (30 + 18 + 65) / 3
    assert informe.top_estados == {"WA": 2, "DE": 1}


def test_informe_como_texto(df_valido):
    texto = InformeUsuarios.desde_dataframe(df_valido).como_texto()
    assert "Usuarios analizados: 3" in texto
    assert "WA: 2" in texto
    assert "gmail.com: 2" in texto
