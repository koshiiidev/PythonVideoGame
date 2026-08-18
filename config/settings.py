"""
constantes del juego, las rutas son relativas a la raiz
"""

#region Ventana
ANCHO, ALTO = 800, 600
TITULO = "Cholito - La leyenda del valle"
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
DIR_ICONOS = 'assets/ui/iconos'
DIR_RETRATOS = 'assets/ui/retratos'
DIR_MUSICA = 'assets/audio/musica'
DIR_SFX = 'assets/audio/sfx'
PAQUETE_NIVELES = 'niveles'
#endregion

#region Partida
DIFICULTADES = {
    'Principiante': {'enemigos': 3, 'velocidad': 60,  'dano': 1, 'multiplicador': 1.0},
    'Normal':       {'enemigos': 5, 'velocidad': 85,  'dano': 1, 'multiplicador': 1.5},
    'Leyenda':      {'enemigos': 8, 'velocidad': 115, 'dano': 1, 'multiplicador': 2.5},
}
DIFICULTAD_POR_DEFECTO = 'Normal'

VIDAS_OPCIONES = (1, 3, 5)
VIDAS_POR_DEFECTO = 3

# Iconos que puede elegir cada jugador
# Retratos de Cholito. Es siempre el mismo personaje: solo cambia el color del
# panuelo, para distinguir jugadores en el marcador
ICONOS_JUGADOR = ('cholito_rojo.png', 'cholito_azul.png', 'cholito_verde.png',
                  'cholito_amarillo.png', 'cholito_morado.png', 'cholito_blanco.png')

LARGO_MAX_NOMBRE = 12
NOMBRE_POR_DEFECTO = 'Cholito'

# Puntos
PUNTOS_POR_ENEMIGO = 100
ENEMIGOS_PARA_BONO = 10
PUNTOS_BONO = 500
VELOCIDAD_POR_BONO = 12       # los enemigos se aceleran con cada bono
#endregion

#region Combate y enemigos
ENEMIGO_LADO = 48
CUADROS_ENEMIGO = 4
FPS_ENEMIGO = 6
ENEMIGO_HITBOX_ANCHO = 0.55   # proporciones de su caja de pies
ENEMIGO_HITBOX_ALTO = 0.35
DIR_ENEMIGOS = 'assets/characters/enemigos'

DISTANCIA_VISION = 220        # a que distancia el enemigo empieza a perseguir
DISTANCIA_APARICION = 260     # no aparecen mas cerca que esto del jugador
ALCANCE_ATAQUE = 52           # largo del machetazo en pixeles
ANCHO_ATAQUE = 46             # ancho del machetazo
INVULNERABLE_S = 1.2          # tiempo sin recibir dano tras un golpe
PARPADEO_HZ = 8               # velocidad del parpadeo mientras es invulnerable
#endregion

#region Archivos
ARCHIVO_ESTADISTICAS = 'datos/estadisticas.json'
#endregion

#region Niveles
NIVEL_INICIAL = 'pueblo'
#endregion

#region Audio
VOLUMEN_MUSICA = 0.5
VOLUMEN_SFX = 0.7
FADE_MUSICA_MS = 600
#endregion
