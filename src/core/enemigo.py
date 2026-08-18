"""
Cada enemigo se mueve solo: si el jugador esta cerca lo persigue, y si no
deambula. La escena le pasa la funcion para consultar si una posicion choca con el mapa
"""

import math
import random
import pygame

from config import settings as ajustes
from src.core import geometria


class Enemigo(object):

    def __init__(self, x, y, tipo='sombra', velocidad=None, vida=1,
                 dano=1, puntos=None):
        #region Validaciones
        vida = int(vida)
        if vida < 1:
            raise ValueError('Un enemigo necesita al menos un punto de vida')
        #endregion

        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        self.velocidad = float(velocidad or ajustes.DIFICULTADES[
            ajustes.DIFICULTAD_POR_DEFECTO]['velocidad'])
        self.vida = vida
        self.dano = int(dano)
        self.puntos = int(ajustes.PUNTOS_POR_ENEMIGO if puntos is None else puntos)

        #region Estado interno
        self.vivo = True
        self.cuadro = 0
        self._t_cuadro = 0.0
        self._t_rumbo = 0.0
        self._rumbo = (0.0, 0.0)
        self._rng = random.Random(int(x) * 31 + int(y) * 17)
        #endregion

    #region Medidas
    @property
    def rect(self):
        """Caja completa, para dibujar y para recibir golpes."""
        lado = ajustes.ENEMIGO_LADO
        return pygame.Rect(int(self.x), int(self.y), lado, lado)

    @property
    def hitbox(self):
        #Solo la base, igual que el jugador: asi se pueden cruzar por arriba
        return geometria.caja_pies_enemigo(self.x, self.y)

    @property
    def y_sort(self):
        return self.y + ajustes.ENEMIGO_LADO
    #endregion

    #region Movimiento
    def _elegir_rumbo(self):
        angulo = self._rng.uniform(0, 2 * math.pi)
        self._rumbo = (math.cos(angulo), math.sin(angulo))
        self._t_rumbo = self._rng.uniform(0.8, 2.2)

    def actualizar(self, dt, objetivo, choca):
        #"objetivo" es el x, y del jugador. choca recibe un Rect y dice
        # si esa posicion es solida.
        if not self.vivo:
            return

        dx, dy = self._direccion(dt, objetivo)
        paso = self.velocidad * dt

        # Cada eje por separado, igual que el jugador: asi rozar una pared no
        # frena el movimiento en la otra direccion
        nueva_x = self.x + dx * paso
        if not choca(geometria.caja_pies_enemigo(nueva_x, self.y)):
            self.x = nueva_x

        nueva_y = self.y + dy * paso
        if not choca(geometria.caja_pies_enemigo(self.x, nueva_y)):
            self.y = nueva_y

        self._animar(dt)

    def _direccion(self, dt, objetivo):
        #Persigue si ve al jugador si no deambula
        if objetivo:
            ox, oy = objetivo
            dx = ox - self.x
            dy = oy - self.y
            distancia = math.hypot(dx, dy)
            if 0 < distancia <= ajustes.DISTANCIA_VISION:
                return dx / distancia, dy / distancia

        self._t_rumbo -= dt
        if self._t_rumbo <= 0:
            self._elegir_rumbo()
        return self._rumbo

    def _animar(self, dt):
        self._t_cuadro += dt
        if self._t_cuadro >= 1.0 / ajustes.FPS_ENEMIGO:
            self.cuadro = (self.cuadro + 1) % ajustes.CUADROS_ENEMIGO
            self._t_cuadro = 0.0
    #endregion

    #region Combate
    def recibir_golpe(self, dano=1):
        #Devuelve True si el golpe lo mato
        if not self.vivo:
            return False
        self.vida -= max(1, int(dano))
        if self.vida <= 0:
            self.vivo = False
            return True
        return False

    def toca(self, rect):
        return self.vivo and self.hitbox.colliderect(rect)
    #endregion

    def __repr__(self):
        return '<Enemigo %s (%d,%d) vida=%d>' % (self.tipo, self.x, self.y, self.vida)
