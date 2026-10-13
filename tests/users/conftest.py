"""Fixtures compartidas por todos los tests de users_app.

pytest carga este archivo automáticamente: cualquier test de esta carpeta
puede usar estas fixtures solo con ponerlas como parámetro.
"""

from pathlib import Path

import pandas as pd
import pytest

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "users.csv"


@pytest.fixture
def df_valido():
    """Tres usuarios en memoria que cumplen todas las reglas."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Ana Ruiz", "Luis Gil", "Eva Sanz"],
        "age": [30, 18, 65],
        "gender": ["Female", "Man", "Female"],
        "email": ["ana@mail.com", "luis@gmail.com", "eva@gmail.com"],
        "phone": ["600111222", None, "600333444"],
        "address": [
            "1 Main St, Springfield, WA 12345",
            "2 Oak Ave, Dover, DE 19901-1234",
            "3 Pine Rd, Seattle, WA 98101",
        ],
        "profile_picture": ["http://img/1", "http://img/2", "http://img/3"],
        "created_at": ["2024-04-22 15:38:34"] * 3,
        "updated_at": ["2024-04-22 15:38:34"] * 3,
    })


@pytest.fixture
def csv_valido(tmp_path, df_valido):
    """Escribe df_valido en un CSV temporal y devuelve su ruta."""
    ruta = tmp_path / "users.csv"
    df_valido.to_csv(ruta, index=False)
    return ruta


@pytest.fixture
def data_file():
    """Ruta al CSV real del proyecto (para los tests de integración)."""
    return DATA_FILE
