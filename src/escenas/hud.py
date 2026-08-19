"""
HUD de la partida que se ve encima

No es una escena, no recibe teclas ni se apila. Es solo un dibujo al que la
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
        #El icono del jugador
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
        #cuadro translucido
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

        # Un corazon por vida las perdidas quedan apagadas
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

    def objetivo(self, pantalla, faltan, titulo_nivel, jefe_vivo=False):
        #texto abajo con lo que falta para pasar el nivel.
        #El jefe manda: mientras siga en pie, no sirve de nada que no queden sombras
        if jefe_vivo:
            texto = '%s  ·  derrota a la bruja' % titulo_nivel
            color = (240, 176, 208)
        elif faltan <= 0:
            texto = '%s  ·  camino libre' % titulo_nivel
            color = (186, 211, 98)
        elif faltan == 1:
            texto = '%s  ·  falta 1 sombra' % titulo_nivel
            color = (232, 214, 176)
        else:
            texto = '%s  ·  faltan %d sombras' % (titulo_nivel, faltan)
            color = (232, 214, 176)
        img = self.font_chico.render(texto, True, color)
        x = ajustes.ANCHO // 2 - img.get_width() // 2
        y = ajustes.ALTO - int(52 * self.ey)
        velo = pygame.Surface((img.get_width() + 20, img.get_height() + 8),
                              pygame.SRCALPHA)
        velo.fill((24, 16, 10, 160))
        pantalla.blit(velo, (x - 10, y - 4))
        pantalla.blit(img, (x, y))

    def barra_jefe(self, pantalla, jefe, nombre='La Cangreja'):
        #Barra de vida del jefe, abajo y ancha, como en cualquier juego del genero
        ancho = int(420 * self.ex)
        alto = int(16 * self.ey)
        x = ajustes.ANCHO // 2 - ancho // 2
        y = ajustes.ALTO - int(78 * self.ey)

        img = self.font_chico.render(nombre.upper(), True, (238, 206, 214))
        pantalla.blit(img, (ajustes.ANCHO // 2 - img.get_width() // 2,
                            y - int(18 * self.ey)))

        marco = pygame.Rect(x, y, ancho, alto)
        velo = pygame.Surface(marco.size, pygame.SRCALPHA)
        velo.fill((20, 12, 16, 200))
        pantalla.blit(velo, marco.topleft)

        # Proporcion de vida restante
        parte = max(0.0, min(1.0, jefe.vida / float(jefe.vida_maxima)))
        if parte > 0:
            relleno = pygame.Rect(x + 2, y + 2, int((ancho - 4) * parte), alto - 4)
            # De morado a rojo segun se va debilitando
            color = (int(150 + 90 * (1 - parte)), int(40 + 20 * parte), int(120 * parte + 40))
            pygame.draw.rect(pantalla, color, relleno)
            pygame.draw.rect(pantalla, (232, 180, 220),
                             (relleno.x, relleno.y, relleno.width, max(1, alto // 4)))
        pygame.draw.rect(pantalla, (170, 130, 160), marco, 2)

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
