"""
Para probar cosas

Va directo a la partida, sin intro ni menú, para probar el mapa rápido
NO tiene lógica propia: usa exactamente las mismas clases que main.py

    python game_test.py            arranca en el nivel inicial
    python game_test.py casa       arranca en el nivel que se le ponga
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from config import settings as ajustes
from main import bucle, crear_gestor


def main():
    from src.escenas.juego import EscenaJuego

    gestor = crear_gestor()

    # Nivel por línea de comandos, si se pasó uno
    if len(sys.argv) > 1:
        gestor.estado.nivel_actual = sys.argv[1]

    gestor.cambiar(EscenaJuego(gestor))
    print('[prueba] nivel: %s | tile %dx%d | depuración: %s'
          % (gestor.estado.nivel_actual, ajustes.TILE_W, ajustes.TILE_H,
             'ON' if ajustes.MOSTRAR_DEPURACION else 'OFF'))
    bucle(gestor)


if __name__ == '__main__':
    main()
