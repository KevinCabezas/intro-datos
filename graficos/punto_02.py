import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Directorios
salidas_p2 = Path("../salidas_punto2")
graficos_dir = salidas_p2 / "graficos"
graficos_dir.mkdir(exist_ok=True)

# Cargar datos generados en el punto 2
ingreso_nivel = pd.read_csv(salidas_p2 / "ingreso_por_nivel_educativo_2016.csv")
ingreso_sexo = pd.read_csv(salidas_p2 / "ingreso_por_sexo_2016.csv")
tasas_edad = pd.read_csv(salidas_p2 / "tasas_por_grupo_edad_2016.csv")
tasas_nivel = pd.read_csv(salidas_p2 / "tasas_por_nivel_educativo_2016.csv")

# ----------------------------------------
# 1. INGRESO POR NIVEL EDUCATIVO (BARRAS)
# ----------------------------------------

plt.figure(figsize=(10, 6))
for aglo in ingreso_nivel["AGLOMERADO_NOM"].unique():
    subset = ingreso_nivel[ingreso_nivel["AGLOMERADO_NOM"] == aglo]
    plt.bar(subset["NIVEL_ED"] + (0.2 if aglo=="Partidos del GBA" else -0.2),
            subset["mediana_ipcf"],
            width=0.4,
            label=aglo)

plt.xlabel("Nivel educativo")
plt.ylabel("Mediana IPCF")
plt.title("Ingreso mediano según nivel educativo - Año 2016")
plt.legend()
plt.xticks(sorted(ingreso_nivel["NIVEL_ED"].unique()))

plt.tight_layout()
plt.savefig(graficos_dir / "ingreso_por_nivel_educativo_2016.png")
plt.close()

# ----------------------------------------
# 2. INGRESO POR SEXO (BARRAS)
# ----------------------------------------

plt.figure(figsize=(8, 6))
for aglo in ingreso_sexo["AGLOMERADO_NOM"].unique():
    subset = ingreso_sexo[ingreso_sexo["AGLOMERADO_NOM"] == aglo]
    plt.bar(subset["SEXO"] + " (" + aglo + ")",
            subset["mediana_ipcf"],
            label=aglo)

plt.ylabel("Mediana IPCF")
plt.title("Ingreso mediano según sexo - Año 2016")
plt.tight_layout()
plt.savefig(graficos_dir / "ingreso_por_sexo_2016.png")
plt.close()

# ----------------------------------------
# 3. TASAS POR GRUPO DE EDAD (BARRAS AGRUPADAS)
# ----------------------------------------

variables = ["tasa_actividad", "tasa_empleo", "tasa_desocupacion"]

for var in variables:
    plt.figure(figsize=(10, 6))

    for aglo in tasas_edad["AGLOMERADO_NOM"].unique():
        subset = tasas_edad[tasas_edad["AGLOMERADO_NOM"] == aglo]
        plt.bar(subset["GRUPO_EDAD"] + " (" + aglo + ")",
                subset[var],
                label=aglo)

    plt.ylabel(var.replace("_", " ").title())
    plt.title(f"{var.replace('_', ' ').title()} según grupo de edad - Año 2016")

    plt.tight_layout()
    plt.savefig(graficos_dir / f"{var}_por_grupo_edad_2016.png")
    plt.close()

# ----------------------------------------
# 4. TASAS POR NIVEL EDUCATIVO (BARRAS AGRUPADAS)
# ----------------------------------------

for var in variables:
    plt.figure(figsize=(10, 6))

    for aglo in tasas_nivel["AGLOMERADO_NOM"].unique():
        subset = tasas_nivel[tasas_nivel["AGLOMERADO_NOM"] == aglo]
        plt.bar(subset["NIVEL_ED"] + (0.2 if aglo=="Partidos del GBA" else -0.2),
                subset[var],
                width=0.4,
                label=aglo)

    plt.xlabel("Nivel educativo")
    plt.ylabel(var.replace("_", " ").title())
    plt.title(f"{var.replace('_', ' ').title()} según nivel educativo - Año 2016")
    plt.legend()
    plt.xticks(sorted(tasas_nivel["NIVEL_ED"].unique()))

    plt.tight_layout()
    plt.savefig(graficos_dir / f"{var}_por_nivel_educativo_2016.png")
    plt.close()

print("\n✅ GRÁFICOS DEL PUNTO 2 GENERADOS con éxito.")
print(f"Guardados en: {graficos_dir}")
