from difflib import SequenceMatcher
import re
import unicodedata

from parser import numero_a_float


MACROS = ("hc", "proteina", "grasa")
NOMBRES_MACROS = {
    "hc": "hidratos",
    "proteina": "proteina",
    "grasa": "grasa",
}


def sugerir_comidas(restante, equivalencias, preferencia="", max_sugerencias=3):
    opciones_por_macro = {}

    for macro, categoria in (
        ("hc", "hidratos"),
        ("proteina", "proteinas"),
        ("grasa", "grasas"),
    ):
        cantidad_restante = max(float(restante[macro]), 0)

        if cantidad_restante < 0.10:
            continue

        opciones = _buscar_equivalencias_simples(
            equivalencias[categoria],
            macro,
            preferencia,
            max_sugerencias,
        )

        if not opciones:
            continue

        equivalencias_a_usar = min(cantidad_restante, 1)
        opciones_por_macro[macro] = [
            _crear_linea_sugerencia(alimento, macro, equivalencias_a_usar)
            for alimento in opciones
        ]

    sugerencias = []

    for indice in range(max_sugerencias):
        sugerencia = []

        for macro in MACROS:
            opciones = opciones_por_macro.get(macro, [])

            if opciones:
                sugerencia.append(opciones[indice % len(opciones)])

        if sugerencia:
            sugerencias.append(sugerencia)

    return sugerencias


def sugerir_comida(restante, equivalencias):
    sugerencias = sugerir_comidas(restante, equivalencias, max_sugerencias=1)
    return sugerencias[0] if sugerencias else []


def _buscar_equivalencias_simples(alimentos, macro_objetivo, preferencia, limite):
    candidatos = []

    for alimento in alimentos:
        macros = alimento["macros"]

        if macros[macro_objetivo] == 1 and _total_macros(macros) == 1:
            candidatos.append(alimento)

    candidatos.sort(
        key=lambda alimento: _puntuar_preferencia(alimento, preferencia),
        reverse=True,
    )

    candidatos_preferidos = [
        alimento
        for alimento in candidatos
        if _puntuar_preferencia(alimento, preferencia) >= 0.15
    ]

    if candidatos_preferidos:
        return candidatos_preferidos[:limite]

    return candidatos[:limite]


def _puntuar_preferencia(alimento, preferencia):
    if not preferencia.strip():
        return 0

    preferencia_normalizada = _normalizar(preferencia)
    alimento_normalizado = _normalizar(
        f"{alimento['alimento']} {alimento['descripcion']}"
    )
    preferencia_tokens = set(preferencia_normalizada.split())
    alimento_tokens = set(alimento_normalizado.split())
    comunes = preferencia_tokens & alimento_tokens
    cobertura = len(comunes) / max(len(preferencia_tokens), 1)
    similitud = SequenceMatcher(None, preferencia_normalizada, alimento_normalizado).ratio()

    return cobertura * 0.80 + similitud * 0.20


def _normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    texto = re.sub(r"[^a-z0-9 ]+", " ", texto)
    palabras = []

    for palabra in texto.split():
        if palabra in ("de", "del", "con", "y", "en", "el", "la", "los", "las", "un", "una", "algo"):
            continue

        if palabra.endswith("s") and len(palabra) > 3:
            palabra = palabra[:-1]

        palabras.append(palabra)

    return " ".join(palabras)


def _total_macros(macros):
    return sum(float(macros[macro]) for macro in MACROS)


def _crear_linea_sugerencia(alimento, macro, equivalencias_a_usar):
    cantidad = numero_a_float(alimento["cantidad"])
    cantidad_ajustada = cantidad * equivalencias_a_usar if cantidad else None
    descripcion = _formatear_descripcion(alimento, cantidad_ajustada)

    return {
        "macro": macro,
        "macro_nombre": NOMBRES_MACROS[macro],
        "equivalencias": equivalencias_a_usar,
        "descripcion": descripcion,
        "alimento_base": alimento["descripcion"],
    }


def _formatear_descripcion(alimento, cantidad):
    if cantidad is None:
        return alimento["descripcion"]

    cantidad_texto = _formatear_numero(cantidad)
    unidad = alimento["unidad"]

    if unidad == "unidad":
        return f"{cantidad_texto} {alimento['alimento']}"

    return f"{cantidad_texto}{unidad} {alimento['alimento']}"


def _formatear_numero(numero):
    if numero.is_integer():
        return str(int(numero))

    return f"{numero:.2f}".rstrip("0").rstrip(".")
