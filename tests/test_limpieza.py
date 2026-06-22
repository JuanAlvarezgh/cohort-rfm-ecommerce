"""Tests de la capa de limpieza sobre la muestra versionada."""
from pathlib import Path

import pandas as pd
import pytest

from analisis.limpieza import cargar, limpiar

RUTA_MUESTRA = Path(__file__).parent.parent / "datos" / "muestra.csv"


@pytest.fixture(scope="module")
def df_crudo():
    return cargar(RUTA_MUESTRA)


@pytest.fixture(scope="module")
def df_limpio(df_crudo):
    return limpiar(df_crudo)


# --- columnas en español ---

COLUMNAS_ESPERADAS = {
    "factura", "codigo_producto", "descripcion", "cantidad",
    "fecha", "precio_unitario", "id_cliente", "pais",
}


def test_columnas_en_espanol(df_crudo):
    assert COLUMNAS_ESPERADAS.issubset(set(df_crudo.columns))


# --- sin id_cliente nulos tras limpiar ---

def test_sin_nulos_id_cliente(df_limpio):
    assert df_limpio["id_cliente"].isna().sum() == 0


# --- sin cancelaciones (facturas que empiezan por 'C') ---

def test_sin_cancelaciones(df_limpio):
    tiene_cancelacion = df_limpio["factura"].astype(str).str.startswith("C")
    assert tiene_cancelacion.sum() == 0


# --- cantidad siempre positiva ---

def test_cantidad_positiva(df_limpio):
    assert (df_limpio["cantidad"] > 0).all()


# --- precio_unitario siempre positivo ---

def test_precio_unitario_positivo(df_limpio):
    assert (df_limpio["precio_unitario"] > 0).all()


# --- columna monto existe y es correcta ---

def test_monto_existe(df_limpio):
    assert "monto" in df_limpio.columns


def test_monto_es_cantidad_por_precio(df_limpio):
    esperado = df_limpio["cantidad"] * df_limpio["precio_unitario"]
    pd.testing.assert_series_equal(df_limpio["monto"], esperado, check_names=False)


# --- la limpieza realmente elimina filas (muestra tiene nulos y cancelaciones) ---

def test_limpieza_reduce_filas(df_crudo, df_limpio):
    assert len(df_limpio) < len(df_crudo)


# --- fecha convertida a datetime ---

def test_fecha_es_datetime(df_limpio):
    assert pd.api.types.is_datetime64_any_dtype(df_limpio["fecha"])


# --- id_cliente es entero tras limpiar ---

def test_id_cliente_es_entero(df_limpio):
    assert pd.api.types.is_integer_dtype(df_limpio["id_cliente"])
