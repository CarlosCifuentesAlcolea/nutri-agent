import json
from datetime import date


MACROS = ("hc", "proteina", "grasa")


def nuevo_registro(tipo_dia):
    return {
        "fecha": date.today().isoformat(),
        "tipo_dia": tipo_dia,
        "comidas": [],
    }


def cargar_registro(ruta_registro, tipo_dia):
    if not ruta_registro.exists():
        return nuevo_registro(tipo_dia)

    with ruta_registro.open("r", encoding="utf-8") as archivo:
        registro = json.load(archivo)

    if registro.get("fecha") != date.today().isoformat():
        return nuevo_registro(tipo_dia)

    if registro.get("tipo_dia") != tipo_dia:
        registro["tipo_dia"] = tipo_dia

    return registro


def guardar_registro(ruta_registro, registro):
    ruta_registro.parent.mkdir(parents=True, exist_ok=True)

    with ruta_registro.open("w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, ensure_ascii=False, indent=2)


def registrar_comida(registro, momento, descripcion, hc=0, proteina=0, grasa=0):
    comida = {
        "momento": momento,
        "descripcion": descripcion,
        "hc": float(hc),
        "proteina": float(proteina),
        "grasa": float(grasa),
    }

    registro["comidas"].append(comida)
    return comida


def calcular_consumido(registro):
    consumido = {macro: 0 for macro in MACROS}

    for comida in registro["comidas"]:
        for macro in MACROS:
            consumido[macro] += float(comida.get(macro, 0))

    return consumido


def calcular_restante(objetivo, registro):
    consumido = calcular_consumido(registro)

    return {
        macro: float(objetivo[macro]) - consumido[macro]
        for macro in MACROS
    }


def reiniciar_registro(tipo_dia):
    return nuevo_registro(tipo_dia)
