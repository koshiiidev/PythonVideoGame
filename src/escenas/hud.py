"""
HUD de la partida que se ve encima

No es una escena, no recibe teclas ni se apila. Es solo un dibujante al que la
escena de juego le pasa la pantalla y el jugador
"""

import pygame

from config import settings as ajustes
from src.core import recursos

FUENTES = ('consolas', 'couriernew', 'dejavusansmono', 'verdana', 'arial')


class Hud(object):

    def __init__(self):
        self.ex = ajustes.ANCHO / 800.0
        self.ey = ajustes.ALTO / 600.0

        self.font = pygame.font.SysFont(FUENTES, int(18 * self.ey), bold=True)
        self.font_chico = pygame.font.SysFont(FUENTES, int(14 * self.ey), bold=True)

        #region Iconos
        lado = int(22 * self.ey)
        self.icono_vida = self._icono('vida', lado)
        self.icono_puntos = self._icono('monedas', lado)
        self.icono_kills = self._icono('experiencia', lado)
        self._retratos = {}
        #endregion

    def _icono(self, nombre, lado):
        return recursos.imagen('%s/%s.png' % (ajustes.DIR_ICONOS, nombre), (lado, lado))

    def _retrato(self, archivo):
        """El icono del jugador, cacheado por nombre de archivo."""
        if archivo not in self._retratos:
            lado = int(46 * self.ey)
            self._retratos[archivo] = recursos.imagen(
                '%s/%s' % (ajustes.DIR_RETRATOS, archivo), (lado, lado))
        return self._retratos[archivo]

    #region Dibujo
    def dibujar(self, pantalla, jugador):
        if jugador is None:
            return
        self._panel_izquierdo(pantalla, jugador)
        self._panel_derecho(pantalla, jugador)

    def _fondo(self, pantalla, rect):
        """Tabla translucida para que el texto se lea sobre cualquier mapa."""
        velo = pygame.Surface(rect.size, pygame.SRCALPHA)
        velo.fill((24, 16, 10, 165))
        pantalla.blit(velo, rect.topleft)
        pygame.draw.rect(pantalla, (122, 92, 54), rect, 2, border_radius=6)

    def _panel_izquierdo(self, pantalla, jugador):
        margen = int(10 * self.ex)
        alto = int(58 * self.ey)
        ancho = int(210 * self.ex)
        panel = pygame.Rect(margen, margen, ancho, alto)
        self._fondo(pantalla, panel)

        x = panel.left + int(6 * self.ex)
        retrato = self._retrato(jugador.icono)
        if retrato:
            pantalla.blit(retrato, (x, panel.centery - retrato.get_height() // 2))
            x += retrato.get_width() + int(8 * self.ex)

        nombre = self.font.render(jugador.nombre, True, (245, 232, 200))
        pantalla.blit(nombre, (x, panel.top + int(7 * self.ey)))

        # Un corazon por vida restante; las perdidas quedan apagadas
        y = panel.top + int(30 * self.ey)
        for i in range(jugador.vidas_iniciales):
            if self.icono_vida:
                icono = self.icono_vida
                if i >= jugador.vidas:
                    icono = icono.copy()
                    icono.set_alpha(70)
                pantalla.blit(icono, (x + i * int(24 * self.ex), y))

    def _panel_derecho(self, pantalla, jugador):
        margen = int(10 * self.ex)
        alto = int(58 * self.ey)
        ancho = int(180 * self.ex)
        panel = pygame.Rect(ajustes.ANCHO - ancho - margen, margen, ancho, alto)
        self._fondo(pantalla, panel)

        filas = [(self.icono_puntos, '%d' % jugador.puntos),
                 (self.icono_kills, '%d' % jugador.eliminados)]
        y = panel.top + int(6 * self.ey)
        for icono, texto in filas:
            x = panel.left + int(8 * self.ex)
            if icono:
                pantalla.blit(icono, (x, y))
                x += icono.get_width() + int(6 * self.ex)
            img = self.font.render(texto, True, (245, 232, 200))
            pantalla.blit(img, (x, y + int(2 * self.ey)))
            y += int(24 * self.ey)

    def aviso(self, pantalla, texto, color=(255, 226, 150)):
        """Mensaje grande y breve en el centro, para bonos y avisos."""
        img = self.font.render(texto, True, color)
        x = ajustes.ANCHO // 2 - img.get_width() // 2
        y = int(96 * self.ey)
        velo = pygame.Surface((img.get_width() + 24, img.get_height() + 12),
                              pygame.SRCALPHA)
        velo.fill((24, 16, 10, 180))
        pantalla.blit(velo, (x - 12, y - 6))
        pantalla.blit(img, (x, y))
    #endregion
