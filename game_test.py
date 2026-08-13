import pygame
import time
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda Tico")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

#region Colores
BLANCO = (255, 255, 255)
AZUL = (0, 100, 200)
VERDE = (0, 200, 0)
GRID_COLOR = (180, 180, 180)

TILE_W, TILE_H = 100, 100

# ==========================================
# JUGADOR - spritesheet 100x100 por frame
# ==========================================
JUG_W, JUG_H = 100, 100

sheet_frente = pygame.image.load('assets/characters/player/J1_F_sp.png').convert_alpha()
sheet_espalda = pygame.image.load('assets/characters/player/J1_E_sp.png').convert_alpha()
sheet_derecha = pygame.image.load('assets/characters/player/J1_D_sp.png').convert_alpha()
sheet_izquierda = pygame.image.load('assets/characters/player/J1_I_sp.png').convert_alpha()
sheet_ataque_frente = pygame.image.load('assets/characters/player/J1_F_ataque_sp.png').convert_alpha()

ataque_frames = [sheet_ataque_frente.subsurface((i * JUG_W, 0, JUG_W, JUG_H)) for i in range(5)]

def carga_frames(sheet, n):
    return [sheet.subsurface((i * JUG_W, 0, JUG_W, JUG_H)) for i in range(n)]

jugador_frames = {
    'frente': carga_frames(sheet_frente, 5),
    'espalda': carga_frames(sheet_espalda, 5),
    'derecha': carga_frames(sheet_derecha, 5),
    'izquierda': carga_frames(sheet_izquierda, 5),
}

# Jugador
jugador = {
    'x': WIDTH // 2 - JUG_W // 2,
    'y': HEIGHT // 2 - JUG_H // 2,
    'velocidad': 180,
    'direccion': 'frente',
    'moviendose': False,
    'atacando': False,
}

# ==========================================
# NPCs - imagenes estaticas 100x100
# ==========================================
npc_sprites = []
for f in sorted(os.listdir('assets/characters/npc/')):
    npc_sprites.append(pygame.image.load('assets/characters/npc/' + f).convert_alpha())

# ==========================================
# GRILLA
# ==========================================
def dibujar_grid():
    for x in range(0, WIDTH, TILE_W):
        pygame.draw.line(pantalla, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, TILE_H):
        pygame.draw.line(pantalla, GRID_COLOR, (0, y), (WIDTH, y), 1)

# ==========================================
# LOOP
# ==========================================
FPS_ANIM = 6
frame_duration = 1.0 / FPS_ANIM
FPS_ATAQUE = 13
ataque_duration = 1.0 / FPS_ATAQUE
keys = {'up': False, 'down': False, 'left': False, 'right': False}

running = True
jugador_frame_idx = 0
last_frame_time = time.time()
ataque_frame_idx = 0
ataque_done = True
last_ataque_time = time.time()

print(f'TILE: {TILE_W}x{TILE_H} | Grid: {WIDTH//TILE_W}x{HEIGHT//TILE_H} | NPCs: {len(npc_sprites)}')

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key in (pygame.K_UP, pygame.K_w): keys['up'] = True
            if event.key in (pygame.K_DOWN, pygame.K_s): keys['down'] = True
            if event.key in (pygame.K_LEFT, pygame.K_a): keys['left'] = True
            if event.key in (pygame.K_RIGHT, pygame.K_d): keys['right'] = True
            if event.key == pygame.K_SPACE and ataque_done:
                ataque_frame_idx = 0
                ataque_done = False
                last_ataque_time = time.time()
                jugador['atacando'] = True
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_w): keys['up'] = False
            if event.key in (pygame.K_DOWN, pygame.K_s): keys['down'] = False
            if event.key in (pygame.K_LEFT, pygame.K_a): keys['left'] = False
            if event.key in (pygame.K_RIGHT, pygame.K_d): keys['right'] = False
            #if event.key == pygame.K_SPACE:
                #jugador['atacando'] = False

    # Movimiento
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

    # Limites
    jugador['x'] = max(0, min(WIDTH - JUG_W, jugador['x']))
    jugador['y'] = max(0, min(HEIGHT - JUG_H, jugador['y']))

    # Frame de animacion
    if time.time() - last_frame_time >= frame_duration:
        if jugador['moviendose']:
            jugador_frame_idx = (jugador_frame_idx + 1) % 5
        else:
            jugador_frame_idx = 0
        last_frame_time = time.time()

    # Animacion de ataque
    if not ataque_done and time.time() - last_ataque_time >= ataque_duration:
        ataque_frame_idx += 1
        if ataque_frame_idx >= 5:
            ataque_frame_idx = 0
            ataque_done = True
            jugador['atacando'] = False
        last_ataque_time = time.time()

    # Dibujar
    pantalla.fill(BLANCO)
    dibujar_grid()

    # NPCs estaticos
    npc_y = 5
    npc_spacing = JUG_W + 10
    for i, npc in enumerate(npc_sprites):
        npc_x = 5 + i * npc_spacing
        pantalla.blit(npc, (npc_x, npc_y))
        pygame.draw.rect(pantalla, VERDE, (npc_x, npc_y, JUG_W, JUG_H), 2)

    # Jugador
    if jugador['atacando']:
        pantalla.blit(ataque_frames[ataque_frame_idx], (jugador['x'], jugador['y']))
    else:
        pantalla.blit(jugador_frames[jugador['direccion']][jugador_frame_idx], (jugador['x'], jugador['y']))
    pygame.draw.rect(pantalla, AZUL, (jugador['x'], jugador['y'], JUG_W, JUG_H), 3)

    # Info
    estado = "ATACANDO" if jugador['atacando'] else ("MOVIENDOSE" if jugador['moviendose'] else "QUIETO")
    info = font.render(
        f"Direccion: {jugador['direccion']} | {estado} | Tile: {TILE_W}x{TILE_H} | NPCs: {len(npc_sprites)} | ESPACIO=atacar",
        True, (0, 0, 0)
    )
    pygame.draw.rect(pantalla, BLANCO, (0, HEIGHT - 22, WIDTH, 22))
    pantalla.blit(info, (5, HEIGHT - 18))

    pygame.display.flip()

pygame.quit()
