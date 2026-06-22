"""Tests de la capa de gráficos: verifican que se genera el PNG esperado."""

import pandas as pd
import pytest

from analisis.graficos import (
    dispersion_segmentos,
    grafico_codo,
    heatmap_cohortes,
    perfil_segmentos,
)


@pytest.fixture()
def matriz_minima():
    """Matriz de retención 3x3 con datos sintéticos."""
    return pd.DataFrame(
        {0: [1.0, 1.0, 1.0], 1: [0.5, 0.4, 0.6], 2: [0.3, float("nan"), 0.25]},
        index=pd.PeriodIndex(["2023-01", "2023-02", "2023-03"], freq="M"),
    )


@pytest.fixture()
def rfm_minimo():
    """DataFrame RFM segmentado con 12 clientes, 3 por etiqueta."""
    return pd.DataFrame(
        {
            "id_cliente": range(1, 13),
            "recencia": [10, 12, 8, 9, 60, 55, 70, 65, 200, 190, 210, 220],
            "frecuencia": [20, 18, 22, 19, 8, 7, 9, 8, 2, 1, 2, 1],
            "monetario": [5000, 4800, 5200, 4900, 1500, 1200, 1700, 1100,
                          300, 250, 280, 200],
            "segmento": [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2],
            "etiqueta": (
                ["Campeones"] * 4 + ["Leales"] * 4 + ["En riesgo"] * 4
            ),
        }
    )


def test_heatmap_cohortes_crea_png(matriz_minima, tmp_path):
    ruta = tmp_path / "heatmap.png"
    heatmap_cohortes(matriz_minima, ruta)
    assert ruta.exists()
    assert ruta.stat().st_size > 1000


def test_grafico_codo_crea_png(tmp_path):
    inercias = {2: 1500.0, 3: 900.0, 4: 600.0, 5: 450.0}
    ruta = tmp_path / "codo.png"
    grafico_codo(inercias, ruta)
    assert ruta.exists()
    assert ruta.stat().st_size > 500


def test_dispersion_segmentos_crea_png(rfm_minimo, tmp_path):
    ruta = tmp_path / "dispersion.png"
    dispersion_segmentos(rfm_minimo, ruta)
    assert ruta.exists()
    assert ruta.stat().st_size > 1000


def test_perfil_segmentos_crea_png(rfm_minimo, tmp_path):
    # El fixture solo tiene 3 etiquetas; la función reindexará y habrá NaN
    # para "Perdidos", lo cual es aceptable para verificar que se genera el PNG.
    ruta = tmp_path / "perfil.png"
    perfil_segmentos(rfm_minimo, ruta)
    assert ruta.exists()
    assert ruta.stat().st_size > 1000
