"""Convierte el volcado SQL original (10000_users.sql) en data/users.csv.

Uso (desde la raíz del proyecto):
    python scripts/sql_a_csv.py ruta/a/10000_users.sql data/users.csv

Qué hace:
    - Lee las sentencias INSERT INTO `users` del volcado de phpMyAdmin (MySQL).
    - Interpreta los escapes de MySQL (\\n, \\", \\', \\\\).
    - Elimina la columna "password" (no se usa y no debe subirse al repositorio).
    - Junta en una sola línea las direcciones que venían en dos ("calle\\nciudad"
      pasa a "calle, ciudad").

No forma parte de users_app: solo se usó una vez para preparar los datos.
"""

import csv
import re
import sys

ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "\\": "\\", "'": "'", '"': '"'}


def leer_filas(texto):
    """Devuelve (columnas, filas) a partir del texto del volcado SQL."""
    cabecera = re.search(r"INSERT INTO `users` \((.*?)\) VALUES", texto)
    columnas = re.findall(r"`(\w+)`", cabecera.group(1))
    filas = []
    for m in re.finditer(r"INSERT INTO `users` \(.*?\) VALUES\s*", texto):
        i = m.end()
        while texto[i] != ";":
            if texto[i] != "(":
                i += 1
                continue
            i += 1
            fila, valor = [], ""
            while True:
                c = texto[i]
                if c == "'":                       # valor entre comillas
                    i += 1
                    partes = []
                    while texto[i] != "'":
                        if texto[i] == "\\":
                            partes.append(ESCAPES.get(texto[i + 1], texto[i + 1]))
                            i += 2
                        else:
                            partes.append(texto[i])
                            i += 1
                    i += 1
                    valor = "".join(partes)
                elif c in ",)":                    # fin de un valor
                    valor = valor.strip()
                    fila.append("" if valor == "NULL" else valor)
                    valor = ""
                    i += 1
                    if c == ")":
                        filas.append(fila)
                        break
                else:                              # número o NULL sin comillas
                    valor += c
                    i += 1
    return columnas, filas


def main(origen, destino):
    with open(origen, encoding="utf-8") as f:
        columnas, filas = leer_filas(f.read())

    quitar = columnas.index("password")
    pos_direccion = columnas.index("address")
    columnas_salida = [c for c in columnas if c != "password"]

    with open(destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(columnas_salida)
        for fila in filas:
            fila[pos_direccion] = fila[pos_direccion].replace("\n", ", ")
            escritor.writerow([v for j, v in enumerate(fila) if j != quitar])

    print(f"{len(filas)} usuarios escritos en {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: python scripts/sql_a_csv.py ORIGEN.sql DESTINO.csv")
    main(sys.argv[1], sys.argv[2])
