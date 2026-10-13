"""Tests del módulo cli (sin depender de rutas de tu ordenador)."""

import runpy
import sys

import pandas as pd
import pytest

from users_app.cli import ARCHIVO_POR_DEFECTO, main, parse_args


def test_parse_args_por_defecto():
    args = parse_args([])
    assert args.archivo == ARCHIVO_POR_DEFECTO
    assert args.top == 5
    assert args.guardar_invalidos is None


def test_parse_args_personalizados():
    args = parse_args(["--archivo", "otro.csv", "--top", "3"])
    assert args.archivo == "otro.csv"
    assert args.top == 3


def test_main_con_csv_valido(csv_valido, capsys):
    codigo = main(["--archivo", str(csv_valido)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Válidas: 3" in salida
    assert "Inválidas: 0" in salida
    assert "Usuarios analizados: 3" in salida


def test_main_archivo_inexistente(tmp_path, capsys):
    codigo = main(["--archivo", str(tmp_path / "no_existe.csv")])
    errores = capsys.readouterr().err
    assert codigo == 1
    assert "Error" in errores


def test_main_guarda_invalidos(tmp_path, df_valido, capsys):
    df_valido.loc[0, "gender"] = "Woman"
    entrada = tmp_path / "users.csv"
    salida = tmp_path / "salida" / "invalidos.csv"   # la carpeta aún no existe
    df_valido.to_csv(entrada, index=False)

    codigo = main(["--archivo", str(entrada), "--guardar-invalidos", str(salida)])

    assert codigo == 0
    invalidos = pd.read_csv(salida)
    assert invalidos["id"].tolist() == [1]
    assert "género" in invalidos.loc[0, "motivo"]


def test_main_sin_usuarios_validos(tmp_path, df_valido, capsys):
    df_valido["gender"] = "Woman"
    entrada = tmp_path / "users.csv"
    df_valido.to_csv(entrada, index=False)
    codigo = main(["--archivo", str(entrada)])
    assert codigo == 0
    assert "No hay usuarios válidos" in capsys.readouterr().out


def test_python_m_users_app(csv_valido, monkeypatch, capsys):
    """Smoke test de 'python -m users_app': ejecuta __main__.py de verdad."""
    monkeypatch.setattr(sys, "argv", ["users_app", "--archivo", str(csv_valido)])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("users_app", run_name="__main__")
    assert info.value.code == 0
    assert "Válidas: 3" in capsys.readouterr().out


@pytest.mark.integration
def test_main_con_datos_reales(data_file, capsys):
    codigo = main(["--archivo", str(data_file)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Filas leídas: 10000" in salida
    assert "Válidas: 10000" in salida
