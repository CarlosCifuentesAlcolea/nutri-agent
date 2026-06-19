from pathlib import Path
from parser import cargar_hidratos

excel = Path("data") / "B05 Carlos C.xlsx"

hidratos = cargar_hidratos(excel)

print(f"\nEncontrados {len(hidratos)} hidratos\n")

for alimento in hidratos[:10]:
    print(alimento)