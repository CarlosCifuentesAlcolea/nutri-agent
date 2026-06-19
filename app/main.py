from pathlib import Path

from parser import cargar_equivalencias, extraer_objetivos
from registro import (
    calcular_consumido,
    calcular_restante,
    cargar_registro,
    guardar_registro,
    registrar_comida,
    reiniciar_registro,
)


EXCEL = Path("data") / "B05 Carlos C.xlsx"
REGISTRO = Path("data") / "registro_diario.json"


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


def pedir_numero(texto):
    while True:
        valor = input(texto).strip().replace(",", ".")

        try:
            return float(valor or 0)
        except ValueError:
            print("Introduce un numero valido.")


def pedir_comida():
    descripcion = input("Que has comido?: ").strip()
    hc = pedir_numero("Equivalencias de hidratos: ")
    proteina = pedir_numero("Equivalencias de proteina: ")
    grasa = pedir_numero("Equivalencias de grasa: ")

    return descripcion, hc, proteina, grasa


def mostrar_equivalencias(nombre, equivalencias):
    print(f"\nEquivalencias de {nombre} encontradas: {len(equivalencias)}\n")

    for indice, alimento in enumerate(equivalencias, start=1):
        print(
            f"{indice}. {alimento['descripcion']} "
            f"({alimento['intercambio']})"
        )


def mostrar_menu():
    print("\nMenu:")
    print("1. Ver objetivo del dia")
    print("2. Ver equivalencias de hidratos")
    print("3. Ver equivalencias de proteinas")
    print("4. Ver equivalencias de grasas")
    print("5. Registrar comida")
    print("6. Ver consumido hoy")
    print("7. Ver restante")
    print("8. Reiniciar registro de hoy")
    print("9. Salir")


def main():
    objetivos = extraer_objetivos(EXCEL)
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
            mostrar_equivalencias("hidratos", equivalencias["hidratos"])
        elif opcion == "3":
            mostrar_equivalencias("proteinas", equivalencias["proteinas"])
        elif opcion == "4":
            mostrar_equivalencias("grasas", equivalencias["grasas"])
        elif opcion == "5":
            descripcion, hc, proteina, grasa = pedir_comida()
            registrar_comida(registro, descripcion, hc, proteina, grasa)
            guardar_registro(REGISTRO, registro)
            mostrar_macros("Restante tras registrar la comida", calcular_restante(objetivo, registro))
        elif opcion == "6":
            mostrar_macros("Consumido hoy", calcular_consumido(registro))
        elif opcion == "7":
            mostrar_macros("Restante hoy", calcular_restante(objetivo, registro))
        elif opcion == "8":
            registro = reiniciar_registro(tipo_dia)
            guardar_registro(REGISTRO, registro)
            print("\nRegistro de hoy reiniciado.")
        elif opcion == "9":
            print("\nHasta luego.")
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()
