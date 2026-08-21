"""
Menu principal

Flechas o W/S para moverse, izquierda y derecha para cambiar valores y
Enter o Espacio para elegir
"""

import math
import pygame
from config import settings as ajustes
from src.core.gestor_escenas import Escena


#region medidas
#sobre 800x600
CENTRO_X = 208            # el poste del cartel
PRIMERA_Y = 200           # centro de la primera placa
SEPARACION = 50
PLACA_W, PLACA_H = 268, 46
SEPARACION_FLECHA = 10
#endregion

#se prueban en orden, la primera que exista es la que se usa
FUENTES = ('consolas', 'couriernew', 'dejavusansmono', 'verdana', 'arial')


class EscenaMenu(Escena):

    def __init__(self, gestor):
        Escena.__init__(self, gestor)
        self.estado = gestor.estado

        #region Escala
        #asociado a resolucion 800x600 y 4:3 pos si se escala la ventana
        self.ex = ajustes.ANCHO / 800.0
        self.ey = ajustes.ALTO / 600.0
        #endregion

        #region Imagenes
        fondo = pygame.image.load('assets/ui/menu_fondo_v2.png').convert()
        self.fondo = pygame.transform.smoothscale(fondo, (ajustes.ANCHO, ajustes.ALTO))

        placa = pygame.image.load('assets/ui/tabla_menu.png').convert_alpha()
        self.placa = pygame.transform.smoothscale(
            placa, (int(PLACA_W * self.ex), int(PLACA_H * self.ey)))

        flecha = pygame.image.load('assets/ui/menu_flecha.png').convert_alpha()
        alto_flecha = int(PLACA_H * 0.80 * self.ey)
        ancho_flecha = int(alto_flecha * flecha.get_width() / float(flecha.get_height()))
        self.flecha = pygame.transform.smoothscale(flecha, (ancho_flecha, alto_flecha))
        #endregion

        #region Fuentes
        self.font = pygame.font.SysFont(FUENTES, int(20 * self.ey), bold=True)
        # El valor va en cuerpo menor, si no choca con la etiqueta
        self.font_valor = pygame.font.SysFont(FUENTES, int(16 * self.ey), bold=True)
        self.font_pie = pygame.font.SysFont(FUENTES, int(15 * self.ey))
        #endregion

        #region Opciones
        #valor cambia con las flechas izquierda y derecha
        self.opciones = [
            ('JUGAR',      self.jugar,     None),
            ('JUGADOR',    self.editar_jugador, self.valor_jugador),
            ('DIFICULTAD', None,           self.valor_dificultad),
            ('VIDAS',      None,           self.valor_vidas),
            ('HISTORIA',   self.historia,  None),
            ('CREDITOS',   self.creditos,  None),
            ('SALIR',      self.gestor.terminar, None),
        ]
        self.seleccion = 0
        self.t = 0.0
        self.aviso = ''
        self.t_aviso = 0.0
        #endregion

    def entrar(self):
        if self.gestor.audio:
            self.gestor.audio.musica('menu.wav')

    #region Valores que se muestran a la derecha
    def valor_dificultad(self):
        return self.estado.dificultad

    def valor_vidas(self):
        return str(self.estado.vidas)

    def valor_jugador(self):
        return self.estado.nombre
    #endregion

    #region Acciones
    def jugar(self):
        from src.escenas.juego import EscenaJuego
        try:
            # Crea el jugador con el nombre, icono, vidas y dificultad elegidos
            self.estado.iniciar_partida()
        except ValueError as e:
            self.mostrar_aviso(str(e))
            return
        self.gestor.cambiar(EscenaJuego(self.gestor))

    def editar_jugador(self):
        from src.escenas.seleccion_jugador import EscenaJugador
        self.gestor.apilar(EscenaJugador(self.gestor))

    def historia(self):
        from src.escenas.cinematica import EscenaCinematica, INTRO
        self.gestor.apilar(EscenaCinematica(self.gestor, INTRO))

    def creditos(self):
        from src.escenas.cinematica import EscenaCinematica, CREDITOS
        self.gestor.apilar(EscenaCinematica(self.gestor, CREDITOS))

    def mostrar_aviso(self, texto):
        self.aviso = texto
        self.t_aviso = 3.0
    #endregion

    #region Navegacion
    def mover(self, paso):
        self.seleccion = (self.seleccion + paso) % len(self.opciones)
        self._sonar('menu_mover.wav')

    def cambiar_valor(self, paso):
        #cambia valor segun dificultad o vidas
        etiqueta = self.opciones[self.seleccion][0]
        try:
            if etiqueta == 'DIFICULTAD':
                nombres = list(ajustes.DIFICULTADES)
                i = nombres.index(self.estado.dificultad)
                self.estado.set_dificultad(nombres[(i + paso) % len(nombres)])
            elif etiqueta == 'VIDAS':
                opciones = list(ajustes.VIDAS_OPCIONES)
                i = opciones.index(self.estado.vidas)
                self.estado.set_vidas(opciones[(i + paso) % len(opciones)])
            else:
                return
        except ValueError as e:
            self.mostrar_aviso(str(e))
            return
        self._sonar('menu_mover.wav')

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.mover(-1)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.mover(1)
        elif evento.key in (pygame.K_LEFT, pygame.K_a):
            self.cambiar_valor(-1)
        elif evento.key in (pygame.K_RIGHT, pygame.K_d):
            self.cambiar_valor(1)
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            accion = self.opciones[self.seleccion][1]
            if accion:
                self._sonar('menu_ok.wav')
                accion()
            else:
                self.cambiar_valor(1)
        elif evento.key == pygame.K_ESCAPE:
            self.gestor.terminar()

    def _sonar(self, nombre):
        if self.gestor.audio:
            self.gestor.audio.sfx(nombre)

    def actualizar(self, dt):
        self.t += dt
        if self.t_aviso > 0:
            self.t_aviso = max(0.0, self.t_aviso - dt)
    #endregion

    #region Dibujo
    def rect_placa(self, indice):
        ancho = self.placa.get_width()
        alto = self.placa.get_height()
        cx = int(CENTRO_X * self.ex)
        cy = int((PRIMERA_Y + indice * SEPARACION) * self.ey)
        return pygame.Rect(cx - ancho // 2, cy - alto // 2, ancho, alto)

    def _texto(self, pantalla, texto, x, y, color, centrado=False, fuente=None):
        #con contorno
        fuente = fuente or self.font
        img = fuente.render(texto, True, color)
        pos_x = x - img.get_width() // 2 if centrado else x
        pos_y = y - img.get_height() // 2
        sombra = fuente.render(texto, True, (40, 22, 12))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            pantalla.blit(sombra, (pos_x + dx, pos_y + dy))
        pantalla.blit(img, (pos_x, pos_y))
        return img.get_width()

    def dibujar(self, pantalla):
        pantalla.blit(self.fondo, (0, 0))

        for i, (etiqueta, _, valor) in enumerate(self.opciones):
            rect = self.rect_placa(i)
            pantalla.blit(self.placa, rect.topleft)

            activa = (i == self.seleccion)
            if activa:
                # en modo sumar para que se una y se vea como brillo
                brillo = pygame.Surface(rect.size, pygame.SRCALPHA)
                brillo.fill((60, 42, 10, 0))
                pantalla.blit(brillo, rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

            color = (255, 244, 214) if activa else (226, 210, 180)
            if valor:
                # Etiqueta a la izquierda y valor a la derecha
                margen = int(13 * self.ex)
                texto_valor = valor()
                self._texto(pantalla, etiqueta, rect.left + margen, rect.centery, color)
                img = self.font_valor.render(texto_valor, True, color)
                self._texto(pantalla, texto_valor,
                            rect.right - margen - img.get_width(), rect.centery,
                            (255, 232, 170) if activa else (214, 194, 156),
                            fuente=self.font_valor)
            else:
                self._texto(pantalla, etiqueta, rect.centerx, rect.centery, color, True)

        self._dibujar_flecha(pantalla)
        self._dibujar_pie(pantalla)

    def _dibujar_flecha(self, pantalla):
        rect = self.rect_placa(self.seleccion)
        vaiven = int(round(math.sin(self.t * 5.0) * 3 * self.ex))
        x = rect.left - int(SEPARACION_FLECHA * self.ex) - self.flecha.get_width() + vaiven
        pantalla.blit(self.flecha, (x, rect.centery - self.flecha.get_height() // 2))

    def _dibujar_pie(self, pantalla):
        if self.t_aviso > 0 and self.aviso:
            texto, color = self.aviso, (255, 170, 150)
        else:
            texto = 'Flechas: moverse  ·  Izq/Der: cambiar valor  ·  Enter: elegir'
            color = (236, 226, 206)
        img = self.font_pie.render(texto, True, color)
        x = ajustes.ANCHO // 2 - img.get_width() // 2
        y = ajustes.ALTO - int(30 * self.ey)
        velo = pygame.Surface((img.get_width() + 20, img.get_height() + 8), pygame.SRCALPHA)
        velo.fill((20, 12, 8, 150))
        pantalla.blit(velo, (x - 10, y - 4))
        pantalla.blit(img, (x, y))
    #endregion
