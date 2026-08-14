"""
Constantes del juego. Todo lo que se ajusta, en un solo lugar.

Las rutas son relativas a la raíz del proyecto: main.py hace os.chdir hacia
allí al arrancar, así que funcionan igual desde la terminal que desde el IDE.
"""

#region Ventana
ANCHO, ALTO = 800, 600
TITULO = "Zelda Tico - La Leyenda de la Cangreja"
FPS = 60
#endregion

#region Rejilla y sprites
TILE_W, TILE_H = 64, 64
TILE_ORIG_W, TILE_ORIG_H = 100, 100   # tamaño algunos spritesheets que toca escalar
JUG_W, JUG_H = 64, 64
ARBOL_ESCALA = 1.5                    # el árbol se dibuja más grande para que sobresalga un poco del tile
ARBOL_W = int(TILE_W * ARBOL_ESCALA)
ARBOL_H = int(TILE_H * ARBOL_ESCALA)
#endregion

#region Jugador
VELOCIDAD_JUGADOR = 180               # píxeles por segundo
FRAMES_ANIM = 5                       # cuadros por spritesheet
FPS_ANIM = 6                          # cuadros por segundo al caminar
FPS_ATAQUE = 13                       # cuadros por segundo al atacar
HITBOX_ANCHO = 0.5                    # proporción del sprite (solo los pies para los npc y jugador)
HITBOX_ALTO = 0.2
#endregion

#region Depuracion
# Con esto en False no se dibujan hitboxes, no aparece la barra de info y la
# tecla G para mostrar la rejilla deja de funcionar.
MOSTRAR_DEPURACION = True
#endregion

#region Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (120, 120, 120)
COLOR_REJILLA = (220, 220, 220)
HITBOX_JUGADOR = (255, 0, 0)
HITBOX_NPC = (0, 200, 0)
HITBOX_TILE = (0, 100, 200)
MENU_FONDO = (24, 28, 22)
MENU_TEXTO = (232, 232, 216)
MENU_RESALTE = (186, 211, 98)
#endregion

#region Rutas
DIR_TERRENO = 'assets/tiles/terreno'
DIR_JUGADOR = 'assets/characters/player'
DIR_NPC = 'assets/characters/npc'
DIR_TILES = 'assets/tiles'
DIR_MUSICA = 'assets/audio/musica'
DIR_SFX = 'assets/audio/sfx'
PAQUETE_NIVELES = 'niveles'
#endregion

#region Niveles
NIVEL_INICIAL = 'pueblo'
#endregion

#region Audio
VOLUMEN_MUSICA = 0.5
VOLUMEN_SFX = 0.7
FADE_MUSICA_MS = 600
#endregion
