"""
Estadisticas

Guarda el record global y el historial de partidas en un JSON, si no existe el juego sigue 
con datos de memoria, pero se pierde el historial
"""

import json
import os
from datetime import datetime

from config import settings as ajustes

_VACIO = {'record_global': 0, 'record_nombre': '', 'partidas': []}


def _ruta():
    return ajustes.ARCHIVO_ESTADISTICAS


def cargar():
    #devuelve el diccionario de estadisticas
    ruta = _ruta()
    if not os.path.exists(ruta):
        return dict(_VACIO)
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except (ValueError, OSError) as e:
        print('[estadisticas] archivo no se puede leer, se empieza de cero:', e)
        return dict(_VACIO)

    if not isinstance(datos, dict):
        print('[estadisticas] formato inesperado, se empieza de cero')
        return dict(_VACIO)

    # Rellenar lo que falte, por si el archivo es de una version anterior
    completo = dict(_VACIO)
    completo.update({k: v for k, v in datos.items() if k in _VACIO})
    if not isinstance(completo['partidas'], list):
        completo['partidas'] = []
    try:
        completo['record_global'] = int(completo['record_global'])
    except (TypeError, ValueError):
        completo['record_global'] = 0
    return completo


def guardar(datos):
    #Escribe el archivo y devuelve True
    ruta = _ruta()
    try:
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print('[estadisticas] no se pudo guardar:', e)
        return False


def record_global():
    d = cargar()
    return d['record_global'], d['record_nombre']


def registrar_partida(resumen, dificultad):
    #Guarda una partida terminada y actualiza el record global
    #resumen es lo que devuelve Jugador.resumen()
    #devuelve (record_global, nombre_del_record, es_record_nuevo)

    datos = cargar()
    puntos = int(resumen.get('puntos', 0))
    nuevo = puntos > datos['record_global']

    if nuevo:
        datos['record_global'] = puntos
        datos['record_nombre'] = resumen.get('nombre', '')

    datos['partidas'].append({
        'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'dificultad': dificultad,
        'jugador': resumen,
    })
    # limite archivo
    datos['partidas'] = datos['partidas'][-50:]

    guardar(datos)
    return datos['record_global'], datos['record_nombre'], nuevo
