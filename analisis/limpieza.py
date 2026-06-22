import pandas as pd

COLUMNAS_ES = {
    "InvoiceNo": "factura",
    "StockCode": "codigo_producto",
    "Description": "descripcion",
    "Quantity": "cantidad",
    "InvoiceDate": "fecha",
    "UnitPrice": "precio_unitario",
    "CustomerID": "id_cliente",
    "Country": "pais",
}


def cargar(ruta):
    """Lee el dataset desde .xlsx o .csv y renombra columnas a español."""
    ruta = str(ruta)
    if ruta.lower().endswith(".xlsx"):
        df = pd.read_excel(ruta)
    else:
        df = pd.read_csv(ruta)
    return df.rename(columns=COLUMNAS_ES)


def limpiar(df):
    """Quita cancelaciones, nulos de id_cliente, cantidades/precios no positivos; agrega monto."""
    df = df.copy()
    df = df[df["id_cliente"].notna()]
    df = df[~df["factura"].astype(str).str.startswith("C")]
    df = df[(df["cantidad"] > 0) & (df["precio_unitario"] > 0)]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["id_cliente"] = df["id_cliente"].astype(int)
    df["monto"] = df["cantidad"] * df["precio_unitario"]
    return df.reset_index(drop=True)
