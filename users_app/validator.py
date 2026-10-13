"""Validación de las reglas de negocio del dataset de usuarios.

Ofrece dos formas de validar:
    - validate_users(df): modo estricto. Lanza una excepción en cuanto
      una regla no se cumple.
    - separar_validos(df): modo fila a fila. Devuelve las filas válidas
      y las inválidas (con el motivo), sin lanzar excepciones.

Las dos usan las mismas funciones "mascara_*", que devuelven una serie de
True/False marcando con True las filas que INCUMPLEN cada regla.
"""

import pandas as pd

from users_app.exceptions import (
    DireccionInvalidaError,
    EdadInvalidaError,
    EmailInvalidoError,
    GeneroInvalidoError,
    IdDuplicadoError,
    ValoresNulosError,
)

EDAD_MIN = 18
EDAD_MAX = 65
GENEROS_VALIDOS = {"Man", "Female"}
# Columnas que no pueden estar vacías (en la tabla SQL original solo phone admite NULL)
COLUMNAS_OBLIGATORIAS = [
    "id", "name", "age", "gender", "email",
    "address", "profile_picture", "created_at", "updated_at",
]
PATRON_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
# Estado (2 mayúsculas) + espacio + código postal (5 dígitos), p. ej. "WA 55100"
PATRON_DIRECCION = r"[A-Z]{2} \d{5}"


# --- Máscaras: True = la fila incumple la regla ---

def mascara_nulos(df):
    """Filas con algún valor vacío en COLUMNAS_OBLIGATORIAS."""
    return df[COLUMNAS_OBLIGATORIAS].isna().any(axis=1)


def mascara_ids_duplicados(df):
    """Filas cuyo id aparece más de una vez."""
    return df["id"].duplicated(keep=False)


def mascara_emails_mal_formados(df):
    """Filas cuyo email no tiene formato válido."""
    return ~df["email"].astype(str).str.match(PATRON_EMAIL)


def mascara_emails_repetidos(df):
    """Filas cuyo email aparece más de una vez."""
    return df["email"].duplicated(keep=False)


def mascara_edades(df):
    """Filas con edad no numérica o fuera de [EDAD_MIN, EDAD_MAX]."""
    edades = pd.to_numeric(df["age"], errors="coerce")  # lo que no sea número pasa a NaN
    return edades.isna() | (edades < EDAD_MIN) | (edades > EDAD_MAX)


def mascara_generos(df):
    """Filas con un género fuera de GENEROS_VALIDOS."""
    return ~df["gender"].isin(GENEROS_VALIDOS)


def mascara_direcciones(df):
    """Filas cuya dirección no contiene estado + código postal."""
    return ~df["address"].astype(str).str.contains(PATRON_DIRECCION)


# Cada regla: (máscara, excepción del modo estricto, motivo para el modo fila a fila)
REGLAS = [
    (mascara_nulos, ValoresNulosError, "valores vacíos"),
    (mascara_ids_duplicados, IdDuplicadoError, "id repetido"),
    (mascara_emails_mal_formados, EmailInvalidoError, "email con formato incorrecto"),
    (mascara_emails_repetidos, EmailInvalidoError, "email repetido"),
    (mascara_edades, EdadInvalidaError, f"edad fuera de {EDAD_MIN}-{EDAD_MAX}"),
    (mascara_generos, GeneroInvalidoError, "género no permitido"),
    (mascara_direcciones, DireccionInvalidaError, "dirección sin estado y código postal"),
]


def _ids(df, mascara, max_ids=5):
    """Devuelve un texto con los primeros ids de las filas marcadas."""
    ids = df.loc[mascara, "id"].head(max_ids).tolist()
    return ", ".join(str(i) for i in ids)


def validate_users(df):
    """Comprueba todas las reglas y se detiene en la primera que falle.

    Args:
        df: DataFrame devuelto por load_users.

    Returns:
        El mismo DataFrame, si pasa todas las reglas.

    Raises:
        ValidacionError (o una de sus subclases) si alguna regla no se cumple.
    """
    for mascara_fn, excepcion, motivo in REGLAS:
        mascara = mascara_fn(df)
        if mascara.any():
            raise excepcion(f"{motivo.capitalize()} en {mascara.sum()} filas (ids: {_ids(df, mascara)})")
    return df


def separar_validos(df):
    """Separa los usuarios válidos de los inválidos, fila a fila.

    Args:
        df: DataFrame devuelto por load_users.

    Returns:
        Tupla (validos, invalidos):
            validos: DataFrame con las filas que cumplen todas las reglas.
            invalidos: DataFrame con las filas que incumplen alguna regla,
                con una columna extra "motivo" (varios motivos separados por "; ").
    """
    motivos = pd.Series("", index=df.index)
    for mascara_fn, _excepcion, motivo in REGLAS:
        mascara = mascara_fn(df)
        motivos[mascara] = motivos[mascara] + motivo + "; "

    es_invalida = motivos != ""
    validos = df[~es_invalida].copy()
    invalidos = df[es_invalida].copy()
    invalidos["motivo"] = motivos[es_invalida].str.rstrip("; ")
    return validos, invalidos
