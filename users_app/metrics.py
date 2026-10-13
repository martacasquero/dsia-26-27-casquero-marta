"""Métricas sobre el dataset de usuarios (se calculan sobre usuarios ya validados)."""

from dataclasses import dataclass

import pandas as pd

# Tramos de edad: [18, 25), [25, 35), [35, 45), [45, 55), [55, 66)
LIMITES_TRAMOS = [18, 25, 35, 45, 55, 66]
ETIQUETAS_TRAMOS = ["18-24", "25-34", "35-44", "45-54", "55-65"]


def extraer_estado(df):
    """Devuelve una serie con el estado (2 letras) sacado de la dirección.

    Ejemplo: "62083 Kris Cove, North Mitchel, WA 55100-3047" -> "WA"
    """
    return df["address"].str.extract(r"([A-Z]{2}) \d{5}", expand=False)


def usuarios_por_estado(df, top=None):
    """Número de usuarios por estado, de mayor a menor.

    Args:
        df: DataFrame de usuarios.
        top: si se indica, devuelve solo los `top` primeros estados.
    """
    conteo = extraer_estado(df).value_counts()
    return conteo.head(top) if top else conteo


def usuarios_por_genero(df):
    """Número de usuarios por género."""
    return df["gender"].value_counts()


def edad_media_por_genero(df):
    """Edad media por género, redondeada a 1 decimal."""
    return df.groupby("gender")["age"].mean().round(1)


def usuarios_por_tramo_edad(df):
    """Número de usuarios en cada tramo de edad (ETIQUETAS_TRAMOS), en orden."""
    tramos = pd.cut(df["age"], bins=LIMITES_TRAMOS, labels=ETIQUETAS_TRAMOS, right=False)
    return tramos.value_counts().reindex(ETIQUETAS_TRAMOS, fill_value=0)


def top_dominios_email(df, n=5):
    """Los `n` dominios de email más frecuentes (lo que va detrás de la @)."""
    dominios = df["email"].str.split("@").str[1]
    return dominios.value_counts().head(n)


@dataclass
class InformeUsuarios:
    """Resumen de métricas de un conjunto de usuarios."""

    total: int
    edad_media: float
    por_genero: dict
    edad_media_por_genero: dict
    por_tramo_edad: dict
    top_estados: dict
    top_dominios: dict

    @classmethod
    def desde_dataframe(cls, df, top=5):
        """Calcula todas las métricas a partir de un DataFrame de usuarios."""
        return cls(
            total=len(df),
            edad_media=round(float(df["age"].mean()), 1),
            por_genero=usuarios_por_genero(df).to_dict(),
            edad_media_por_genero=edad_media_por_genero(df).to_dict(),
            por_tramo_edad=usuarios_por_tramo_edad(df).to_dict(),
            top_estados=usuarios_por_estado(df, top=top).to_dict(),
            top_dominios=top_dominios_email(df, n=top).to_dict(),
        )

    def como_texto(self):
        """Devuelve el informe en texto, listo para imprimir por pantalla."""
        lineas = [
            f"Usuarios analizados: {self.total}",
            f"Edad media: {self.edad_media}",
            "",
            "Usuarios por género:",
            *[f"  {g}: {n}" for g, n in self.por_genero.items()],
            "",
            "Edad media por género:",
            *[f"  {g}: {e}" for g, e in self.edad_media_por_genero.items()],
            "",
            "Usuarios por tramo de edad:",
            *[f"  {t}: {n}" for t, n in self.por_tramo_edad.items()],
            "",
            f"Top {len(self.top_estados)} estados:",
            *[f"  {s}: {n}" for s, n in self.top_estados.items()],
            "",
            f"Top {len(self.top_dominios)} dominios de email:",
            *[f"  {d}: {n}" for d, n in self.top_dominios.items()],
        ]
        return "\n".join(lineas)
