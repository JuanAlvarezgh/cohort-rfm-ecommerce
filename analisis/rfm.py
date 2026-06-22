import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def tabla_rfm(df: pd.DataFrame, fecha_referencia=None) -> pd.DataFrame:
    """Calcula Recencia, Frecuencia y Monetario por cliente."""
    if fecha_referencia is None:
        fecha_referencia = df["fecha"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("id_cliente").agg(
        recencia=("fecha", lambda x: (fecha_referencia - x.max()).days),
        frecuencia=("factura", "nunique"),
        monetario=("monto", "sum"),
    ).reset_index()
    return rfm


_KS_PREDETERMINADO = range(2, 9)


def metodo_codo(rfm: pd.DataFrame, ks=_KS_PREDETERMINADO, semilla=42) -> dict:
    """Inercia de KMeans por cada k (para elegir el numero de segmentos)."""
    X = _escalar(rfm)
    return {k: KMeans(n_clusters=k, random_state=semilla, n_init=10).fit(X).inertia_ for k in ks}


def _escalar(rfm: pd.DataFrame):
    base = rfm[["recencia", "frecuencia", "monetario"]].copy()
    # log1p para reducir asimetria (frecuencia y monetario son muy sesgados)
    base["frecuencia"] = np.log1p(base["frecuencia"])
    base["monetario"] = np.log1p(base["monetario"])
    return StandardScaler().fit_transform(base)


def segmentar(rfm: pd.DataFrame, k=4, semilla=42) -> pd.DataFrame:
    """Asigna cada cliente a un segmento con KMeans y le pone una etiqueta legible."""
    rfm = rfm.copy()
    X = _escalar(rfm)
    rfm["segmento"] = KMeans(n_clusters=k, random_state=semilla, n_init=10).fit_predict(X)
    # Etiqueta por ranking del perfil del cluster: mejor recencia (baja), mayor f y monetario
    perfil = rfm.groupby("segmento").agg(
        recencia=("recencia", "mean"),
        frecuencia=("frecuencia", "mean"),
        monetario=("monetario", "mean"),
    )
    # puntaje: menor recencia es mejor -> usar -recencia; sumar rangos normalizados
    puntaje = (
        (-perfil["recencia"]).rank() + perfil["frecuencia"].rank() + perfil["monetario"].rank()
    ).sort_values(ascending=False)
    etiquetas_ordenadas = ["Campeones", "Leales", "En riesgo", "Perdidos"]
    mapa = {seg: etiquetas_ordenadas[i] if i < len(etiquetas_ordenadas) else f"Segmento {i}"
            for i, seg in enumerate(puntaje.index)}
    rfm["etiqueta"] = rfm["segmento"].map(mapa)
    return rfm
