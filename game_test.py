import pygame
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda Tico")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

#region Colores
BLANCO = (255, 255, 255)
AZUL = (0, 100, 200)
NEGRO = (0, 0, 0)
#endregion


# Tamano original del sprite
SPRITE_W, SPRITE_H = 421, 354
ESCALA = 3
DISP_W = SPRITE_W // ESCALA
DISP_H = SPRITE_H // ESCALA
TILE_SIZE = 50

# Cargar spritesheets
sheet_frente = pygame.image.load('assets/characters/player/camina_frente_spritesheet.png').convert_alpha()
sheet_espalda = pygame.image.load('assets/characters/player/camina_espalda_spritesheet.png').convert_alpha()
sheet_derecha = pygame.image.load('assets/characters/player/camina_derecha_spritesheet.png').convert_alpha()

# Extraer frames de cada spritesheet
def carga_animacion(sheet, n_frames):
    frames = []
    for i in range(n_frames):
        frame = sheet.subsurface((i * SPRITE_W, 0, SPRITE_W, SPRITE_H))
        frame = pygame.transform.smoothscale(frame, (DISP_W, DISP_H))
        frames.append(frame)
    return frames

# Voltear frames horizontalmente
def voltear(frames):
    return [pygame.transform.flip(f, True, False) for f in frames]

frames = {
    'frente': carga_animacion(sheet_frente, 5),
    'espalda': carga_animacion(sheet_espalda, 5),
    'derecha': carga_animacion(sheet_derecha, 5),
    'izquierda': voltear(carga_animacion(sheet_derecha, 5)),
}

#region Tiles

def dibujar_grid():
    for x in range(30):
        pygame.draw.line(pantalla, NEGRO, (x*60, 0), (x*60, HEIGHT))
        pygame.draw.line(pantalla, NEGRO, (0, x * 60), (WIDTH, x * 60 ))
#endregion

# Jugador
jugador = {
    'x': WIDTH // 2 - DISP_W // 2,
    'y': HEIGHT // 2 - DISP_H // 2,
    'velocidad': 200,
    'direccion': 'frente',
    'moviendose': False,
}

FPS_ANIM = 8
frame_duration = 1.0 / FPS_ANIM

# Estados de teclas
keys = {
    'up': False,
    'down': False,
    'left': False,
    'right': False,
}

running = True
frame_idx = 0
last_frame_time = time.time()

print(f"Sprites cargados: frente={len(frames['frente'])}, espalda={len(frames['espalda'])}, derecha={len(frames['derecha'])}, izquierda={len(frames['izquierda'])} (flip de derecha)")
print(f"Display: {DISP_W}x{DISP_H}")
print("Flechas o WASD para mover | ESC para cerrar")

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key in (pygame.K_UP, pygame.K_w):
                keys['up'] = True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                keys['down'] = True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                keys['left'] = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                keys['right'] = True
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_w):
                keys['up'] = False
            if event.key in (pygame.K_DOWN, pygame.K_s):
                keys['down'] = False
            if event.key in (pygame.K_LEFT, pygame.K_a):
                keys['left'] = False
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                keys['right'] = False

    # Determinar direccion y movimiento
    jugador['moviendose'] = False

    if keys['up']:
        jugador['direccion'] = 'espalda'
        jugador['y'] -= jugador['velocidad'] * dt
        jugador['moviendose'] = True
    elif keys['down']:
        jugador['direccion'] = 'frente'
        jugador['y'] += jugador['velocidad'] * dt
        jugador['moviendose'] = True
    elif keys['left']:
        jugador['direccion'] = 'izquierda'
        jugador['x'] -= jugador['velocidad'] * dt
        jugador['moviendose'] = True
    elif keys['right']:
        jugador['direccion'] = 'derecha'
        jugador['x'] += jugador['velocidad'] * dt
        jugador['moviendose'] = True

    # Mantener dentro de pantalla
    jugador['x'] = max(0, min(WIDTH - DISP_W, jugador['x']))
    jugador['y'] = max(0, min(HEIGHT - DISP_H, jugador['y']))

    # Actualizar frame de animacion
    if time.time() - last_frame_time >= frame_duration:
        if jugador['moviendose']:
            frame_idx = (frame_idx + 1) % 5
        else:
            frame_idx = 0  # frame quieto
        last_frame_time = time.time()

    # Dibujar
    pantalla.fill(BLANCO)
    dibujar_grid()

    # Sprite
    current_frames = frames[jugador['direccion']]
    pantalla.blit(current_frames[frame_idx], (jugador['x'], jugador['y']))

    # Contorno
    pygame.draw.rect(pantalla, AZUL, (jugador['x'], jugador['y'], DISP_W, DISP_H), 2)

    # Info
    estado = "MOVIENDOSE" if jugador['moviendose'] else "QUIETO"
    info = font.render(
        f"Direccion: {jugador['direccion']} | Estado: {estado} | Pos: ({jugador['x']:.0f}, {jugador['y']:.0f})",
        True, (0, 0, 0)
    )
    pantalla.blit(info, (10, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
