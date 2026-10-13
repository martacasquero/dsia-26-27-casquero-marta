"""Interfaz de línea de comandos del pipeline de usuarios.

Uso:
    python -m users_app
    python -m users_app --archivo data/users.csv --top 10
    python -m users_app --guardar-invalidos invalidos.csv
"""

import argparse
import sys
from pathlib import Path

from users_app.exceptions import UsersError
from users_app.loader import load_users
from users_app.metrics import InformeUsuarios
from users_app.validator import separar_validos

ARCHIVO_POR_DEFECTO = "data/users.csv"


def parse_args(argv=None):
    """Lee los argumentos de la terminal.

    Args:
        argv: lista de argumentos (None = los de la terminal). Útil en los tests.
    """
    parser = argparse.ArgumentParser(
        prog="python -m users_app",
        description="Carga, valida y calcula métricas del dataset de usuarios.",
    )
    parser.add_argument(
        "--archivo", default=ARCHIVO_POR_DEFECTO,
        help=f"ruta al CSV de usuarios (por defecto: {ARCHIVO_POR_DEFECTO})",
    )
    parser.add_argument(
        "--top", type=int, default=5,
        help="cuántos estados y dominios de email mostrar (por defecto: 5)",
    )
    parser.add_argument(
        "--guardar-invalidos", metavar="RUTA",
        help="guarda las filas inválidas (con su motivo) en este CSV",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Ejecuta el pipeline completo: cargar -> validar -> métricas -> informe.

    Returns:
        0 si todo ha ido bien, 1 si ha habido un error del proyecto.
    """
    args = parse_args(argv)
    try:
        df = load_users(args.archivo)
    except UsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    validos, invalidos = separar_validos(df)
    print(f"Filas leídas: {len(df)}")
    print(f"Válidas: {len(validos)}")
    print(f"Inválidas: {len(invalidos)}")

    if args.guardar_invalidos:
        ruta = Path(args.guardar_invalidos)
        ruta.parent.mkdir(parents=True, exist_ok=True)  # crea la carpeta si no existe
        invalidos.to_csv(ruta, index=False)
        print(f"Filas inválidas guardadas en: {args.guardar_invalidos}")

    if validos.empty:
        print("No hay usuarios válidos sobre los que calcular métricas.")
        return 0

    print()
    print(InformeUsuarios.desde_dataframe(validos, top=args.top).como_texto())
    return 0
