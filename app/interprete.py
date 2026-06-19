from difflib import SequenceMatcher
import re
import unicodedata

from parser import numero_a_float


def _normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    texto = re.sub(r"[^a-z0-9 ]+", " ", texto)
    texto = re.sub(r"\b(de|del|con|y|en|el|la|los|las|un|una)\b", " ", texto)
    return " ".join(texto.split())


def _tokens(texto):
    return set(_normalizar(texto).split())


def _aplanar_equivalencias(equivalencias):
    alimentos = []

    for categoria, lista in equivalencias.items():
        for alimento in lista:
            copia = dict(alimento)
            copia["categoria"] = categoria
            alimentos.append(copia)

    return alimentos


def _puntuar(alimento_usuario, alimento):
    consulta = alimento_usuario["alimento"]
    consulta_normalizada = _normalizar(consulta)
    alimento_normalizado = _normalizar(alimento["alimento"])

    consulta_tokens = _tokens(consulta)
    alimento_tokens = _tokens(alimento["alimento"])

    comunes = consulta_tokens & alimento_tokens
    cobertura = len(comunes) / max(len(alimento_tokens), 1)
    similitud = SequenceMatcher(None, consulta_normalizada, alimento_normalizado).ratio()
    cercania_cantidad = _puntuar_cantidad(alimento_usuario["cantidad"], alimento["cantidad"])

    return cobertura * 0.50 + similitud * 0.15 + cercania_cantidad * 0.35


def _puntuar_cantidad(cantidad_usuario, cantidad_alimento):
    if cantidad_usuario is None or cantidad_alimento is None:
        return 0.0

    cantidad_base = numero_a_float(cantidad_alimento)

    if not cantidad_base:
        return 0.0

    return min(cantidad_usuario, cantidad_base) / max(cantidad_usuario, cantidad_base)


def interpretar_comida(texto, equivalencias):
    alimento_usuario = _parsear_texto_usuario(texto)
    candidatos = _aplanar_equivalencias(equivalencias)

    if not candidatos:
        return None

    mejor = max(candidatos, key=lambda alimento: _puntuar(alimento_usuario, alimento))
    puntuacion = _puntuar(alimento_usuario, mejor)

    if puntuacion < 0.20:
        return None

    cantidad_usuario = alimento_usuario["cantidad"]
    cantidad_base = numero_a_float(mejor["cantidad"])
    factor = 1.0

    if cantidad_usuario is not None and cantidad_base:
        factor = cantidad_usuario / cantidad_base

    macros = {
        "hc": mejor["macros"]["hc"] * factor,
        "proteina": mejor["macros"]["proteina"] * factor,
        "grasa": mejor["macros"]["grasa"] * factor,
    }

    return {
        "texto_usuario": texto,
        "coincidencia": mejor,
        "factor": factor,
        "puntuacion": puntuacion,
        "macros": macros,
    }


def _parsear_texto_usuario(texto):
    patron = r"(?P<cantidad>\d+(?:[,.]\d+)?(?:/\d+)?)\s*(?P<unidad>g|gr|ml)?\s+(?P<alimento>.+)"
    coincidencia = re.search(patron, texto, re.IGNORECASE)

    if not coincidencia:
        return {
            "cantidad": None,
            "unidad": None,
            "alimento": texto,
        }

    return {
        "cantidad": numero_a_float(coincidencia.group("cantidad")),
        "unidad": coincidencia.group("unidad") or "unidad",
        "alimento": coincidencia.group("alimento"),
    }
