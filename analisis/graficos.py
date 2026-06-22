"""Funciones para generar y guardar los gráficos del análisis de cohortes y RFM."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")


def heatmap_cohortes(matriz, ruta):
    """Heatmap de retención por cohorte mensual.

    Parámetros
    ----------
    matriz : DataFrame con filas=cohorte (periodo mensual), columnas=indice de mes,
             valores=proporcion 0-1.
    ruta   : ruta donde se guarda el PNG.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    datos = matriz.values
    im = ax.imshow(datos, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Proporción de clientes activos", fontsize=11)

    filas = [str(c) for c in matriz.index]
    columnas = [str(c) for c in matriz.columns]

    ax.set_xticks(range(len(columnas)))
    ax.set_xticklabels(columnas, fontsize=9)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels(filas, fontsize=9)

    for i in range(len(filas)):
        for j in range(len(columnas)):
            valor = datos[i, j]
            if not np.isnan(valor):
                texto = f"{valor:.0%}"
                color_texto = "white" if valor > 0.6 else "black"
                ax.text(j, i, texto, ha="center", va="center", fontsize=7,
                        color=color_texto)

    ax.set_title("Retención de clientes por cohorte mensual", fontsize=14, pad=14)
    ax.set_xlabel("Índice de mes desde primera compra", fontsize=11)
    ax.set_ylabel("Cohorte (mes de primera compra)", fontsize=11)

    fig.tight_layout()
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)


def grafico_codo(inercias, ruta):
    """Gráfico de línea: inercia vs k (método del codo).

    Parámetros
    ----------
    inercias : dict {k: inercia} generado por metodo_codo.
    ruta     : ruta donde se guarda el PNG.
    """
    ks = sorted(inercias.keys())
    valores = [inercias[k] for k in ks]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ks, valores, marker="o", linewidth=2, color="#2c7bb6")
    ax.set_xticks(ks)
    ax.set_title("Método del codo para elegir k", fontsize=13)
    ax.set_xlabel("Número de clústeres (k)", fontsize=11)
    ax.set_ylabel("Inercia (suma de distancias al cuadrado)", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)


def dispersion_segmentos(rfm_segmentado, ruta):
    """Dispersión frecuencia (log) vs monetario (log), coloreado por etiqueta.

    Parámetros
    ----------
    rfm_segmentado : DataFrame con columnas frecuencia, monetario, etiqueta.
    ruta           : ruta donde se guarda el PNG.
    """
    colores = {
        "Campeones": "#1a9641",
        "Leales": "#a6d96a",
        "En riesgo": "#fdae61",
        "Perdidos": "#d7191c",
    }

    fig, ax = plt.subplots(figsize=(9, 6))

    for etiqueta, grupo in rfm_segmentado.groupby("etiqueta"):
        color = colores.get(etiqueta, "#888888")
        ax.scatter(
            grupo["frecuencia"],
            grupo["monetario"],
            label=etiqueta,
            color=color,
            alpha=0.55,
            s=18,
            edgecolors="none",
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Segmentos de clientes (RFM + k-means)", fontsize=13)
    ax.set_xlabel("Frecuencia (nº de pedidos, escala log)", fontsize=11)
    ax.set_ylabel("Monetario (£, escala log)", fontsize=11)
    ax.legend(title="Segmento", fontsize=10, title_fontsize=10)
    ax.grid(linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)


def perfil_segmentos(rfm_segmentado, ruta):
    """Barras: número de clientes y monetario medio por segmento.

    Parámetros
    ----------
    rfm_segmentado : DataFrame con columnas etiqueta, monetario.
    ruta           : ruta donde se guarda el PNG.
    """
    orden = ["Campeones", "Leales", "En riesgo", "Perdidos"]
    colores = ["#1a9641", "#a6d96a", "#fdae61", "#d7191c"]

    perfil = rfm_segmentado.groupby("etiqueta").agg(
        num_clientes=("id_cliente", "count"),
        monetario_medio=("monetario", "mean"),
    ).reindex(orden)

    etiquetas = perfil.index.tolist()
    x = np.arange(len(etiquetas))
    ancho = 0.45

    fig, ax1 = plt.subplots(figsize=(9, 6))
    ax2 = ax1.twinx()

    ax1.bar(x - ancho / 2, perfil["num_clientes"], ancho,
            color=colores, alpha=0.85, label="Nº de clientes")
    ax2.bar(x + ancho / 2, perfil["monetario_medio"], ancho,
            color=colores, alpha=0.45, edgecolor="black",
            linewidth=0.8, label="Monetario medio (£)")

    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, fontsize=11)
    ax1.set_ylabel("Número de clientes", fontsize=11)
    ax2.set_ylabel("Monetario medio (£)", fontsize=11)
    ax1.set_title("Tamaño y valor medio por segmento", fontsize=13)

    lineas1, nombres1 = ax1.get_legend_handles_labels()
    lineas2, nombres2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, nombres1 + nombres2, fontsize=10, loc="upper right")

    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)
