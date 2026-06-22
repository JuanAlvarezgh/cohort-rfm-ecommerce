"""Genera los graficos del analisis y muestra un resumen con resultados reales."""

import io
import sys
from pathlib import Path

# Forzar salida UTF-8 en Windows (evita UnicodeEncodeError con cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from analisis.cohortes import matriz_retencion  # noqa: E402
from analisis.graficos import (  # noqa: E402
    dispersion_segmentos,
    grafico_codo,
    heatmap_cohortes,
    perfil_segmentos,
)
from analisis.limpieza import cargar, limpiar  # noqa: E402
from analisis.rfm import metodo_codo, segmentar, tabla_rfm  # noqa: E402

RUTA_DATOS = Path("datos/Online Retail.xlsx")
RUTA_IMG = Path("docs/img")


def _asegurar_datos():
    """Descarga el dataset si no existe."""
    if not RUTA_DATOS.exists():
        import subprocess

        subprocess.check_call([sys.executable, "descargar_datos.py"])


def _sep(titulo=""):
    ancho = 64
    if titulo:
        linea = f"--- {titulo} "
        print(linea + "-" * max(0, ancho - len(linea)))
    else:
        print("-" * ancho)


def main():
    _asegurar_datos()

    # --- Carga y limpieza ---
    df = limpiar(cargar(str(RUTA_DATOS)))

    # --- Analisis ---
    matriz = matriz_retencion(df)
    rfm = tabla_rfm(df)
    inercias = metodo_codo(rfm)
    seg = segmentar(rfm, k=4, semilla=42)

    # --- Graficos ---
    RUTA_IMG.mkdir(parents=True, exist_ok=True)
    heatmap_cohortes(matriz, RUTA_IMG / "heatmap_cohortes.png")
    grafico_codo(inercias, RUTA_IMG / "codo_kmeans.png")
    dispersion_segmentos(seg, RUTA_IMG / "dispersion_segmentos.png")
    perfil_segmentos(seg, RUTA_IMG / "perfil_segmentos.png")

    # --- Resumen ---
    fecha_min = df["fecha"].min()
    fecha_max = df["fecha"].max()
    num_clientes = df["id_cliente"].nunique()
    num_facturas = df["factura"].nunique()
    pais_principal = df.groupby("pais")["factura"].nunique().idxmax()

    # Retencion mes 1 y mes 3 (promedio sobre cohortes)
    retencion_mes1 = matriz[1].dropna().mean() if 1 in matriz.columns else float("nan")
    retencion_mes3 = matriz[3].dropna().mean() if 3 in matriz.columns else float("nan")

    print()
    _sep("RESUMEN DEL ANALISIS DE CLIENTES -- COHORT-RFM ECOMMERCE")
    periodo = f"{fecha_min.strftime('%Y-%m-%d')} al {fecha_max.strftime('%Y-%m-%d')}"
    print(f"  Periodo          : {periodo}")
    print(f"  Clientes unicos  : {num_clientes:,}")
    print(f"  Facturas unicas  : {num_facturas:,}")
    print(f"  Pais principal   : {pais_principal}")
    _sep()

    print()
    _sep("RETENCION MEDIA POR COHORTE")
    print(f"  Mes 1  : {retencion_mes1:.1%}")
    print(f"  Mes 3  : {retencion_mes3:.1%}")
    _sep()

    print()
    _sep("PERFIL DE SEGMENTOS (k-means, k=4)")
    total = len(seg)
    orden = ["Campeones", "Leales", "En riesgo", "Perdidos"]
    perfil = seg.groupby("etiqueta").agg(
        num_clientes=("id_cliente", "count"),
        recencia_media=("recencia", "mean"),
        frecuencia_media=("frecuencia", "mean"),
        monetario_medio=("monetario", "mean"),
    ).reindex(orden)

    encabezado = (
        f"  {'Segmento':<12} {'Clientes':>9} {'% total':>8} "
        f"{'Recencia':>10} {'Frecuencia':>11} {'Monetario':>11}"
    )
    print(encabezado)
    print("  " + "-" * 62)
    for etiqueta, fila in perfil.iterrows():
        pct = fila["num_clientes"] / total * 100
        print(
            f"  {etiqueta:<12} {int(fila['num_clientes']):>9,} {pct:>7.1f}% "
            f"  {fila['recencia_media']:>8.1f}d "
            f"  {fila['frecuencia_media']:>8.1f}  "
            f"  GBP{fila['monetario_medio']:>8.2f}"
        )
    _sep()

    print()
    _sep("RECOMENDACIONES POR SEGMENTO")
    recomendaciones = {
        "Campeones": (
            "Fidelizar con programa VIP o acceso anticipado a nuevas colecciones. "
            "Son los clientes de mayor valor; mantener la relacion activa."
        ),
        "Leales": (
            "Incentivar con descuentos por volumen o beneficios de membresia "
            "para aumentar su frecuencia y monetario."
        ),
        "En riesgo": (
            "Campana de reactivacion urgente: correo personalizado con oferta "
            "especial. El tiempo de inactividad aun es recuperable."
        ),
        "Perdidos": (
            "Campana de win-back con descuento agresivo o encuesta de satisfaccion. "
            "Si no responden, reducir inversion publicitaria en este segmento."
        ),
    }
    for seg_nombre, recomendacion in recomendaciones.items():
        print(f"  {seg_nombre}:")
        print(f"    {recomendacion}")
        print()
    _sep()

    print()
    print("  Graficos generados en docs/img/:")
    for ruta in sorted(RUTA_IMG.glob("*.png")):
        tam_kb = ruta.stat().st_size // 1024
        print(f"    {ruta.name:<35} ({tam_kb} KB)")
    print()


if __name__ == "__main__":
    main()
