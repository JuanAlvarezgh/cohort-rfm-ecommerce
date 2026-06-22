"""Descarga el dataset Online Retail (UCI) a datos/."""
from pathlib import Path
from urllib.request import urlopen

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
DESTINO = Path("datos/Online Retail.xlsx")


def descargar():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    if DESTINO.exists():
        print(f"Ya existe: {DESTINO}")
        return
    print("Descargando dataset Online Retail desde UCI...")
    with urlopen(URL, timeout=60) as r:  # noqa: S310
        DESTINO.write_bytes(r.read())
    print(f"Guardado en {DESTINO} ({DESTINO.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    descargar()
