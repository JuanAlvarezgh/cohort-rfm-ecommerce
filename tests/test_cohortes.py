"""Tests de la matriz de retención por cohorte mensual."""
from pathlib import Path

import pytest

from analisis.cohortes import matriz_retencion
from analisis.limpieza import cargar, limpiar

RUTA_MUESTRA = Path(__file__).parent.parent / "datos" / "muestra.csv"


@pytest.fixture(scope="module")
def df_limpio():
    return limpiar(cargar(RUTA_MUESTRA))


@pytest.fixture(scope="module")
def retencion(df_limpio):
    return matriz_retencion(df_limpio)


def test_col_cero_es_100_porciento(retencion):
    """Todos los clientes de una cohorte están activos en el mes 0 (su primera compra)."""
    assert (retencion[0] == 1.0).all()


def test_valores_entre_0_y_1(retencion):
    """Los valores de retención (ignorando NaN) deben estar en el rango [0, 1]."""
    valores = retencion.stack()
    assert (valores >= 0).all() and (valores <= 1).all()


def test_indice_columnas_empieza_en_cero(retencion):
    """El primer índice de columna debe ser 0."""
    assert retencion.columns[0] == 0
