"""Menú principal. Flechas o W/S para moverse, Enter o Espacio para elegir."""

import pygame

from config import settings as ajustes
from src.core.scene_manager import Escena


class EscenaMenu(Escena):

    def __init__(self, gestor):
        Escena.__init__(self, gestor)
        self.font_titulo = pygame.font.SysFont(None, 64)
        self.font_opcion = pygame.font.SysFont(None, 34)
        self.font_pie = pygame.font.SysFont(None, 20)

        # texto, función a ejecutar
        self.opciones = [
            ('Jugar', self.jugar),
            ('Ver intro', self.ver_intro),
            ('Salir', self.gestor.terminar),
        ]
        self.seleccion = 0

    def entrar(self):
        if self.gestor.audio:
            self.gestor.audio.musica('menu.ogg') #aun falta el audio

    #region Acciones
    def jugar(self):
        from src.escenas.juego import EscenaJuego
        self.gestor.estado.reiniciar()
        self.gestor.cambiar(EscenaJuego(self.gestor))

    def ver_intro(self):
        from src.escenas.cinematica import EscenaCinematica, INTRO
        self.gestor.apilar(EscenaCinematica(self.gestor, INTRO))
    #endregion

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.seleccion = (self.seleccion - 1) % len(self.opciones)
            self._sonar('menu_mover.wav')
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.seleccion = (self.seleccion + 1) % len(self.opciones)
            self._sonar('menu_mover.wav')
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self._sonar('menu_ok.wav')
            self.opciones[self.seleccion][1]()
        elif evento.key == pygame.K_ESCAPE:
            self.gestor.terminar()

    def _sonar(self, nombre):
        if self.gestor.audio:
            self.gestor.audio.sfx(nombre)

    def dibujar(self, pantalla):
        pantalla.fill(ajustes.MENU_FONDO)

        titulo = self.font_titulo.render('Zelda Tico', True, ajustes.MENU_RESALTE)
        pantalla.blit(titulo, (ajustes.ANCHO // 2 - titulo.get_width() // 2, 110))

        sub = self.font_pie.render('La Leyenda de la Cangreja', True, ajustes.MENU_TEXTO)
        pantalla.blit(sub, (ajustes.ANCHO // 2 - sub.get_width() // 2, 175))

        for i, (texto, _) in enumerate(self.opciones):
            activa = (i == self.seleccion)
            color = ajustes.MENU_RESALTE if activa else ajustes.MENU_TEXTO
            etiqueta = ('> %s <' % texto) if activa else texto
            img = self.font_opcion.render(etiqueta, True, color)
            pantalla.blit(img, (ajustes.ANCHO // 2 - img.get_width() // 2, 280 + i * 52))

        pie = self.font_pie.render('Flechas para moverse  ·  Enter para elegir',
                                   True, ajustes.GRIS)
        pantalla.blit(pie, (ajustes.ANCHO // 2 - pie.get_width() // 2, ajustes.ALTO - 46))
