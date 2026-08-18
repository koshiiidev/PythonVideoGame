"""
pantalla de jugador selecciona nombre e icono

se apila sobre el menu, asi que al cerrarla el menu sigue donde estaba
se puede escribir con el teclado, elige el icono con las flechas y confirma con Enter
valida que no deja nombres vacios
"""

import pygame

from config import settings as ajustes
from src.core import recursos
from src.core.gestor_escenas import Escena

FUENTES = ('consolas', 'couriernew', 'dejavusansmono', 'verdana', 'arial')


class EscenaJugador(Escena):

    def __init__(self, gestor):
        Escena.__init__(self, gestor)
        self.estado = gestor.estado
        self.transparente = True          # el menú se sigue viendo debajo

        self.ex = ajustes.ANCHO / 800.0
        self.ey = ajustes.ALTO / 600.0

        self.font = pygame.font.SysFont(FUENTES, int(24 * self.ey), bold=True)
        self.font_chico = pygame.font.SysFont(FUENTES, int(16 * self.ey))

        #region Valores iniciales
        self.nombre = self.estado.nombre
        self.indice_icono = list(ajustes.ICONOS_JUGADOR).index(self.estado.icono)
        self.error = ''
        #endregion

        #region Iconos ya cargados
        lado = int(64 * self.ey)
        self.iconos = []
        for nombre in ajustes.ICONOS_JUGADOR:
            img = recursos.imagen('%s/%s' % (ajustes.DIR_RETRATOS, nombre), (lado, lado))
            self.iconos.append(img)
        #endregion

    #region Eventos
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        if evento.key == pygame.K_ESCAPE:
            self.gestor.desapilar()
        elif evento.key in (pygame.K_LEFT, pygame.K_UP):
            self.indice_icono = (self.indice_icono - 1) % len(ajustes.ICONOS_JUGADOR)
        elif evento.key in (pygame.K_RIGHT, pygame.K_DOWN):
            self.indice_icono = (self.indice_icono + 1) % len(ajustes.ICONOS_JUGADOR)
        elif evento.key == pygame.K_BACKSPACE:
            self.nombre = self.nombre[:-1]
            self.error = ''
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.confirmar()
        else:
            self.escribir(evento)

    def escribir(self, evento):
        """Solo letras, números y espacio, hasta el largo máximo."""
        caracter = evento.unicode
        if not caracter or not (caracter.isalnum() or caracter == ' '):
            return
        if len(self.nombre) >= ajustes.LARGO_MAX_NOMBRE:
            self.error = 'Máximo %d caracteres' % ajustes.LARGO_MAX_NOMBRE
            return
        self.nombre += caracter
        self.error = ''

    def confirmar(self):
        icono = ajustes.ICONOS_JUGADOR[self.indice_icono]
        try:
            self.estado.configurar_jugador(self.nombre, icono)
        except ValueError as e:
            self.error = str(e)
            return
        if self.gestor.audio:
            self.gestor.audio.sfx('menu_ok.wav')
        self.gestor.desapilar()
    #endregion

    #region Dibujo
    def dibujar(self, pantalla):
        # Oscurecer lo de atrás para que el panel resalte
        fondo_oscuro = pygame.Surface((ajustes.ANCHO, ajustes.ALTO), pygame.SRCALPHA)
        fondo_oscuro.fill((10, 8, 6, 190))
        pantalla.blit(fondo_oscuro, (0, 0))

        #dibujar recuadro de panel
        ancho = int(440 * self.ex)
        alto = int(300 * self.ey)
        panel = pygame.Rect(ajustes.ANCHO // 2 - ancho // 2,
                            ajustes.ALTO // 2 - alto // 2, ancho, alto)
        pygame.draw.rect(pantalla, (46, 32, 20), panel, border_radius=int(10 * self.ey))
        pygame.draw.rect(pantalla, (150, 112, 66), panel, 3, border_radius=int(10 * self.ey))

        cx = panel.centerx
        y = panel.top + int(28 * self.ey)

        self._centrado(pantalla, 'JUGADOR', cx, y, (250, 226, 150), self.font)
        y += int(46 * self.ey)

        #region Nombre
        self._centrado(pantalla, 'Nombre', cx, y, (198, 180, 152), self.font_chico)
        y += int(26 * self.ey)

        caja = pygame.Rect(cx - int(150 * self.ex), y - int(16 * self.ey),
                           int(300 * self.ex), int(34 * self.ey))
        pygame.draw.rect(pantalla, (28, 20, 14), caja, border_radius=6)
        pygame.draw.rect(pantalla, (120, 92, 56), caja, 2, border_radius=6)
        # cursor parpadea con el reloj de pygame
        cursor = '_' if (pygame.time.get_ticks() // 500) % 2 == 0 else ' '
        self._centrado(pantalla, self.nombre + cursor, cx, y, (245, 238, 220), self.font)
        y += int(48 * self.ey)
        #endregion

        #region Icono
        self._centrado(pantalla, 'Icono', cx, y, (198, 180, 152), self.font_chico)
        y += int(20 * self.ey)
        icono = self.iconos[self.indice_icono]
        if icono:
            pantalla.blit(icono, (cx - icono.get_width() // 2, y))
            flecha_y = y + icono.get_height() // 2
            self._centrado(pantalla, '<', cx - int(70 * self.ex), flecha_y,
                           (250, 226, 150), self.font)
            self._centrado(pantalla, '>', cx + int(70 * self.ex), flecha_y,
                           (250, 226, 150), self.font)
        y += int(76 * self.ey)
        #endregion

        pie = self.error if self.error else 'Enter: confirmar   ·   Esc: cancelar'
        color = (255, 150, 130) if self.error else (188, 172, 146)
        self._centrado(pantalla, pie, cx, y, color, self.font_chico)

    def _centrado(self, pantalla, texto, cx, cy, color, fuente):
        img = fuente.render(texto, True, color)
        pantalla.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))
    #endregion
