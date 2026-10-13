"""Tests del módulo cli de ventas (sin depender de rutas de tu máquina)."""

import json
import runpy
import sys

import pandas as pd
import pytest

from ventas_app.cli import ENTRADA_POR_DEFECTO, ejecutar, main, parse_args


class FakeSalesRepository:
    """Repositorio en memoria: cumple el Protocol SalesRepository sin leer disco."""

    def __init__(self, frame):
        self._frame = frame

    def load(self):
        return self._frame


def test_parse_args_por_defecto():
    args = parse_args([])
    assert args.input == ENTRADA_POR_DEFECTO
    assert args.top == 3
    assert args.estricto is False


def test_main_smoke(csv_mini, capsys):
    codigo = main(["--input", str(csv_mini)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Válidas: 2 | Inválidas: 2" in salida
    assert "Importe total: 80.00" in salida


def test_main_escribe_salidas(csv_mini, tmp_path):
    limpias = tmp_path / "salida" / "ventas_limpias.csv"
    errores = tmp_path / "salida" / "ventas_errores.csv"
    calidad = tmp_path / "salida" / "calidad_datos.json"

    codigo = main(["--input", str(csv_mini), "--output", str(limpias),
                   "--errores", str(errores), "--json", str(calidad)])

    assert codigo == 0
    assert len(pd.read_csv(limpias)) == 2
    assert len(pd.read_csv(errores)) == 2
    assert json.loads(calidad.read_text(encoding="utf-8"))["filas_validas"] == 2


def test_main_fichero_inexistente(tmp_path, capsys):
    codigo = main(["--input", str(tmp_path / "no_existe.csv")])
    assert codigo == 1
    assert "No existe" in capsys.readouterr().err


def test_main_estricto_con_errores_devuelve_1(csv_mini, capsys):
    codigo = main(["--input", str(csv_mini), "--estricto"])
    assert codigo == 1
    assert "no cumplen" in capsys.readouterr().err


def test_ejecutar_con_repositorio_falso(ventas_mini, capsys):
    """DIP: el orquestador funciona con cualquier SalesRepository, no solo con CSV."""
    codigo = ejecutar(FakeSalesRepository(ventas_mini), parse_args([]))
    assert codigo == 0
    assert "Filas totales: 4" in capsys.readouterr().out


def test_python_m_ventas_app(csv_mini, monkeypatch, capsys):
    """Smoke test de 'python -m ventas_app' (ejecuta __main__.py)."""
    monkeypatch.setattr(sys, "argv", ["ventas_app", "--input", str(csv_mini)])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("ventas_app", run_name="__main__")
    assert info.value.code == 0
    assert "Válidas: 2" in capsys.readouterr().out


@pytest.mark.integration
def test_main_csv_del_curso(data_file, capsys):
    codigo = main(["--input", str(data_file)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Válidas: 140 | Inválidas: 10" in salida
