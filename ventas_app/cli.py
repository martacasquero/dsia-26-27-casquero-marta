"""Interfaz de línea de comandos del pipeline de ventas (Facade).

Uso:
    python -m ventas_app
    python -m ventas_app --input data/ventas.csv --output salida/ventas_limpias.csv
    python -m ventas_app --errores salida/ventas_errores.csv --json salida/calidad_datos.json
    python -m ventas_app --estricto
"""

import argparse
import json
import sys
from pathlib import Path

from ventas_app.exceptions import VentasError
from ventas_app.loader import CsvSalesRepository, SalesRepository
from ventas_app.metrics import (
    clientes_recurrentes,
    importe_por_region,
    resumen_calidad,
    top_productos,
)
from ventas_app.validator import validar_ventas

ENTRADA_POR_DEFECTO = "data/ventas.csv"


def parse_args(argv=None):
    """Lee los argumentos de la terminal (argv=None usa los reales; útil en tests)."""
    parser = argparse.ArgumentParser(
        prog="python -m ventas_app",
        description="Carga, valida y resume el CSV de ventas.",
    )
    parser.add_argument("--input", default=ENTRADA_POR_DEFECTO,
                        help=f"CSV de ventas (por defecto: {ENTRADA_POR_DEFECTO})")
    parser.add_argument("--output", help="guarda aquí las ventas válidas (CSV)")
    parser.add_argument("--errores", help="guarda aquí las ventas inválidas con su motivo (CSV)")
    parser.add_argument("--json", help="guarda aquí el resumen de calidad (JSON)")
    parser.add_argument("--top", type=int, default=3, help="número de productos en el top (por defecto: 3)")
    parser.add_argument("--estricto", action="store_true",
                        help="termina con error si hay alguna fila inválida")
    return parser.parse_args(argv)


def informe(validos, errores, resumen, top):
    """Construye el texto del informe que se imprime por pantalla."""
    lineas = [
        f"Filas totales: {resumen['filas_totales']}",
        f"Válidas: {resumen['filas_validas']} | Inválidas: {resumen['filas_invalidas']}",
        f"Importe total: {resumen['importe_total']:.2f}",
        "",
        "Importe por región:",
        *[f"  {region}: {importe:.2f}" for region, importe in importe_por_region(validos).items()],
        "",
        f"Top {top} productos por importe:",
        *[f"  {producto}: {importe:.2f}" for producto, importe in top_productos(validos, top).items()],
        "",
        f"Clientes recurrentes (más de una compra): {len(clientes_recurrentes(validos))}",
    ]
    if not errores.empty:
        lineas += ["", "Filas inválidas:"]
        lineas += [
            f"  {fila.fecha} {fila.region} {fila.producto} ({fila.cliente_id}): {fila.motivo}"
            for fila in errores.itertuples()
        ]
    return "\n".join(lineas)


def _guardar(path, escribir):
    """Crea la carpeta de destino si no existe y escribe el archivo."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    escribir(path)
    print(f"Escrito: {path}")


def ejecutar(repo: SalesRepository, args) -> int:
    """Orquesta el pipeline a partir de cualquier SalesRepository (DIP)."""
    frame = repo.load()
    validos, errores = validar_ventas(frame, estricto=args.estricto)
    resumen = resumen_calidad(frame, validos, errores)

    print(informe(validos, errores, resumen, args.top))

    if args.output:
        _guardar(args.output, lambda p: validos.to_csv(p, index=False))
    if args.errores:
        _guardar(args.errores, lambda p: errores.to_csv(p, index=False))
    if args.json:
        _guardar(args.json, lambda p: p.write_text(
            json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"))
    return 0


def main(argv=None) -> int:
    """Punto de entrada. Devuelve 0 si va bien y 1 si hay un error de dominio."""
    args = parse_args(argv)
    try:
        return ejecutar(CsvSalesRepository(args.input), args)
    except VentasError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # permite también: python -m ventas_app.cli
    raise SystemExit(main())
