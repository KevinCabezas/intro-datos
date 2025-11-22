import pandas as pd
from pathlib import Path

# ---------------------------------------------------
# LEER BASE INDIVIDUAL (ya procesada del punto 1)
# ---------------------------------------------------

carpeta = Path("../2016")
archivos = sorted(carpeta.glob("usu_individual_*.txt"))

print("Archivos encontrados:")
for a in archivos:
    print(" -", a)

dfs = []

for ruta in archivos:
    print(f"Leyendo {ruta.name}...")
    df = pd.read_csv(
        ruta,
        sep=";",
        quotechar='"',
        encoding="latin1",
        low_memory=False
    )

    columnas = [
        "ANO4","TRIMESTRE","AGLOMERADO","ESTADO","PONDERA",
        "P47T","IPCF","NIVEL_ED","CH04","CH06"
    ]

    cols_presentes = [c for c in columnas if c in df.columns]
    df = df[cols_presentes]

    dfs.append(df)

personas = pd.concat(dfs, ignore_index=True)
print("\nTotal registros:", len(personas))

# ---------------------------------------------------
# LIMPIEZA Y CONVERSIÓN
# ---------------------------------------------------

for col in ["IPCF","P47T","PONDERA","CH06","NIVEL_ED","ESTADO"]:
    if col in personas.columns:
        personas[col] = pd.to_numeric(personas[col], errors="coerce")

# Filtrar aglomerados correctos
personas = personas[personas["AGLOMERADO"].isin([27, 33])]

# Filtrar personas de 10+
personas = personas[personas["ESTADO"] != 4]

personas["AGLOMERADO_NOM"] = personas["AGLOMERADO"].map({
    27: "Gran San Juan",
    33: "Partidos del GBA",
})

personas["PERIODO"] = (
    personas["ANO4"].astype("Int64").astype(str)
    + "T"
    + personas["TRIMESTRE"].astype("Int64").astype(str)
)

# ---------------------------------------------------
# SOLO 2016 (PUNTO 2)
# ---------------------------------------------------

personas_2016 = personas[personas["ANO4"] == 2016]
print("\nRegistros año 2016:", len(personas_2016))

# Crear carpeta de salidas
salidas_dir = Path("../salidas_punto2")
salidas_dir.mkdir(exist_ok=True)

# ---------------------------------------------------
# A) INGRESOS SEGÚN NIVEL EDUCATIVO
# ---------------------------------------------------

def ingreso_por_educ(gr):
    x = gr["IPCF"].dropna()
    return pd.Series({
        "media_ipcf": x.mean(),
        "mediana_ipcf": x.median(),
        "q1_ipcf": x.quantile(0.25),
        "q3_ipcf": x.quantile(0.75)
    })

ingreso_nivel = (
    personas_2016
    .groupby(["AGLOMERADO_NOM","NIVEL_ED"])
    .apply(ingreso_por_educ)
    .reset_index()
)

ingreso_nivel.to_csv(salidas_dir / "ingreso_por_nivel_educativo_2016.csv",
                     index=False, encoding="utf-8-sig")

print("\nA) Ingreso por nivel educativo listo.")

# ---------------------------------------------------
# B) INGRESOS SEGÚN SEXO
# ---------------------------------------------------

personas_2016["SEXO"] = personas_2016["CH04"].map({
    1: "Varón",
    2: "Mujer"
})

ingreso_sexo = (
    personas_2016
    .groupby(["AGLOMERADO_NOM","SEXO"])
    .apply(ingreso_por_educ)
    .reset_index()
)

ingreso_sexo.to_csv(salidas_dir / "ingreso_por_sexo_2016.csv",
                    index=False, encoding="utf-8-sig")

print("B) Ingreso por sexo listo.")

# ---------------------------------------------------
# C) TASAS POR GRUPOS DE EDAD
# ---------------------------------------------------

def clasificar_edad(edad):
    if edad < 25:
        return "Jóvenes (15-24)"
    elif edad < 55:
        return "Adultos (25-54)"
    else:
        return "Mayores (55+)"

personas_2016["GRUPO_EDAD"] = personas_2016["CH06"].apply(clasificar_edad)

def tasas_laborales(gr):
    w = gr["PONDERA"]
    total = w.sum()
    activos = w[gr["ESTADO"].isin([1,2])].sum()
    ocupados = w[gr["ESTADO"] == 1].sum()
    desocupados = w[gr["ESTADO"] == 2].sum()

    return pd.Series({
        "tasa_actividad": activos/total*100 if total>0 else None,
        "tasa_empleo": ocupados/total*100 if total>0 else None,
        "tasa_desocupacion": desocupados/activos*100 if activos>0 else None
    })

tasas_edad = (
    personas_2016
    .groupby(["AGLOMERADO_NOM","GRUPO_EDAD"])
    .apply(tasas_laborales)
    .reset_index()
)

tasas_edad.to_csv(salidas_dir / "tasas_por_grupo_edad_2016.csv",
                  index=False, encoding="utf-8-sig")

print("C) Tasas por grupos de edad listas.")

# ---------------------------------------------------
# D) TASAS SEGÚN NIVEL EDUCATIVO
# ---------------------------------------------------

tasas_nivel = (
    personas_2016
    .groupby(["AGLOMERADO_NOM","NIVEL_ED"])
    .apply(tasas_laborales)
    .reset_index()
)

tasas_nivel.to_csv(salidas_dir / "tasas_por_nivel_educativo_2016.csv",
                   index=False, encoding="utf-8-sig")

print("D) Tasas por nivel educativo listas.")

# ---------------------------------------------------
# FIN
# ---------------------------------------------------

print("\nPUNTO 2 COMPLETO (Año 2016).")
print("Archivos generados en: ../salidas_punto2/")
