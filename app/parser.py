from openpyxl import load_workbook
import re


def extraer_objetivos(ruta_excel):
    wb = load_workbook(ruta_excel, data_only=True)

    ws = wb["Dieta"]

    hc_texto = str(ws["C6"].value)
    proteina = float(ws["D6"].value)
    grasa_texto = str(ws["E6"].value)

    hc_numeros = [int(x) for x in re.findall(r"\d+", hc_texto)]
    grasa_numeros = [int(x) for x in re.findall(r"\d+", grasa_texto)]

    objetivos = {
        "entrenamiento": {
            "hc": hc_numeros[0],
            "proteina": proteina,
            "grasa": grasa_numeros[0]
        },
        "descanso": {
            "hc": hc_numeros[1],
            "proteina": proteina,
            "grasa": grasa_numeros[1]
        }
    }

    return objetivos

def buscar_equivalencias(ruta_excel):
    wb = load_workbook(ruta_excel, data_only=True)

    ws = wb["Dieta"]

    for fila in range(1, 120):
        for col in range(1, 10):

            valor = ws.cell(fila, col).value

            if valor:
                texto = str(valor)

                if "1 HIDRATOS" in texto:
                    print("HC encontrado:", fila, col)

                if "1 PROTEÍNA" in texto:
                    print("PROTEINA encontrada:", fila, col)

                if "1 GRASA" in texto:
                    print("GRASA encontrada:", fila, col)

def mostrar_equivalencias(ruta_excel):
    wb = load_workbook(ruta_excel, data_only=True)

    ws = wb["Dieta"]

    for fila in range(20, 60):
        valores = []

        for col in range(2, 6):
            valor = ws.cell(fila, col).value

            if valor is not None:
                valores.append(str(valor))

        if valores:
            print(f"FILA {fila}: {valores}")

def cargar_hidratos(ruta_excel):
    wb = load_workbook(ruta_excel, data_only=True)
    ws = wb["Dieta"]

    for col in range(1, 10):
        valor = ws.cell(25, col).value
        print(f"Columna {col}: {valor}")