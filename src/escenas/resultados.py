"""
Pantalla de resumen, al terminar la partida.

Muestra todo lo que pide el requisito 11: icono y nombre, vidas perdidas,
enemigos eliminados, tiempo, puntos, record por vida y record global. Ademas
avisa si la partida acaba de romper el record.

Enter vuelve al menu principal.
"""

import pygame

from config import settings as ajustes
from src.core import estadisticas, recursos
from src.core.gestor_escenas import Escena

FUENTES = ('consolas', 'couriernew', 'dejavusansmono', 'verdana', 'arial')


class EscenaResultados(Escena):

    def __init__(self, gestor, victoria=False):
        Escena.__init__(self, gestor)
        self.estado = gestor.estado
        self.victoria = victoria

        self.ex = ajustes.ANCHO / 800.0
        self.ey = ajustes.ALTO / 600.0
        self.font_titulo = pygame.font.SysFont(FUENTES, int(34 * self.ey), bold=True)
        self.font = pygame.font.SysFont(FUENTES, int(18 * self.ey), bold=True)
        self.font_chico = pygame.font.SysFont(FUENTES, int(15 * self.ey))

        #region Cierre de la partida
        # Se guarda el resultado y se pregunta si hubo record nuevo
        jugador = self.estado.jugador
        self.resumen = jugador.resumen() if jugador else {}
        self.record, self.record_nombre, self.es_record = self.estado.cerrar_partida()
        if not self.resumen:
            self.record, self.record_nombre = estadisticas.record_global()
        #endregion

        lado = int(64 * self.ey)
        self.retrato = recursos.imagen(
            '%s/%s' % (ajustes.DIR_RETRATOS, self.resumen.get('icono', ajustes.ICONOS_JUGADOR[0])),
            (lado, lado))

    def entrar(self):
        if self.gestor.audio:
            self.gestor.audio.musica('final.ogg' if self.victoria else 'derrota.ogg')

    #region Eventos
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,
                          pygame.K_ESCAPE):
            from src.escenas.menu import EscenaMenu
            self.gestor.cambiar(EscenaMenu(self.gestor))
    #endregion

    #region Dibujo
    def dibujar(self, pantalla):
        pantalla.fill(ajustes.MENU_FONDO)

        titulo = 'VICTORIA' if self.victoria else 'FIN DE LA PARTIDA'
        color = (186, 211, 98) if self.victoria else (226, 140, 110)
        img = self.font_titulo.render(titulo, True, color)
        pantalla.blit(img, (ajustes.ANCHO // 2 - img.get_width() // 2, int(40 * self.ey)))

        panel = pygame.Rect(int(120 * self.ex), int(100 * self.ey),
                            ajustes.ANCHO - int(240 * self.ex), int(360 * self.ey))
        pygame.draw.rect(pantalla, (40, 30, 20), panel, border_radius=10)
        pygame.draw.rect(pantalla, (128, 96, 58), panel, 2, border_radius=10)

        #region Encabezado con retrato y nombre
        x = panel.left + int(20 * self.ex)
        y = panel.top + int(18 * self.ey)
        if self.retrato:
            pantalla.blit(self.retrato, (x, y))
            x += self.retrato.get_width() + int(14 * self.ex)
        nombre = self.font_titulo.render(self.resumen.get('nombre', '-'), True, (250, 232, 180))
        pantalla.blit(nombre, (x, y + int(12 * self.ey)))
        #endregion

        #region Filas de datos
        filas = [
            ('Dificultad', self.estado.dificultad),
            ('Puntos', '%d' % self.resumen.get('puntos', 0)),
            ('Enemigos eliminados', '%d' % self.resumen.get('eliminados', 0)),
            ('Vidas perdidas', '%d' % self.resumen.get('vidas_perdidas', 0)),
            ('Mejor puntaje en una vida', '%d' % self.resumen.get('record_por_vida', 0)),
            ('Tiempo jugado', self._tiempo(self.resumen.get('tiempo', 0))),
            ('Record global', '%d  (%s)' % (self.record, self.record_nombre or '-')),
        ]
        y = panel.top + int(104 * self.ey)
        for etiqueta, valor in filas:
            img = self.font.render(etiqueta, True, (206, 188, 158))
            pantalla.blit(img, (panel.left + int(24 * self.ex), y))
            img = self.font.render(valor, True, (245, 236, 214))
            pantalla.blit(img, (panel.right - int(24 * self.ex) - img.get_width(), y))
            y += int(30 * self.ey)
        #endregion

        if self.es_record:
            img = self.font.render('¡NUEVO RECORD!', True, (255, 214, 120))
            pantalla.blit(img, (ajustes.ANCHO // 2 - img.get_width() // 2,
                                panel.bottom - int(34 * self.ey)))

        pie = self.font_chico.render('Enter para volver al menú', True, (188, 172, 146))
        pantalla.blit(pie, (ajustes.ANCHO // 2 - pie.get_width() // 2,
                            ajustes.ALTO - int(40 * self.ey)))

    @staticmethod
    def _tiempo(segundos):
        segundos = int(segundos)
        return '%d:%02d' % (segundos // 60, segundos % 60)
    #endregion
