# dsia-26-27-casquero-marta — Proyecto I

![CI](https://github.com/martacasquero/dsia-26-27-casquero-marta/actions/workflows/ci.yml/badge.svg)

Dos pipelines de calidad de datos con la misma forma:

```
CSV → loader → validator → metrics → cli (informe y ficheros de salida)
```

| Parte | Paquete | Datos |
| --- | --- | --- |
| A — Ventas (dataset del curso) | `ventas_app/` | `data/ventas.csv` (150 filas) |
| B — Usuarios (dataset externo) | `users_app/` | `data/users.csv` (10.000 filas) |

## Estructura

```text
dsia-26-27-casquero-marta/
├── ventas_app/              # Parte A
│   ├── __main__.py          # python -m ventas_app
│   ├── exceptions.py        # VentasError, DataLoadError, ValidationError
│   ├── loader.py            # SalesRepository (Protocol) + CsvSalesRepository
│   ├── validator.py         # validar_ventas → (validos, errores)
│   ├── metrics.py           # importes por región/producto, clientes recurrentes…
│   └── cli.py               # argparse + orquestación
├── users_app/               # Parte B (misma estructura)
│   ├── __main__.py
│   ├── exceptions.py
│   ├── loader.py
│   ├── validator.py
│   ├── metrics.py
│   └── cli.py
├── tests/
│   ├── ventas/              # conftest.py + test_loader / test_validator / test_metrics / test_cli
│   └── users/               # conftest.py + test_loader / test_validator / test_metrics / test_cli
├── data/
│   ├── ventas.csv
│   └── users.csv
├── scripts/
│   └── sql_a_csv.py         # preparación de users.csv a partir del volcado SQL
├── .github/workflows/ci.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Instalación

Con **pip** (Python 3.12):

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Con **uv**:

```bash
uv sync
```

Con uv, antepón `uv run` a los comandos de abajo (por ejemplo, `uv run pytest -q`).

---

## Parte A — Pipeline de ventas (`ventas_app`)

### Uso

```bash
python -m ventas_app                                        # usa data/ventas.csv
python -m ventas_app --input data/ventas.csv --output salida/ventas_limpias.csv
python -m ventas_app --errores salida/ventas_errores.csv --json salida/calidad_datos.json
python -m ventas_app --top 5                                # top 5 productos
python -m ventas_app --estricto                             # sale con código 1 si hay filas inválidas
python -m ventas_app.cli --help                             # también funciona así
```

La carpeta `salida/` se crea sola y está en `.gitignore`, porque los ficheros se pueden regenerar.

### Contrato de datos

**Entrada:** `fecha`, `region`, `producto`, `unidades`, `precio_unitario`, `cliente_id`.

**Fila válida:**
- `unidades` es numérica y mayor que 0;
- `precio_unitario` es numérico y mayor que 0.

A las filas válidas se les añade `importe = unidades * precio_unitario`. Las inválidas no se borran: se separan con una columna `motivo`.

**Checkpoint:** con `data/ventas.csv` salen **140 válidas y 10 inválidas**. Lo comprueba el test de integración `test_checkpoint_csv_del_curso`.

### Métricas

1. Importe total.
2. Importe por región, de mayor a menor.
3. Importe por producto y top N productos.
4. Clientes recurrentes (más de una compra válida).
5. Resumen de calidad (`calidad_datos.json`): filas totales, válidas, inválidas e importe total.

### Diseño (SOLID)

- **SRP** — `validator.py` solo decide qué filas son válidas: no lee ni escribe ficheros. El I/O está en `loader.py` (lectura) y `cli.py` (escritura).
- **DIP** — `cli.ejecutar()` recibe cualquier objeto que cumpla el `Protocol` `SalesRepository`, no un CSV concreto. Así se prueba en `test_ejecutar_con_repositorio_falso` con un `FakeSalesRepository` en memoria.
- **OCP** — Las métricas son funciones independientes en `metrics.py`. Para añadir una nueva (por ejemplo, ticket medio) no hay que tocar el loader ni el validator.

---

## Parte B — Pipeline de usuarios (`users_app`)

### Dataset

| Campo | Valor |
| --- | --- |
| Origen (URL) | _(completar)_ |
| Licencia / condiciones de uso | _(completar)_ |
| Fecha de descarga | _(completar)_ |
| Formato original | Volcado SQL de phpMyAdmin (MySQL 5.7), tabla `users` |
| Filas | 10.000 |

**Preparación.** El volcado se convirtió a `data/users.csv` con:

```bash
python scripts/sql_a_csv.py ruta/a/10000_users.sql data/users.csv
```

Durante la conversión:
- se eliminó la columna `password`, que no se usa en el análisis y no debe subirse al repositorio;
- las direcciones que venían en dos líneas se unieron en una (`calle, ciudad, ESTADO CP`).

**Columnas:** `id`, `name`, `age`, `gender`, `email`, `phone`, `address`, `profile_picture`, `created_at`, `updated_at`.

### Uso

```bash
python -m users_app                                   # usa data/users.csv
python -m users_app --archivo otra_ruta.csv
python -m users_app --top 10
python -m users_app --guardar-invalidos salida/users_invalidos.csv
```

### Reglas de validación

| Regla | Justificación |
| --- | --- |
| Sin valores vacíos, salvo en `phone` | En la tabla SQL original todas las columnas eran `NOT NULL` excepto `phone` |
| `id` único | Era la clave primaria de la tabla |
| `email` con formato válido y sin repetir | Tenía una clave `UNIQUE` en la tabla |
| `age` entre 18 y 65 | Rango de edades del dataset |
| `gender` ∈ {`Man`, `Female`} | Únicos valores presentes en el dataset |
| `address` contiene estado + código postal (p. ej. `WA 55100`) | Formato de todas las direcciones del dataset |

Hay dos modos de validar:
- `validate_users(df)`: **estricto**. Lanza la excepción de la primera regla que falle (`EdadInvalidaError`, `EmailInvalidoError`…; todas heredan de `ValidacionError`).
- `separar_validos(df)`: **fila a fila**. Devuelve `(validos, invalidos)` con una columna `motivo`. Es el modo que usa la CLI.

Con `data/users.csv`: 10.000 válidas y 0 inválidas.

### Métricas

1. Usuarios por estado (extraído de la dirección).
2. Usuarios por género.
3. Edad media por género.
4. Usuarios por tramo de edad (18-24, 25-34, 35-44, 45-54, 55-65).
5. Dominios de email más frecuentes.

---

## Tests

```bash
pytest -q                                   # todos
pytest -q -m "not integration"              # solo unitarios
pytest -q -m integration                    # solo integración (CSV reales)
pytest --cov=ventas_app --cov=users_app --cov-report=term-missing --cov-fail-under=60
```

Resumen: **102 tests**, de los cuales 6 son de integración. La cobertura es del **99 %**.

| Módulo | Parte A (`tests/ventas/`) | Parte B (`tests/users/`) |
| --- | --- | --- |
| loader | Carga correcta; fichero inexistente, vacío, solo cabecera y columnas que faltan → `DataLoadError` | Igual, con `NoHayArchivoError`, `ArchivoVacioError` y `FaltanColumnasError` |
| validator | Válidas vs inválidas; bordes con `parametrize` (0, -1, nulos, `"na"`); importe; modo estricto | Válidas vs inválidas; bordes de edad (0, -1, 17, 18, 65, 66, nulos); emails; cada excepción |
| metrics | Cada agregación con resultado conocido sobre la fixture `ventas_mini` | Cada agregación con resultado conocido sobre la fixture `df_valido` |
| cli | `parse_args`, `main` con CSV en `tmp_path`, ficheros de salida, error de carga, modo estricto, repositorio falso y `python -m` | `parse_args`, `main` con CSV en `tmp_path`, error de carga, exportación de inválidos y `python -m` |

Conceptos de pytest usados:
- **AAA + assert**: `test_load_csv_ok` (ventas) y `test_carga_un_csv_pequeno` (users), con Arrange / Act / Assert comentados.
- **`pytest.raises`**: errores del loader y del validator en las dos partes.
- **`parametrize`**: unidades y precios no válidos, bordes de edad, emails, tramos de edad.
- **`fixture`**: `ventas_mini`, `csv_mini`, `df_valido`, `csv_valido` y `data_file` en los `conftest.py`; además de `tmp_path`, `capsys` y `monkeypatch`.
- **`@pytest.mark.integration`**: 6 tests (3 por parte) con los CSV reales, incluido el checkpoint 140/10.

## Integración continua

`.github/workflows/ci.yml` es un único workflow para las dos partes. Se ejecuta en cada `push` a `main` y en cada `pull_request`:

1. checkout del código;
2. Python 3.12;
3. `pip install -r requirements.txt`;
4. `pytest --cov=ventas_app --cov=users_app --cov-report=term-missing --cov-fail-under=60`.

El estado del último run aparece en el badge del principio y en la pestaña **Actions** del repositorio.
