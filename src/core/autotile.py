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
        with open(os.path.join(carpeta, 'tileset_terreno.json'), encoding='utf-8') as f:
            self.man = json.load(f)
        self.ts = self.man['tile_size']
        self.escala = escala or self.ts
        self.pasto = [self._img('pasto', n) for n in self.man['terrenos']['pasto']['tiles']]
        self.sets = {}
        for terr in ('camino', 'tierra', 'agua'):
            d = self.man['terrenos'][terr]
            self.sets[terr] = {int(k): self._img(terr, v) for k, v in d['tiles'].items()}
        self.agua_esq = {k: self._img('agua', v)
                         for k, v in self.man['terrenos']['agua']['esquinas_internas'].items()}

    def _img(self, sub, nombre):
        ruta = os.path.join(self.carpeta, sub, nombre + '.png')
        img = pygame.image.load(ruta).convert_alpha()
        if self.escala != self.ts:
            img = pygame.transform.scale(img, (self.escala, self.escala))
        return img

    # ------------------------------------------------------------------
    @staticmethod
    def bitmask(mapa, x, y, ch):
        """Bits de los 4 vecinos que son del mismo terreno."""
        b = 0
        for bit, (dx, dy) in DXY.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(mapa) and 0 <= nx < len(mapa[ny]) and mapa[ny][nx] == ch:
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
    def recodos(mapa, x, y, ch, bits):
        #Esquinas concavas que hay que estampar encima.
        fuera = []
        for esq, ((dx, dy), req) in DIAG.items():
            if bits & req != req:
                continue
            ny, nx = y + dy, x + dx
            dentro = (0 <= ny < len(mapa) and 0 <= nx < len(mapa[ny]))
            if not dentro or mapa[ny][nx] != ch:
                fuera.append(esq)
        return fuera
