"""
Arranque del juego.

"""

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

import pygame

from config import settings as ajustes
from src.core.audio import Audio
from src.core.estado import EstadoJuego
from src.core.gestor_escenas import GestorEscenas


def crear_gestor():
    """Prepara, sin escenas todavia"""
    pygame.init()
    pantalla = pygame.display.set_mode((ajustes.ANCHO, ajustes.ALTO))
    pygame.display.set_caption(ajustes.TITULO)
    return GestorEscenas(pantalla, EstadoJuego(), Audio())


def bucle(gestor):
    reloj = pygame.time.Clock()
    while gestor.corriendo:
        dt = reloj.tick(ajustes.FPS) / 1000.0
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                gestor.terminar()
            else:
                gestor.manejar_evento(evento)
        if not gestor.corriendo:
            break
        gestor.actualizar(dt)
        gestor.dibujar()
        pygame.display.flip()
    pygame.quit()


def main():
    from src.escenas.cinematica import EscenaCinematica, INTRO
    from src.escenas.menu import EscenaMenu

    gestor = crear_gestor()

    # La intro arranca primero y, al terminar, deja el menú en su lugar
    def ir_al_menu():
        gestor.cambiar(EscenaMenu(gestor))

    gestor.cambiar(EscenaCinematica(gestor, INTRO, al_terminar=ir_al_menu))
    bucle(gestor)


if __name__ == '__main__':
    main()
