"""
Calculos de cajas o hitboxes que usan varias partes del juego

Todo personaje jugador, NPC, enemigo colisiona solo con sus PIES, no con el
sprite entero
"""

import pygame

from config import settings as ajustes


def caja_pies(x, y, lado, prop_ancho=None, prop_alto=None):
    #Caja en la base de un sprite cuadrado ubicado en (x, y)
    #"prop_ancho" y "prop_alto" son proporciones del sprite. Si no se pasan, se
    #usan las del jugador que estan en settings
    prop_ancho = ajustes.HITBOX_ANCHO if prop_ancho is None else prop_ancho
    prop_alto = ajustes.HITBOX_ALTO if prop_alto is None else prop_alto

    ancho = max(1, int(lado * prop_ancho))
    alto = max(1, int(lado * prop_alto))
    return pygame.Rect(int(x) + (lado - ancho) // 2,
                       int(y) + lado - alto - 2,
                       ancho, alto)


def caja_pies_jugador(x, y):
    return caja_pies(x, y, ajustes.JUG_W)


def caja_pies_enemigo(x, y):
    return caja_pies(x, y, ajustes.ENEMIGO_LADO,
                     ajustes.ENEMIGO_HITBOX_ANCHO,
                     ajustes.ENEMIGO_HITBOX_ALTO)


def caja_delante(x, y, lado, direccion, largo, ancho):
    #Rectangulo proyectado hacia donde mira un personaje
    cx = x + lado // 2
    cy = y + lado // 2
    if direccion == 'espalda':
        return pygame.Rect(cx - ancho // 2, cy - largo, ancho, largo)
    if direccion == 'frente':
        return pygame.Rect(cx - ancho // 2, cy, ancho, largo)
    if direccion == 'izquierda':
        return pygame.Rect(cx - largo, cy - ancho // 2, largo, ancho)
    return pygame.Rect(cx, cy - ancho // 2, largo, ancho)
