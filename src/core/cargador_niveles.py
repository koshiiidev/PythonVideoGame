"""
Cargador de niveles

Cada nivel es un modulo dentro de niveles/ pueblo.py, casa.py... y contiene solo datos

Los niveles no forman una lista ordenada sino que cada uno declara sus
propias salidas y ahí dice a qué nivel llevan. No hay un orden global que
mantener y agregar un nivel nuevo no obliga a tocar los que ya existen
"""

import importlib

from config import settings as ajustes
from src.core import geometria

_cache = {}

# En la capa DECOR el hueco es el espacio, no el punto
VACIO_DECOR = ' '


class Nivel(object):

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
        #que criatura puebla este nivel
        self.enemigo = getattr(mod, 'ENEMIGO', 'sombra')
        # Tile que se pinta debajo de todo None = pasto.
        self.suelo = getattr(mod, 'SUELO', None)
        # Caracteres que se dibujan mas grandes que su tile: caracter -> cuantos tiles de ancho ocupa
        self.altos = dict(getattr(mod, 'ALTOS', {}) or {})
        # Cuantas celdas BLOQUEA cada objeto grande: caracter -> (ancho, alto)
        # en tiles. Es distinto de ALTOS, que solo dice de que tamano se dibuja:
        # una casa puede verse de tres tiles de ancho y bloquear solo dos de
        # fondo, porque el techo no estorba
        self.huellas = dict(getattr(mod, 'HUELLAS', {}) or {})
        # Cuanto estorba cada cosa: se parte de la tabla comun de settings y el
        # nivel puede reescribir lo que quiera con su propio COLISIONES
        self.colisiones = dict(ajustes.COLISIONES)
        self.colisiones.update(getattr(mod, 'COLISIONES', {}) or {})
        # Caracteres que NO cortan un terreno: caracter del terreno -> los que
        # lo continuan. Una puerta en medio de un muro tiene que dejar que el
        # muro siga de largo, no rematarlo a los dos lados
        self.continuan = {c: set(otros)
                          for c, otros in (getattr(mod, 'CONTINUAN', {}) or {}).items()}
        # Objetos que se ordenan por PROFUNDIDAD: se dibujan junto con los
        # personajes segun la Y de su base, para poder caminar por detras.
        # Los de ALTOS ya entran solos, esto es para los que miden un tile
        self.profundidad = set(getattr(mod, 'PROFUNDIDAD', ()) or ())
        # Objetos PLANOS: estan tirados en el suelo, no parados sobre el. Una
        # alfombra se pisa, asi que se dibuja debajo de todo el mundo y NO entra
        # al orden por profundidad, aunque mida mas de una casilla
        self.planos = set(getattr(mod, 'PLANOS', ()) or ())
        # Cosas entre las que se puede pasar a proposito (el cafetal). Se parte
        # de la lista comun y el nivel puede agregar las suyas
        self.atravesables = set(ajustes.ATRAVESABLES) | set(
            getattr(mod, 'ATRAVESABLES', ()) or ())
        # Jefe del nivel. Es un diccionario. None = nivel sin jefe.
        self.jefe = getattr(mod, 'JEFE', None)
        # cuantos hay que derrotar para despejar el nivel. 0 = ninguno
        self.objetivo = int(getattr(mod, 'OBJETIVO', 0))
        # el nivel que cierra la historia al despejarlo se gana el juego
        self.es_final = bool(getattr(mod, 'ES_FINAL', False))

        self.filas = len(self.mapa)
        self.cols = max(len(f) for f in self.mapa)

        # Capa de ENCIMA, opcional. MAPA es el suelo y lo que ocupa la celda
        # entera; DECOR es lo que se PARA sobre ese suelo. Son dos porque una
        # celda guarda un solo caracter: con una sola capa, poner un barril en
        # el camino borraba el camino y quedaba un hueco de pasto debajo.
        # Se rellena al tamano de MAPA para no revisar limites al leerla.
        self.decor = self._normalizar(getattr(mod, 'DECOR', None))

        # Se resuelve una sola vez al cargar el nivel, no en cada frame
        self.bloqueados = self._calcular_bloqueados()

    def _normalizar(self, decor):
        #Deja la capa de decoracion con exactamente filas x cols caracteres
        if not decor:
            return None
        return [(decor[i] if i < len(decor) else '')
                .ljust(self.cols, VACIO_DECOR)[:self.cols]
                for i in range(self.filas)]

    def _calcular_bloqueados(self):
        #Convierte las HUELLAS en un conjunto de celdas (col, fil) ocupadas.
        # Diccionario celda -> letra del objeto que la ocupa, no un conjunto:
        # asi se puede decir DE QUE es la huella cuando algo sale mal, en vez
        # de reportar el '.' que hay escrito en el mapa
        celdas = {}
        for fil in range(self.filas):
            for col in range(len(self.mapa[fil])):
                letra = self.mapa[fil][col]
                huella = self.huellas.get(letra)
                if not huella:
                    continue
                ancho, alto = huella
                izquierda = (ancho - 1) // 2
                for dx in range(-izquierda, ancho - izquierda):
                    for dy in range(alto):
                        celdas[(col + dx, fil - dy)] = letra
        return celdas

    #region Consultas
    def celda(self, col, fil):
        #Que hay en la celda, fuera del mapa devuelve pasto
        if 0 <= fil < self.filas and 0 <= col < len(self.mapa[fil]):
            return self.mapa[fil][col]
        return '.' #pasto o suelo base del nivel

    def adorno(self, col, fil):
        #Que hay en la capa de encima. Vacio si no hay capa o no hay nada ahi
        if self.decor is None:
            return VACIO_DECOR
        if 0 <= fil < self.filas and 0 <= col < self.cols:
            return self.decor[fil][col]
        return VACIO_DECOR

    def es_solido(self, col, fil):
        # Una celda estorba si el caracter de CUALQUIERA de las dos capas es
        # solido, o si le cae encima la huella de un objeto grande vecino
        if (col, fil) in self.bloqueados:
            return True
        return (self.celda(col, fil) in self.solidos
                or self.adorno(col, fil) in self.solidos)

    def colision(self, col, fil):
        """
        Que estorba en esa casilla: (ancho, alto, anclaje).

        En la tabla el anclaje es opcional; si no se escribe, la caja se apoya
        abajo y va centrada Aqui se completa para que quien lo use no tenga que preguntarse si viene o no.

        Si la casilla esta tapada por la huella de un objeto grande, estorba
        entera
        """
        if (col, fil) in self.bloqueados:
            medida = (1.0, 1.0)
        else:
            # Si lo que estorba esta en la capa de encima manda esa: el suelo
            # de abajo (un camino, un piso) no bloquea nada por si mismo
            adorno = self.adorno(col, fil)
            caracter = adorno if adorno in self.solidos else self.celda(col, fil)
            medida = self.colisiones.get(caracter,
                                         ajustes.COLISION_POR_DEFECTO)
        if len(medida) >= 3:
            return tuple(medida[:3])
        return (medida[0], medida[1], geometria.ANCLAJE_POR_DEFECTO)

    def salida_en(self, col, fil):
        """Devuelve (nivel_destino, col, fil) si ese tile es una salida"""
        return self.salidas.get((col, fil))

    def ancho_px(self, tile_w):
        return self.cols * tile_w

    def alto_px(self, tile_h):
        return self.filas * tile_h
    #endregion

    #region Revision
    def problemas(self):
        """
        Errores del nivel, en texto. Lista vacia = el nivel esta bien.

        Caza los errores tipicos de dibujar un mapa a mano sin tener que abrir
        el juego a buscarlos a ojo. Las revisiones NO estan aqui: viven en
        src/core/revision_niveles.py, para que las use igual el validador de
        herramientas/ y el corredor de pruebas, sin que existan dos copias que
        se vayan separando con el tiempo.
        """
        from src.core import revision_niveles
        return revision_niveles.problemas(self)
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
