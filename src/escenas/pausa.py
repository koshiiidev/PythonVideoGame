"""
Pausa
Se APILA sobre la partida en vez de reemplazarla
Esc o P para cerrarla, flechas para moverse, Enter para elegir.
"""

import pygame

from config import settings as ajustes
from src.core.gestor_escenas import Escena

FUENTES = ('consolas', 'couriernew', 'dejavusansmono', 'verdana', 'arial')


class EscenaPausa(Escena):

    def __init__(self, gestor, escena_juego):
        Escena.__init__(self, gestor)
        self.transparente = True          # la partida se sigue viendo detras
        self.juego = escena_juego
        self.estado = gestor.estado

        self.ex = ajustes.ANCHO / 800.0
        self.ey = ajustes.ALTO / 600.0
        self.font_titulo = pygame.font.SysFont(FUENTES, int(30 * self.ey), bold=True)
        self.font = pygame.font.SysFont(FUENTES, int(20 * self.ey), bold=True)
        self.font_chico = pygame.font.SysFont(FUENTES, int(14 * self.ey))

        self.opciones = [
            ('CONTINUAR', self.continuar),
            ('REINICIAR NIVEL', self.reiniciar_nivel),
            ('VOLVER AL MENU', self.volver_al_menu),
        ]
        self.seleccion = 0

    def entrar(self):
        # Bajar la musica mientras esta pausado
        if self.gestor.audio and self.gestor.audio.disponible:
            try:
                pygame.mixer.music.set_volume(self.gestor.audio.volumen_musica * 0.35)
            except pygame.error:
                pass

    def salir(self):
        if self.gestor.audio and self.gestor.audio.disponible:
            try:
                pygame.mixer.music.set_volume(self.gestor.audio.volumen_musica)
            except pygame.error:
                pass

    #region Acciones
    def continuar(self):
        self.gestor.desapilar()

    def reiniciar_nivel(self):
        #Vuelve a poblar el nivel y devuelve al jugador a su punto de entrada
        self.juego.cargar_nivel(self.estado.nivel_actual)
        self.gestor.desapilar()

    def volver_al_menu(self):
        from src.escenas.menu import EscenaMenu
        # La partida en curso se descarta se sale sin guardar el puntaje
        self.estado.reiniciar()
        self.gestor.cambiar(EscenaMenu(self.gestor))
    #endregion

    #region Eventos
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in (pygame.K_ESCAPE, pygame.K_p):
            self.continuar()
        elif evento.key in (pygame.K_UP, pygame.K_w):
            self.seleccion = (self.seleccion - 1) % len(self.opciones)
            self._sonar('menu_mover.wav')
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.seleccion = (self.seleccion + 1) % len(self.opciones)
            self._sonar('menu_mover.wav')
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self._sonar('menu_ok.wav')
            self.opciones[self.seleccion][1]()

    def _sonar(self, nombre):
        if self.gestor.audio:
            self.gestor.audio.sfx(nombre)
    #endregion

    #region Dibujo
    def dibujar(self, pantalla):
        velo = pygame.Surface((ajustes.ANCHO, ajustes.ALTO), pygame.SRCALPHA)
        velo.fill((8, 6, 4, 175))
        pantalla.blit(velo, (0, 0))

        ancho = int(340 * self.ex)
        alto = int(260 * self.ey)
        panel = pygame.Rect(ajustes.ANCHO // 2 - ancho // 2,
                            ajustes.ALTO // 2 - alto // 2, ancho, alto)
        pygame.draw.rect(pantalla, (46, 32, 20), panel, border_radius=int(10 * self.ey))
        pygame.draw.rect(pantalla, (150, 112, 66), panel, 3, border_radius=int(10 * self.ey))

        img = self.font_titulo.render('PAUSA', True, (250, 226, 150))
        pantalla.blit(img, (panel.centerx - img.get_width() // 2,
                            panel.top + int(22 * self.ey)))

        y = panel.top + int(86 * self.ey)
        for i, (texto, _) in enumerate(self.opciones):
            activa = (i == self.seleccion)
            color = (255, 244, 214) if activa else (198, 180, 152)
            etiqueta = ('> %s <' % texto) if activa else texto
            img = self.font.render(etiqueta, True, color)
            pantalla.blit(img, (panel.centerx - img.get_width() // 2, y))
            y += int(40 * self.ey)

        jugador = self.estado.jugador
        if jugador:
            marcador = 'Puntos %d   ·   Vidas %d' % (jugador.puntos, jugador.vidas)
            img = self.font_chico.render(marcador, True, (188, 172, 146))
            pantalla.blit(img, (panel.centerx - img.get_width() // 2,
                                panel.bottom - int(30 * self.ey)))
    #endregion
