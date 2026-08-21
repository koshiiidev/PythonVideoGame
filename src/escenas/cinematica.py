"""
Se pasa sola cuando se acaba el tiempo o a mano con Enter/Espacio. Escape saltea toda la cinemática

"""

import pygame

from config import settings as ajustes
from src.core import recursos
from src.core.gestor_escenas import Escena


#region Guiones
# texto: lo que se muestra. Se parte en varias líneas con \n
# duracion: segundos en pantalla, contando los fundidos
# imagen: ruta opcional a un PNG de fondo
# La intro planta el problema, no lo resuelve: el final se guarda para FINAL
INTRO = [
    {'texto': 'Hace muchos años, un pueblo vivía en armonía\n'
              'entre cafetales, montañas y tradiciones.', 'duracion': 5.0},
    {'texto': 'Una noche, la niebla bajó de la montaña,\n'
              'y con ella llegó la oscuridad.', 'duracion': 5.0},
    {'texto': 'Los cafetales se marchitaron.\n'
              'Los caminos se perdieron.\n'
              'Nadie volvió a ver el sol.', 'duracion': 5.0},
    {'texto': 'Solo uno se atrevió a subir a buscar la luz:\n'
              'Cholito, un joven campesino del valle.', 'duracion': 5.0},
]

# Se muestra al sellar a la bruja. Cierra con el mensaje del juego.
FINAL = [
    {'texto': 'La bruja no fue destruida.\n'
              'Primero fue escuchada. Después, sellada.', 'duracion': 5.0},
    {'texto': 'En la montaña que hoy llaman La Cangreja\n'
              'duerme su rencor, y ya no baja al valle.', 'duracion': 5.0},
    {'texto': 'La niebla se abrió.\n'
              'El café volvió a florecer.', 'duracion': 4.5},
    {'texto': '"El valor no siempre es destruir al mal,\n'
              'sino hacer lo necesario para que nunca más regrese."', 'duracion': 6.0},
]

CREDITOS = [
    {'texto': 'CHOLITO\nLa Leyenda de la Cangreja', 'duracion': 4.5},
    {'texto': 'Inspirado en leyendas costarricenses:\n'
              'La Segua, El Cadejos y el cerro La Cangreja.', 'duracion': 5.0},
    {'texto': 'Proyecto final\nDesarrollo de Aplicaciones de Ult. Gen.\nUAM', 'duracion': 4.5},
    {'texto': 'Gracias por jugar.', 'duracion': 3.5},
]
#endregion


class EscenaCinematica(Escena):

    def __init__(self, gestor, guion, al_terminar=None):
       #"al_terminar" simplemente se desapila y vuelve a la que esta debajo
        Escena.__init__(self, gestor)
        self.guion = guion
        self.al_terminar = al_terminar
        self.font = pygame.font.SysFont(None, 32)
        self.font_pie = pygame.font.SysFont(None, 18)
        self.indice = 0
        self.t = 0.0
        self.duracion_fundido = 0.8

    def entrar(self):
        if self.gestor.audio:
            self.gestor.audio.musica('intro.wav')

    #region Control
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_ESCAPE:
            self.terminar()
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.siguiente()

    def siguiente(self):
        self.indice += 1
        self.t = 0.0
        if self.indice >= len(self.guion):
            self.terminar()

    def terminar(self):
        if self.al_terminar:
            self.al_terminar()
        else:
            self.gestor.desapilar()

    def actualizar(self, dt):
        if self.indice >= len(self.guion):
            return
        self.t += dt
        if self.t >= self.guion[self.indice].get('duracion', 4.0):
            self.siguiente()
    #endregion

    #region Dibujo
    def _alpha(self, placa):
        dur = placa.get('duracion', 4.0)
        f = self.duracion_fundido
        if self.t < f:
            return int(255 * (self.t / f))
        if self.t > dur - f:
            return int(255 * max(0.0, (dur - self.t) / f))
        return 255

    def dibujar(self, pantalla):
        pantalla.fill(ajustes.NEGRO)
        if self.indice >= len(self.guion):
            return

        placa = self.guion[self.indice]
        alpha = self._alpha(placa)

        if placa.get('imagen'):
            img = recursos.imagen(placa['imagen'], (ajustes.ANCHO, ajustes.ALTO))
            if img:
                img = img.copy()
                img.set_alpha(alpha)
                pantalla.blit(img, (0, 0))

        lineas = placa.get('texto', '').split('\n')
        alto_total = len(lineas) * 40
        y = ajustes.ALTO // 2 - alto_total // 2
        for linea in lineas:
            img = self.font.render(linea, True, ajustes.MENU_TEXTO)
            img.set_alpha(alpha)
            pantalla.blit(img, (ajustes.ANCHO // 2 - img.get_width() // 2, y))
            y += 40

        pie = self.font_pie.render('Enter para seguir  ·  Esc para saltar',
                                   True, ajustes.GRIS)
        pantalla.blit(pie, (ajustes.ANCHO // 2 - pie.get_width() // 2, ajustes.ALTO - 40))
    #endregion
