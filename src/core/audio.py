"""
Música y efectos de sonido.

si no hay tarjeta de sonido, si falta un archivo o si el mixer no arranca, el juego sigue corriendo igual y
solo se pierde el audio

Uso:
    audio = Audio()
    audio.musica('pueblo.ogg')       # arranca en bucle, con fundido
    audio.sfx('espada.wav')          # efecto puntual
    audio.parar_musica()
"""

import os
import pygame

from config import settings as ajustes


class Audio(object):

    def __init__(self, volumen_musica=None, volumen_sfx=None):
        self.volumen_musica = (ajustes.VOLUMEN_MUSICA if volumen_musica is None
                               else volumen_musica)
        self.volumen_sfx = (ajustes.VOLUMEN_SFX if volumen_sfx is None
                            else volumen_sfx)
        self.disponible = False
        self.pista_actual = None
        self.silenciado = False
        self._cache_sfx = {}
        self._iniciar()

    def _iniciar(self):
        try:
            pygame.mixer.init()
            self.disponible = True
        except pygame.error as e:
            #imprime pero no detiene juego
            print('[audio] sin sonido:', e)
            self.disponible = False

    #region Musica
    def musica(self, nombre, loop=True, fade_ms=None):
        #reproduce una pista de assets/audio/musica, no reinicia
        if not self.disponible or self.silenciado:
            return
        if nombre == self.pista_actual:
            return
        ruta = os.path.join(ajustes.DIR_MUSICA, nombre)
        if not os.path.exists(ruta):
            print('[audio] falta la música:', ruta)
            return
        fade = ajustes.FADE_MUSICA_MS if fade_ms is None else fade_ms
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(self.volumen_musica)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade)
            self.pista_actual = nombre
        except pygame.error as e:
            print('[audio] no se pudo reproducir', nombre, e)

    def parar_musica(self, fade_ms=None):
        if not self.disponible:
            return
        fade = ajustes.FADE_MUSICA_MS if fade_ms is None else fade_ms
        try:
            pygame.mixer.music.fadeout(fade)
        except pygame.error:
            pass
        self.pista_actual = None
    #endregion

    #region Efectos
    def sfx(self, nombre):
        #Reproduce un efecto de assets/audio/sfx
        if not self.disponible or self.silenciado:
            return
        sonido = self._cargar_sfx(nombre)
        if sonido:
            sonido.play()

    def _cargar_sfx(self, nombre):
        if nombre in self._cache_sfx:
            return self._cache_sfx[nombre]
        ruta = os.path.join(ajustes.DIR_SFX, nombre)
        sonido = None
        if os.path.exists(ruta):
            try:
                sonido = pygame.mixer.Sound(ruta)
                sonido.set_volume(self.volumen_sfx)
            except pygame.error as e:
                print('[audio] no se pudo cargar', ruta, e)
        else:
            print('[audio] falta el efecto:', ruta)
        self._cache_sfx[nombre] = sonido
        return sonido
    #endregion

    #region Volumen
    def silenciar(self, valor=None):
        #alterna el silencio o lo fija si se pasa True/False
        self.silenciado = (not self.silenciado) if valor is None else valor
        if not self.disponible:
            return
        try:
            pygame.mixer.music.set_volume(0 if self.silenciado else self.volumen_musica)
        except pygame.error:
            pass
        return self.silenciado
    #endregion
