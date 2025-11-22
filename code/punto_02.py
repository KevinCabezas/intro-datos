import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------

base_dir = Path("..")   # cambiar si tu script está en otra ubicación
anios = list(range(2016, 2026))

# -----------------------------------------
# 1) LEER TODOS LOS TXT DE TODAS LAS CARPETAS
# -----------------------------------------

dfs = []

for anio in anios:
    carpeta_anio = base_dir / str(anio)

    if not carpeta_anio.exists():
        print(f"⚠ Carpeta {carpeta_anio} no existe, se saltea.")
        continue

    archivos = sorted(carpeta_anio.glob("usu_individual_*.txt"))

    if not archivos:
        print(f"⚠ No hay archivos en {carpeta_anio}")
        continue

    print(f"\nLeyendo archivos del año {anio}:")

    for ruta in archivos:
        print(" -", ruta.name)

        df = pd.read_csv(
            ruta,
            sep=";",
            encoding="latin1",
            quotechar='"',
            low_memory=False
        )

        columnas = [
            "ANO4","TRIMESTRE","AGLOMERADO","ESTADO","PONDERA",
            "P47T","IPCF","NIVEL_ED","CH04","CH06"
        ]

        cols = [c for c in columnas if c in df.columns]
        df = df[cols]

        dfs.append(df)

# Unir todo en un solo DataFrame
personas = pd.concat(dfs, ignore_index=True)
print("\nTotal registros cargados:", len(personas))

# -----------------------------------------
# 2) LIMPIEZA
# -----------------------------------------

for col in ["ANO4","TRIMESTRE","AGLOMERADO","ESTADO","PONDERA","IPCF","P47T","NIVEL_ED","CH04","CH06"]:
    if col in personas.columns:
        personas[col] = pd.to_numeric(personas[col], errors="coerce")

# Filtrar aglomerados
personas = personas[personas["AGLOMERADO"].isin([27,33])]

# Sacar menores de 10
personas = personas[personas["ESTADO"] != 4]

# Agregar columnas
personas["AGLOMERADO_NOM"] = personas["AGLOMERADO"].map({
    27: "Gran San Juan",
    33: "Partidos del GBA"
})

personas["PERIODO"] = personas["ANO4"].astype(int).astype(str) + "T" + personas["TRIMESTRE"].astype(int).astype(str)

personas["SEXO"] = personas["CH04"].map({1:"Varón", 2:"Mujer"})

def clasificar_edad(edad):
    if pd.isna(edad): return None
    if edad < 25: return "Jóvenes (15-24)"
    if edad < 55: return "Adultos (25-54)"
    return "Mayores (55+)"

personas["GRUPO_EDAD"] = personas["CH06"].apply(clasificar_edad)

# -----------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------

def ingreso_stats(gr):
    x = gr["IPCF"].dropna()
    return pd.Series({
        "media_ipcf": x.mean(),
        "mediana_ipcf": x.median(),
        "q1_ipcf": x.quantile(0.25),
        "q3_ipcf": x.quantile(0.75)
    })

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

# -----------------------------------------
# 3) ANALISIS MULTIANUAL
# -----------------------------------------

salidas = base_dir / "salidas_punto2_global"
salidas.mkdir(exist_ok=True)

# ---- A: INGRESO POR NIVEL EDUCATIVO (todos los años) ----
ingreso_nivel = (
    personas
    .groupby(["ANO4","PERIODO","AGLOMERADO_NOM","NIVEL_ED"])
    .apply(ingreso_stats)
    .reset_index()
)

ingreso_nivel.to_csv(salidas / "ingreso_por_nivel_educativo.csv",
                     index=False, encoding="utf-8-sig")

print("✔ ingreso_por_nivel_educativo.csv listo")

# ---- B: INGRESO POR SEXO ----
ingreso_sexo = (
    personas
    .groupby(["ANO4","PERIODO","AGLOMERADO_NOM","SEXO"])
    .apply(ingreso_stats)
    .reset_index()
)

ingreso_sexo.to_csv(salidas / "ingreso_por_sexo.csv",
                    index=False, encoding="utf-8-sig")

print("✔ ingreso_por_sexo.csv listo")

# ---- C: TASAS POR GRUPO DE EDAD ----
tasas_edad = (
    personas
    .groupby(["ANO4","PERIODO","AGLOMERADO_NOM","GRUPO_EDAD"])
    .apply(tasas_laborales)
    .reset_index()
)

tasas_edad.to_csv(salidas / "tasas_por_grupo_edad.csv",
                  index=False, encoding="utf-8-sig")

print("✔ tasas_por_grupo_edad.csv listo")

# ---- D: TASAS POR NIVEL EDUCATIVO ----
tasas_nivel = (
    personas
    .groupby(["ANO4","PERIODO","AGLOMERADO_NOM","NIVEL_ED"])
    .apply(tasas_laborales)
    .reset_index()
)

tasas_nivel.to_csv(salidas / "tasas_por_nivel_educativo.csv",
                   index=False, encoding="utf-8-sig")

print("✔ tasas_por_nivel_educativo.csv listo")

print("\nPUNTO 2 COMPLETO (TODOS LOS AÑOS EN ARCHIVOS GLOBALES)")
print(f"Salidas creadas en: {salidas.resolve()}")
