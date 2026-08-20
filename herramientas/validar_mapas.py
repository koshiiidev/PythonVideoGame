"""
Revisa los mapas sin abrir el juego.

    python herramientas/validar_mapas.py            revisa todos los niveles
    python herramientas/validar_mapas.py pueblo     revisa solo uno

Busca los errores tipicos de dibujar un mapa a mano: filas de distinto largo,
caracteres que no existen, NPC o salidas encima de tiles solidos, capas
desalineadas y salidas que apuntan a un nivel que no existe.

Devuelve 0 si esta todo bien y 1 si encontro algo, para poder engancharlo a un
hook de git mas adelante.
"""

import os
import sys

# Las consolas de Windows no siempre traen UTF-8 y los mensajes llevan tildes
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
sys.path.insert(0, RAIZ)

from config import settings as ajustes
from src.core import cargador_niveles as niveles


def nombres_de_niveles():
    carpeta = os.path.join(RAIZ, ajustes.PAQUETE_NIVELES)
    return sorted(f[:-3] for f in os.listdir(carpeta)
                  if f.endswith('.py') and not f.startswith('__'))


def revisar(nombre, existentes):
    try:
        nivel = niveles.cargar(nombre)
    except Exception as e:
        return ['no se pudo cargar: %s: %s' % (type(e).__name__, e)]

    fallos = nivel.problemas()

    # Esto necesita saber de los otros niveles, por eso no va dentro de Nivel
    for (col, fil), destino in nivel.salidas.items():
        if destino[0] not in existentes:
            fallos.append('SALIDA (%d,%d): apunta al nivel %r y no existe'
                          % (col, fil, destino[0]))
    return fallos


def main():
    existentes = nombres_de_niveles()
    pedidos = sys.argv[1:] or existentes

    total = 0
    for nombre in pedidos:
        fallos = revisar(nombre, existentes)
        total += len(fallos)
        if fallos:
            print('[X] %s  (%d)' % (nombre, len(fallos)))
            for f in fallos:
                print('     - %s' % f)
        else:
            nivel = niveles.cargar(nombre)
            capas = 2 if nivel.decor else 1
            print('[OK] %-10s %2dx%-2d  %d capa(s)  %d npc  %d salida(s)'
                  % (nombre, nivel.cols, nivel.filas, capas,
                     len(nivel.npcs), len(nivel.salidas)))

    print('-' * 52)
    print('%d problema(s) en %d nivel(es)' % (total, len(pedidos)))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
