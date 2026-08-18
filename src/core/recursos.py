"""
Caché de imágenes.

se guarda cada imagen ya cargada y escalada, y la segunda vez que se pide
se devuelve lo que ya se tiene aqui
"""

import os
import pygame

_cache = {}


def imagen(ruta, tam=None):
    #Devuelve la imagen ya convertida y si se pide escalada
    #"tam" es una tupla (ancho, alto) si el archivo no existe devuelve None
    #para que no se caiga el juego
    
    clave = (ruta, tam)
    if clave in _cache:
        return _cache[clave]

    if not os.path.exists(ruta):
        print('[assets] no se encontró:', ruta)
        _cache[clave] = None
        return None

    img = pygame.image.load(ruta).convert_alpha()
    if tam and img.get_size() != tuple(tam):
        img = pygame.transform.scale(img, tam)
    _cache[clave] = img
    return img


def spritesheet(ruta, n_frames, tam_frame, ancho_original):
    #Corta un spritesheet horizontal en una lista de cuadros
    #ancho_original es el ancho en el archivo (100px) se escala a tam_frame antes de cortar
    
    clave = ('sheet', ruta, n_frames, tam_frame)
    if clave in _cache:
        return _cache[clave]

    if not os.path.exists(ruta):
        print('[assets] no se encontró el spritesheet:', ruta)
        _cache[clave] = []
        return []

    hoja = pygame.image.load(ruta).convert_alpha()
    total = hoja.get_width() // ancho_original
    hoja = pygame.transform.scale(hoja, (total * tam_frame[0], tam_frame[1]))
    cuadros = [hoja.subsurface((i * tam_frame[0], 0, tam_frame[0], tam_frame[1]))
               for i in range(min(n_frames, total))]
    _cache[clave] = cuadros
    return cuadros


def limpiar():
    _cache.clear()
