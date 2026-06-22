"""Tests de la capa RFM: tabla, método del codo y segmentación k-means."""
from pathlib import Path

import pytest

from analisis.limpieza import cargar, limpiar
from analisis.rfm import metodo_codo, segmentar, tabla_rfm

RUTA_MUESTRA = Path(__file__).parent.parent / "datos" / "muestra.csv"


@pytest.fixture(scope="module")
def df_limpio():
    return limpiar(cargar(RUTA_MUESTRA))


@pytest.fixture(scope="module")
def rfm(df_limpio):
    return tabla_rfm(df_limpio)


@pytest.fixture(scope="module")
def segmentado(rfm):
    return segmentar(rfm, k=4, semilla=42)


# --- tabla_rfm ---


def test_rfm_cliente_conocido_frecuencia(rfm):
    """El cliente 17850 tiene exactamente 10 facturas únicas en la muestra."""
    fila = rfm[rfm["id_cliente"] == 17850].iloc[0]
    assert fila["frecuencia"] == 10


def test_rfm_cliente_conocido_monetario(rfm):
    """El cliente 17850 tiene monto total de 1499.34."""
    fila = rfm[rfm["id_cliente"] == 17850].iloc[0]
    assert abs(fila["monetario"] - 1499.34) < 0.01


def test_rfm_recencia_no_negativa(rfm):
    """La recencia de todos los clientes debe ser >= 0."""
    assert (rfm["recencia"] >= 0).all()


# --- metodo_codo ---


def test_codo_devuelve_inercia_por_k(rfm):
    """metodo_codo devuelve un dict con una inercia por cada k del rango."""
    ks = range(2, 6)
    resultado = metodo_codo(rfm, ks=ks)
    assert set(resultado.keys()) == set(ks)
    assert all(isinstance(v, float) for v in resultado.values())


def test_codo_inercia_decrece_con_k(rfm):
    """La inercia de KMeans debe disminuir al aumentar k."""
    resultado = metodo_codo(rfm, ks=range(2, 7))
    valores = [resultado[k] for k in sorted(resultado)]
    assert all(valores[i] > valores[i + 1] for i in range(len(valores) - 1))


# --- segmentar ---


def test_segmentar_cuatro_etiquetas_distintas(segmentado):
    """Con k=4 deben aparecer exactamente 4 etiquetas distintas."""
    assert segmentado["etiqueta"].nunique() == 4


def test_segmentar_campeones_mayor_frecuencia_y_monetario(segmentado):
    """El segmento Campeones debe tener la mayor frecuencia y monetario medios."""
    perfil = segmentado.groupby("etiqueta").agg(
        frecuencia=("frecuencia", "mean"),
        monetario=("monetario", "mean"),
    )
    assert perfil.loc["Campeones", "frecuencia"] == perfil["frecuencia"].max()
    assert perfil.loc["Campeones", "monetario"] == perfil["monetario"].max()
