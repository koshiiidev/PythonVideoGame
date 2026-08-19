"""
autotile.py -- carga y autotileado del tileset de terreno 64x64.

Uso minimo:

    from autotile import Terreno
    terreno = Terreno('assets/tiles/terreno')          # carpeta del tileset

    # mapa: una matriz de strings o de ids.
    MAPA = [
        "..........",
        "..######..",
        "..#....#..",
        "..######..",
    ]

    # en el bucle de dibujo
    terreno.dibujar(pantalla, MAPA, camara_x, camara_y,
                    tipos={'#': 'camino', '@': 'tierra', '~': 'agua'})

Como funciona el bitmask
------------------------
Para cada celda se mira si el vecino de arriba/derecha/abajo/izquierda es del
MISMO terreno.  Cada vecino aporta un bit:

        N = 1        1
        E = 2     8 -+- 2
        S = 4        4
        W = 8

La suma (0..15) es el indice del tile.  Ejemplos:

    0  -> aislado / charco           10 -> recto horizontal
    1  -> remate que mira al Norte   11 -> T
    5  -> recto vertical             15 -> cruce / interior
"""
import json
import os
try:
    import pygame
except ImportError:
    pygame = None

N, E, S, W = 1, 2, 4, 8
DXY = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
# cada esquina: desplazamiento diagonal + los dos bits ortogonales que la rodean
DIAG = {'NW': ((-1, -1), N | W), 'NE': ((1, -1), N | E),
        'SE': ((1, 1), S | E), 'SW': ((-1, 1), S | W)}


class Terreno(object):
    def __init__(self, carpeta, escala=None):
        self.carpeta = carpeta

        # DEL MANIFIESTO SOLO SE USAN TRES COSAS, y son justamente las que NO se
        # pueden deducir del nombre de archivo:
        #   1. tile_size          de que tamano vienen los tiles en disco
        #   2. pasto.tiles        la lista de variantes de pasto (no son bitmask)
        #   3. agua.esquinas_internas   las calcomanias de esquina del agua
        # El resto del JSON (el indice bits -> archivo de cada terreno) quedo de
        # cuando el juego lo necesitaba. Hoy no se lee: el numero del nombre de
        # archivo ES el bitmask, asi que la carpeta se explica sola. Por eso
        # cerca y muro no aparecen en el JSON y aun asi funcionan
        with open(os.path.join(carpeta, 'tileset_terreno.json'), encoding='utf-8') as f:
            self.man = json.load(f)
        self.ts = self.man['tile_size']
        self.escala = escala or self.ts
        # El pasto no es bitmask: son variantes sueltas que se sortean por celda
        self.pasto = [self._img('pasto', n) for n in self.man['terrenos']['pasto']['tiles']]

        self.sets = {}
        for nombre in sorted(os.listdir(carpeta)):
            ruta = os.path.join(carpeta, nombre)
            if nombre == 'pasto' or not os.path.isdir(ruta):
                continue
            self.cargar_conjunto(nombre, ruta)

        # El agua ademas lleva calcomanias para las esquinas concavas: con 16
        # tiles no alcanza para dibujar una orilla que se mete hacia adentro
        self.agua_esq = {k: self._img('agua', v)
                         for k, v in self.man['terrenos']['agua']['esquinas_internas'].items()}

    def _img(self, sub, nombre):
        return self._cargar(os.path.join(self.carpeta, sub, nombre + '.png'))

    def _cargar(self, ruta):
        img = pygame.image.load(ruta).convert_alpha()
        if self.escala != self.ts:
            img = pygame.transform.scale(img, (self.escala, self.escala))
        return img

    def cargar_conjunto(self, nombre, carpeta):
        """
        Registra un juego de 16 tiles a partir de una carpeta.
            <loquesea>_<bits>_<descripcion>.png     ej. muro_10_recto_H.png
        """
        if pygame is None or not os.path.isdir(carpeta):
            return False
        juego = {}
        for archivo in sorted(os.listdir(carpeta)):
            if not archivo.endswith('.png'):
                continue
            partes = archivo[:-4].split('_')
            if len(partes) < 2 or not partes[1].isdigit():
                continue
            juego[int(partes[1])] = self._cargar(os.path.join(carpeta, archivo))
        # Si faltara alguna de las 16 combinaciones el mapa se veria con huecos,
        # asi que se prefiere no registrarlo antes que registrarlo a medias
        if len(juego) < 16:
            return False
        self.sets[nombre] = juego
        return True

    # ------------------------------------------------------------------
    @staticmethod
    def bitmask(mapa, x, y, ch, tambien=None):
        """
        Bits de los 4 vecinos que son del mismo terreno.

        "tambien" son otros caracteres que CONTINUAN ese terreno aunque se
        dibujen distinto. Sirve para una puerta en medio de un muro: sin esto
        el muro veria un hueco y se rematarian los dos lados, como si la pared
        se cortara ahi.
        """
        iguales = {ch} | set(tambien or ())
        b = 0
        for bit, (dx, dy) in DXY.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(mapa) and 0 <= nx < len(mapa[ny]) and mapa[ny][nx] in iguales:
                b |= bit
        return b

    def tile(self, terreno, bits):
        return self.sets[terreno][bits]

    # ------------------------------------------------------------------
    def dibujar(self, superficie, mapa, offx=0, offy=0, tipos=None, pasto_rand=None):
        """Pinta el mapa completo. `tipos` mapea el caracter -> nombre de terreno."""
        tipos = tipos or {'#': 'camino', '@': 'tierra', '~': 'agua'}
        t = self.escala
        for y, fila in enumerate(mapa):
            for x, ch in enumerate(fila):
                px, py = x * t + offx, y * t + offy
                # capa 0: siempre pasto debajo
                base = self.pasto[0]
                if pasto_rand is not None:
                    base = self.pasto[pasto_rand(x, y) % len(self.pasto)]
                superficie.blit(base, (px, py))
                terr = tipos.get(ch)
                if not terr:
                    continue
                b = self.bitmask(mapa, x, y, ch)
                superficie.blit(self.sets[terr][b], (px, py))
                if terr == 'agua':
                    for esq in self.recodos(mapa, x, y, ch, b):
                        superficie.blit(self.agua_esq[esq], (px, py))

    @staticmethod
    def recodos(mapa, x, y, ch, bits, tambien=None):
        #Esquinas concavas que hay que estampar encima.
        iguales = {ch} | set(tambien or ())
        fuera = []
        for esq, ((dx, dy), req) in DIAG.items():
            if bits & req != req:
                continue
            ny, nx = y + dy, x + dx
            dentro = (0 <= ny < len(mapa) and 0 <= nx < len(mapa[ny]))
            if not dentro or mapa[ny][nx] not in iguales:
                fuera.append(esq)
        return fuera
