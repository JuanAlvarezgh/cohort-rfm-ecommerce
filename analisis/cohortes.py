import pandas as pd


def matriz_retencion(df: pd.DataFrame) -> pd.DataFrame:
    """Matriz de retención por cohorte mensual.

    Cada cliente pertenece a la cohorte del mes de su primera compra.
    Devuelve un DataFrame: filas = cohorte (periodo mensual), columnas = indice de mes
    (0,1,2,...), valores = proporcion (0-1) de clientes de la cohorte activos ese mes.
    """
    df = df.copy()
    df["mes"] = df["fecha"].dt.to_period("M")
    df["cohorte"] = df.groupby("id_cliente")["mes"].transform("min")
    df["indice"] = (df["mes"] - df["cohorte"]).apply(lambda x: x.n)
    tabla = (
        df.groupby(["cohorte", "indice"])["id_cliente"].nunique().reset_index()
    )
    tam_cohorte = tabla[tabla["indice"] == 0].set_index("cohorte")["id_cliente"]
    pivote = tabla.pivot(index="cohorte", columns="indice", values="id_cliente")
    retencion = pivote.divide(tam_cohorte, axis=0)
    return retencion
