from pathlib import Path

from interprete import interpretar_comida
from parser import cargar_equivalencias, extraer_distribucion_comidas, extraer_objetivos
from registro import (
    calcular_consumido,
    calcular_consumido_momento,
    calcular_restante,
    cargar_registro,
    guardar_registro,
    registrar_comida,
    reiniciar_registro,
)
from sugerencias import sugerir_comidas


EXCEL = Path("data") / "B05 Carlos C.xlsx"
REGISTRO = Path("data") / "registro_diario.json"
MOMENTOS_DIA = ("desayuno", "almuerzo", "comida", "merienda", "cena", "otro")


def preguntar_tipo_dia():
    while True:
        respuesta = input("Has entrenado hoy? (si/no): ").strip().lower()

        if respuesta in ("si", "s", "yes", "y"):
            return "entrenamiento"

        if respuesta in ("no", "n"):
            return "descanso"

        print("Responde con 'si' o 'no'.")


def mostrar_objetivo(tipo_dia, objetivo):
    print(f"\nObjetivo de hoy ({tipo_dia}):")
    print(f"- Hidratos: {objetivo['hc']} equivalencias")
    print(f"- Proteina: {objetivo['proteina']} equivalencias")
    print(f"- Grasa: {objetivo['grasa']} equivalencias")


def mostrar_macros(titulo, macros):
    print(f"\n{titulo}:")
    print(f"- Hidratos: {macros['hc']:.2f}")
    print(f"- Proteina: {macros['proteina']:.2f}")
    print(f"- Grasa: {macros['grasa']:.2f}")


def mostrar_sugerencias_comida(restante, equivalencias, preferencia=""):
    sugerencias = sugerir_comidas(restante, equivalencias, preferencia)

    print("\nSugerencias de comida:")

    if not sugerencias:
        print("No te quedan equivalencias suficientes para proponer una comida.")
        return

    for indice, sugerencia in enumerate(sugerencias, start=1):
        print(f"\nOpcion {indice}:")

        for linea in sugerencia:
            print(
                f"- {linea['descripcion']} "
                f"({linea['equivalencias']:.2f} eq. de {linea['macro_nombre']})"
            )

        ingredientes = ", ".join(linea["descripcion"] for linea in sugerencia)
        print(f"Idea de plato: {ingredientes}.")

    print("\nPreparacion: ajusta el plato con estas cantidades y anade verduras libres si encaja con la comida.")
    print("\nAjustala con verduras libres si quieres mas volumen.")


def calcular_restante_momento(distribucion_comidas, registro, momento, restante_dia):
    objetivo_momento = distribucion_comidas.get(momento)

    if objetivo_momento is None:
        return restante_dia

    consumido_momento = calcular_consumido_momento(registro, momento)

    return {
        macro: min(
            max(objetivo_momento[macro] - consumido_momento[macro], 0),
            max(restante_dia[macro], 0),
        )
        for macro in ("hc", "proteina", "grasa")
    }


def pedir_numero(texto):
    while True:
        valor = input(texto).strip().replace(",", ".")

        try:
            return float(valor or 0)
        except ValueError:
            print("Introduce un numero valido.")


def pedir_momento_dia():
    print("\nMomento del dia:")

    for indice, momento in enumerate(MOMENTOS_DIA, start=1):
        print(f"{indice}. {momento}")

    while True:
        respuesta = input("Elige una opcion: ").strip().lower()

        if respuesta.isdigit():
            indice = int(respuesta)

            if 1 <= indice <= len(MOMENTOS_DIA):
                return MOMENTOS_DIA[indice - 1]

        if respuesta in MOMENTOS_DIA:
            return respuesta

        print("Elige una opcion valida.")


def pedir_confirmacion(texto):
    respuesta = input(texto).strip().lower()
    return respuesta in ("si", "s", "yes", "y")


def pedir_comida_interpretada(equivalencias):
    momento = pedir_momento_dia()
    descripcion = input("Que has comido?: ").strip()
    interpretacion = interpretar_comida(descripcion, equivalencias)

    if interpretacion is None:
        print("No he encontrado una equivalencia clara. Lo registramos manualmente.")
        hc = pedir_numero("Equivalencias de hidratos: ")
        proteina = pedir_numero("Equivalencias de proteina: ")
        grasa = pedir_numero("Equivalencias de grasa: ")
        return momento, descripcion, hc, proteina, grasa

    coincidencia = interpretacion["coincidencia"]
    macros = interpretacion["macros"]

    print("\nHe interpretado esto:")
    print(f"- Coincidencia: {coincidencia['descripcion']} ({coincidencia['intercambio']})")
    print(f"- Factor aplicado: {interpretacion['factor']:.2f}")
    print(f"- Hidratos: {macros['hc']:.2f}")
    print(f"- Proteina: {macros['proteina']:.2f}")
    print(f"- Grasa: {macros['grasa']:.2f}")

    if pedir_confirmacion("Quieres registrar estos valores? (si/no): "):
        return momento, descripcion, macros["hc"], macros["proteina"], macros["grasa"]

    print("Vale, lo registramos manualmente.")
    hc = pedir_numero("Equivalencias de hidratos: ")
    proteina = pedir_numero("Equivalencias de proteina: ")
    grasa = pedir_numero("Equivalencias de grasa: ")

    return momento, descripcion, hc, proteina, grasa


def mostrar_equivalencias(nombre, equivalencias):
    print(f"\nEquivalencias de {nombre} encontradas: {len(equivalencias)}\n")

    for indice, alimento in enumerate(equivalencias, start=1):
        print(
            f"{indice}. {alimento['descripcion']} "
            f"({alimento['intercambio']})"
        )


def mostrar_menu_equivalencias(equivalencias):
    while True:
        print("\nEquivalencias:")
        print("1. Hidratos")
        print("2. Proteinas")
        print("3. Grasas")
        print("4. Volver")

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            mostrar_equivalencias("hidratos", equivalencias["hidratos"])
        elif opcion == "2":
            mostrar_equivalencias("proteinas", equivalencias["proteinas"])
        elif opcion == "3":
            mostrar_equivalencias("grasas", equivalencias["grasas"])
        elif opcion == "4":
            break
        else:
            print("Opcion no valida.")


def mostrar_menu():
    print("\nMenu:")
    print("1. Ver objetivo del dia")
    print("2. Ver equivalencias")
    print("3. Registrar comida")
    print("4. Ver consumido hoy")
    print("5. Ver restante")
    print("6. Sugerir comida")
    print("7. Reiniciar registro de hoy")
    print("8. Salir")


def main():
    objetivos = extraer_objetivos(EXCEL)
    distribucion_comidas = extraer_distribucion_comidas(EXCEL)
    equivalencias = cargar_equivalencias(EXCEL)

    tipo_dia = preguntar_tipo_dia()
    objetivo = objetivos[tipo_dia]
    registro = cargar_registro(REGISTRO, tipo_dia)

    mostrar_objetivo(tipo_dia, objetivo)

    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            mostrar_objetivo(tipo_dia, objetivo)
        elif opcion == "2":
            mostrar_menu_equivalencias(equivalencias)
        elif opcion == "3":
            momento, descripcion, hc, proteina, grasa = pedir_comida_interpretada(equivalencias)
            registrar_comida(registro, momento, descripcion, hc, proteina, grasa)
            guardar_registro(REGISTRO, registro)
            mostrar_macros("Restante tras registrar la comida", calcular_restante(objetivo, registro))
        elif opcion == "4":
            mostrar_macros("Consumido hoy", calcular_consumido(registro))
        elif opcion == "5":
            mostrar_macros("Restante hoy", calcular_restante(objetivo, registro))
        elif opcion == "6":
            restante = calcular_restante(objetivo, registro)
            momento = pedir_momento_dia()
            restante_momento = calcular_restante_momento(
                distribucion_comidas,
                registro,
                momento,
                restante,
            )
            mostrar_macros(f"Restante para {momento}", restante_momento)
            preferencia = input("Quieres algo concreto? (opcional): ").strip()
            mostrar_sugerencias_comida(restante_momento, equivalencias, preferencia)
        elif opcion == "7":
            registro = reiniciar_registro(tipo_dia)
            guardar_registro(REGISTRO, registro)
            print("\nRegistro de hoy reiniciado.")
        elif opcion == "8":
            print("\nHasta luego.")
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()
