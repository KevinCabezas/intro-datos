# with open("../2016/usu_individual_T216.txt", "r", encoding="latin1") as f:
#     print(f.readline())


import pandas as pd
from pathlib import Path
anio = "2025"
# ---------------------------------------------------
# CONFIGURACIÓN BÁSICA
# ---------------------------------------------------

# Carpeta donde están los TXT (desde /code apuntamos a ../data)
carpeta = Path(f"../{anio}")

# Buscar TODOS los archivos usu_individual_*.txt dentro de ../data
archivos = sorted(carpeta.glob("usu_individual_*.txt"))

print("Archivos encontrados:")
for a in archivos:
    print(" -", a)

if not archivos:
    raise FileNotFoundError("No se encontraron archivos 'usu_individual_*.txt' en ../data")

# ---------------------------------------------------
# LECTURA Y UNIÓN DE TODOS LOS TRIMESTRES
# ---------------------------------------------------

dfs = []

for ruta in archivos:
    print(f"\nLeyendo {ruta.name} ...")
    
    df = pd.read_csv(
        ruta,
        sep=";",
        quotechar='"',
        encoding="latin1",
        low_memory=False
    )

    # Columnas que necesitamos para el PUNTO 1
    columnas_necesarias = [
        "ANO4",
        "TRIMESTRE",
        "AGLOMERADO",
        "ESTADO",
        "PONDERA",
        "P47T",
        "IPCF",
    ]

    # Nos quedamos solo con las columnas que existan en este archivo
    cols_presentes = [c for c in columnas_necesarias if c in df.columns]
    df = df[cols_presentes]

    dfs.append(df)

# Unimos todos los trimestres
personas = pd.concat(dfs, ignore_index=True)
print("\nListo. Registros cargados TOTAL:", len(personas))

# ---------------------------------------------------
# LIMPIEZA Y FILTROS BÁSICOS
# ---------------------------------------------------

# Convertir a numérico (por si vienen como texto)
for col in ["P47T", "IPCF", "PONDERA", "AGLOMERADO", "ESTADO", "ANO4", "TRIMESTRE"]:
    if col in personas.columns:
        personas[col] = pd.to_numeric(personas[col], errors="coerce")

# Filtrar solo los dos aglomerados: 27 = Gran San Juan, 33 = Partidos del GBA
personas = personas[personas["AGLOMERADO"].isin([27, 33])]

# Filtrar solo personas de 10 años o más (ESTADO != 4)
# 1 = Ocupado, 2 = Desocupado, 3 = Inactivo, 4 = < 10 años
personas = personas[personas["ESTADO"] != 4]

# Etiqueta de aglomerado
personas["AGLOMERADO_NOM"] = personas["AGLOMERADO"].map({
    27: "Gran San Juan",
    33: "Partidos del GBA",
})

# Crear PERIODO tipo "2016T2"
personas["PERIODO"] = (
    personas["ANO4"].astype("Int64").astype(str)
    + "T"
    + personas["TRIMESTRE"].astype("Int64").astype(str)
)

print("\nRegistros luego de filtros (2 aglomerados, 10+ años):", len(personas))

# ---------------------------------------------------
# CÁLCULO DE TASAS LABORALES (PUNTO 1)
# ---------------------------------------------------

def calcular_tasas(gr: pd.DataFrame) -> pd.Series:
    w = gr["PONDERA"]

    total = w.sum()
    activos = w[gr["ESTADO"].isin([1, 2])].sum()
    ocupados = w[gr["ESTADO"] == 1].sum()
    desocupados = w[gr["ESTADO"] == 2].sum()

    tasa_actividad = activos / total * 100 if total > 0 else None
    tasa_empleo = ocupados / total * 100 if total > 0 else None
    tasa_desocupacion = desocupados / activos * 100 if activos > 0 else None

    return pd.Series({
        "tasa_actividad": tasa_actividad,
        "tasa_empleo": tasa_empleo,
        "tasa_desocupacion": tasa_desocupacion,
    })

tasas = (
    personas
    .groupby(["AGLOMERADO_NOM", "PERIODO"], group_keys=False)
    .apply(calcular_tasas)
    .reset_index()
    .sort_values(["AGLOMERADO_NOM", "PERIODO"])
)

print("\nTASAS LABORALES (primeras filas):")
print(tasas.head())
# ---------------------------------------------------
# CÁLCULO DE MEDIDAS DE INGRESO (IPCF) (PUNTO 1)
# ---------------------------------------------------

ingresos = personas.copy()

# Convertir IPCF a numérico por si viene como texto
ingresos["IPCF"] = pd.to_numeric(ingresos["IPCF"], errors="coerce")

# FILTRO NUEVO: excluir valores 0, negativos o nulos
ingresos = ingresos[ingresos["IPCF"] > 0]

def resumen_ingreso(gr: pd.DataFrame) -> pd.Series:
    x = gr["IPCF"].dropna()
    return pd.Series({
        "media_ipcf": x.mean(),
        "mediana_ipcf": x.median(),
        "q1_ipcf": x.quantile(0.25),
        "q3_ipcf": x.quantile(0.75),
    })

resumen_ing = (
    ingresos
    .groupby(["AGLOMERADO_NOM", "PERIODO"], group_keys=False)
    .apply(resumen_ingreso)
    .reset_index()
    .sort_values(["AGLOMERADO_NOM", "PERIODO"])
)


# ---------------------------------------------------
# GUARDAR RESULTADOS A ARCHIVOS CSV
# ---------------------------------------------------

salidas_dir = Path("../salidas")
salidas_dir.mkdir(exist_ok=True)

ruta_tasas = salidas_dir / f"tasas_{anio}_punto1.csv"
ruta_ingresos = salidas_dir / f"ingresos_{anio}_punto1.csv"

tasas.to_csv(ruta_tasas, index=False, encoding="utf-8-sig")
resumen_ing.to_csv(ruta_ingresos, index=False, encoding="utf-8-sig")

print(f"\nTasas guardadas en: {ruta_tasas}")
print(f"Resumen de ingresos guardado en: {ruta_ingresos}")
print("\nPUNTO 1 COMPLETADO (tasas + medidas de ingreso por trimestre).")
