"""
Cargador de niveles

Cada nivel es un módulo dentro de niveles/ pueblo.py, casa.py... y contiene
solo datos. Toda la lógica tiene que esta aqui en la clase Nivel

Los niveles no forman una lista ordenada sino que cada uno declara sus
propias salidas y ahí dice a qué nivel llevan. No hay un orden global que
mantener y agregar un nivel nuevo no obliga a tocar los que ya existen
"""

import importlib

from config import settings as ajustes

_cache = {}


class Nivel(object):
    """Envuelve el módulo de datos y le agrega el comportamiento."""

    def __init__(self, nombre, mod):
        self.nombre = nombre
        self.modulo = mod

        self.mapa = mod.MAPA
        self.terrenos = getattr(mod, 'TERRENOS', {})
        self.objetos = getattr(mod, 'OBJETOS', {})
        self.solidos = set(getattr(mod, 'SOLIDOS', ()))
        self.npcs = getattr(mod, 'NPCS', [])
        self.salidas = getattr(mod, 'SALIDAS', {})
        self.inicio = getattr(mod, 'JUGADOR_INICIO', None)
        self.musica = getattr(mod, 'MUSICA', None)
        self.titulo = getattr(mod, 'TITULO', nombre)

        self.filas = len(self.mapa)
        self.cols = max(len(f) for f in self.mapa)

    #region Consultas
    def celda(self, col, fil):
        """Qué hay en esa celda. Fuera del mapa devuelve pasto"""
        if 0 <= fil < self.filas and 0 <= col < len(self.mapa[fil]):
            return self.mapa[fil][col]
        return '.'

    def es_solido(self, col, fil):
        return self.celda(col, fil) in self.solidos

    def salida_en(self, col, fil):
        """Devuelve (nivel_destino, col, fil) si ese tile es una salida"""
        return self.salidas.get((col, fil))

    def ancho_px(self, tile_w):
        return self.cols * tile_w

    def alto_px(self, tile_h):
        return self.filas * tile_h
    #endregion


def cargar(nombre):
    if nombre not in _cache:
        mod = importlib.import_module('%s.%s' % (ajustes.PAQUETE_NIVELES, nombre))
        _cache[nombre] = Nivel(nombre, mod)
    return _cache[nombre]


def recargar(nombre):
    #vuelve a leer el archivo del disco
    mod = importlib.import_module('%s.%s' % (ajustes.PAQUETE_NIVELES, nombre))
    _cache[nombre] = Nivel(nombre, importlib.reload(mod))
    return _cache[nombre]


def limpiar_cache():
    _cache.clear()
