"""
El juego en si

Se carga el nivel por nombre y se puede cambiar la escena en caliente
"""

import pygame

from config import settings as ajustes
from src.core import assets_manager as assets
from src.core import niveles
from src.core.autotile import Terreno
from src.core.scene_manager import Escena


class EscenaJuego(Escena):

    def __init__(self, gestor):
        Escena.__init__(self, gestor)
        self.estado = gestor.estado
        self.audio = gestor.audio

        self.font = pygame.font.SysFont(None, 24)
        self.font_rejilla = pygame.font.SysFont(None, 16)
        self._cache_rejilla = {}

        #region Assets
        self.terreno = Terreno(ajustes.DIR_TERRENO, escala=ajustes.TILE_W)
        self.jugador_frames = self._cargar_animaciones('%s_sp.png')
        self.ataque_frames = self._cargar_animaciones('%s_ataque_sp.png')
        #endregion

        #region Estado de la partida
        self.nivel = None
        self.objeto_images = {}
        self.npcs = []
        self.jugador = {
            'x': 0, 'y': 0,
            'velocidad': ajustes.VELOCIDAD_JUGADOR,
            'direccion': 'frente',
            'moviendose': False,
            'atacando': False,
        }
        self.camera = {'x': 0, 'y': 0}
        self.teclas = {'up': False, 'down': False, 'left': False, 'right': False}

        self.frame_idx = 0
        self.t_frame = 0.0
        self.ataque_idx = 0
        self.t_ataque = 0.0
        self.ataque_listo = True

        # tile en que esta el jugador para que no se ejecute varias veces la el cambio de mapa por los frames
        self.tile_previo = None
        #endregion

    #region Carga
    def _cargar_animaciones(self, patron):
        codigos = {'frente': 'J1_F', 'espalda': 'J1_E',
                   'derecha': 'J1_D', 'izquierda': 'J1_I'}
        frames = {}
        for nombre, codigo in codigos.items():
            ruta = '%s/%s' % (ajustes.DIR_JUGADOR, patron % codigo)
            frames[nombre] = assets.spritesheet(
                ruta, ajustes.FRAMES_ANIM,
                (ajustes.JUG_W, ajustes.JUG_H), ajustes.TILE_ORIG_W)
        return frames

    def entrar(self):
        self.cargar_nivel(self.estado.nivel_actual, self.estado.entrada)

    def cargar_nivel(self, nombre, entrada=None):
        #carga o cambia de mapa, entrada es (columna, fila) en tiles o None
        self.nivel = niveles.cargar(nombre)
        self.estado.nivel_actual = nombre

        # Sprites de objetos: dependen del nivel, porque cada uno usa caracteres diferentes
        self.objeto_images = {}
        for caracter, ruta in self.nivel.objetos.items():
            tam = ((ajustes.ARBOL_W, ajustes.ARBOL_H) if caracter == 'A' # si es un arbol usa el tamaño del arbol
                   else (ajustes.TILE_W, ajustes.TILE_H)) # si no usa el tamaño del tile
            img = assets.imagen(ruta, tam) # carga la imagen
            if img: # si la imagen se cargo correctamente
                self.objeto_images[caracter] = img # se agrega al diccionario de objetos

        # NPCs: las posiciones vienen en tiles y aqui se pasan a pixeles
        self.npcs = []
        for datos in self.nivel.npcs: # por cada npc en el nivel
            img = assets.imagen('%s/%s' % (ajustes.DIR_NPC, datos['sprite']),
                                (ajustes.JUG_W, ajustes.JUG_H)) # carga la imagen
            if not img: 
                continue # si la imagen no se cargo correctamente se salta el npc
            self.npcs.append({
                'sprite': img,
                'x': datos['x'] * ajustes.TILE_W,
                'y': datos['y'] * ajustes.TILE_H,
                'solido': datos.get('solido', True), # los npcs son solidos por defecto
            })

        self._ubicar_jugador(entrada)
        self._cache_rejilla.clear()

        if self.audio and self.nivel.musica:
            self.audio.musica(self.nivel.musica)

    def _ubicar_jugador(self, entrada):
        destino = entrada or self.nivel.inicio
        if destino: # si hay una entrada definida
            self.jugador['x'] = destino[0] * ajustes.TILE_W 
            self.jugador['y'] = destino[1] * ajustes.TILE_H 
        else: # si no hay una entrada definida se posiciona en el centro del mapa
            self.jugador['x'] = self.ancho_mapa // 2 - ajustes.JUG_W // 2 
            self.jugador['y'] = self.alto_mapa // 2 - ajustes.JUG_H // 2
        self.estado.entrada = None
        self.tile_previo = self.tile_del_jugador()
        self.actualizar_camara()
    #endregion

    #region Medidas
    @property
    def ancho_mapa(self):
        return self.nivel.ancho_px(ajustes.TILE_W)

    @property
    def alto_mapa(self):
        return self.nivel.alto_px(ajustes.TILE_H)

    def tile_del_jugador(self):
        #Tile donde están los pies del jugador
        return (int((self.jugador['x'] + ajustes.JUG_W // 2) // ajustes.TILE_W),
                int((self.jugador['y'] + ajustes.JUG_H - 4) // ajustes.TILE_H))
    #endregion

    #region Hitbox y colision
    def hitbox_pies(self, pos_x, pos_y):
        #solo los pies para que el personaje se vea frente a los objetos
        ancho = int(ajustes.JUG_W * ajustes.HITBOX_ANCHO) 
        alto = int(ajustes.JUG_H * ajustes.HITBOX_ALTO)
        off_x = (ajustes.JUG_W - ancho) // 2
        off_y = ajustes.JUG_H - alto - 2
        return pygame.Rect(pos_x + off_x, pos_y + off_y, ancho, alto)

    def hitbox_tile(self, caracter, col, fil):
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        base = pygame.Rect(col * tw, fil * th, tw, th)

        if caracter == 'A':   # Árbol solo el tronco para que el jugador pueda estar detras
            ancho = int(tw * 0.7)
            alto = int(th * 0.9)
            return pygame.Rect(col * tw + (tw - ancho) // 2,
                               fil * th + (th - alto), ancho, alto)

        if caracter == 'T':   # Tronco solo la franja del medio
            alto = int(th * 0.4)
            return pygame.Rect(col * tw, fil * th + (th - alto) // 2, tw, alto)

        return base           # Agua y pared el tile completo

    def colisiona_con_mapa(self, rect_pies):
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        col_ini = int(max(0, rect_pies.left // tw))
        col_fin = int(min(self.nivel.cols - 1, rect_pies.right // tw))
        fil_ini = int(max(0, rect_pies.top // th))
        fil_fin = int(min(self.nivel.filas - 1, rect_pies.bottom // th))

        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                if self.nivel.es_solido(col, fil):
                    if rect_pies.colliderect(
                            self.hitbox_tile(self.nivel.celda(col, fil), col, fil)):
                        return True
        return False

    def colisiona_con_npcs(self, rect_pies):
        ancho = int(ajustes.JUG_W * ajustes.HITBOX_ANCHO)
        alto = int(ajustes.JUG_H * ajustes.HITBOX_ALTO)
        off_x = (ajustes.JUG_W - ancho) // 2
        off_y = ajustes.JUG_H - alto - 2
        for npc in self.npcs:
            if npc.get('solido', False):
                r = pygame.Rect(npc['x'] + off_x, npc['y'] + off_y, ancho, alto)
                if rect_pies.colliderect(r):
                    return True
        return False
    #endregion

    #region Eventos
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.gestor.desapilar()
            elif evento.key in (pygame.K_UP, pygame.K_w):
                self.teclas['up'] = True
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.teclas['down'] = True
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                self.teclas['left'] = True
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.teclas['right'] = True
            elif evento.key == pygame.K_g and ajustes.MOSTRAR_DEPURACION:
                #La rejilla es de depuración si está apagada, la tecla no hace nada
                self.estado.mostrar_rejilla = not self.estado.mostrar_rejilla
            elif evento.key == pygame.K_SPACE and self.ataque_listo:
                self.ataque_idx = 0
                self.t_ataque = 0.0
                self.ataque_listo = False
                self.jugador['atacando'] = True
                if self.audio:
                    self.audio.sfx('espada.wav') #todavia no esta este audio

        elif evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.teclas['up'] = False
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.teclas['down'] = False
            elif evento.key in (pygame.K_LEFT, pygame.K_a):
                self.teclas['left'] = False
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.teclas['right'] = False
    #endregion

    #region Actualizacion
    def actualizar(self, dt):
        self.mover(dt)
        self.revisar_salida()
        self.actualizar_camara()
        self.animar(dt)

    def mover(self, dt):
        j = self.jugador
        j['moviendose'] = False
        nueva_x, nueva_y = j['x'], j['y']

        if self.teclas['up']:
            j['direccion'] = 'espalda'; nueva_y -= j['velocidad'] * dt; j['moviendose'] = True
        elif self.teclas['down']:
            j['direccion'] = 'frente';  nueva_y += j['velocidad'] * dt; j['moviendose'] = True
        elif self.teclas['left']:
            j['direccion'] = 'izquierda'; nueva_x -= j['velocidad'] * dt; j['moviendose'] = True
        elif self.teclas['right']:
            j['direccion'] = 'derecha'; nueva_x += j['velocidad'] * dt; j['moviendose'] = True

        # Cada eje se resuelve por separado
        if nueva_x != j['x']:
            nueva_x = max(0, min(self.ancho_mapa - ajustes.JUG_W, nueva_x))
            hb = self.hitbox_pies(nueva_x, j['y'])
            if not self.colisiona_con_mapa(hb) and not self.colisiona_con_npcs(hb):
                j['x'] = nueva_x

        if nueva_y != j['y']:
            nueva_y = max(0, min(self.alto_mapa - ajustes.JUG_H, nueva_y))
            hb = self.hitbox_pies(j['x'], nueva_y)
            if not self.colisiona_con_mapa(hb) and not self.colisiona_con_npcs(hb):
                j['y'] = nueva_y

    def revisar_salida(self):
        #Si el jugador acaba de entrar a un tile con salida cambia de nivel
        tile = self.tile_del_jugador()
        if tile == self.tile_previo: #evitar bucle o repetir la accion en cada frame
            return
        self.tile_previo = tile
        destino = self.nivel.salida_en(tile[0], tile[1])
        if destino:
            nombre, col, fil = destino
            if self.audio:
                self.audio.sfx('puerta.wav') #todavia no esta este audio
            self.cargar_nivel(nombre, (col, fil))

    def actualizar_camara(self):
        c, j = self.camera, self.jugador
        c['x'] = j['x'] + ajustes.JUG_W // 2 - ajustes.ANCHO // 2
        c['y'] = j['y'] + ajustes.JUG_H // 2 - ajustes.ALTO // 2
        # Nunca mostrar fuera del mapa, deja la cámara pegada en 0 y el mapa queda quieto
        c['x'] = max(0, min(max(0, self.ancho_mapa - ajustes.ANCHO), c['x']))
        c['y'] = max(0, min(max(0, self.alto_mapa - ajustes.ALTO), c['y']))

    def animar(self, dt):
        self.t_frame += dt
        if self.t_frame >= 1.0 / ajustes.FPS_ANIM:
            self.frame_idx = ((self.frame_idx + 1) % ajustes.FRAMES_ANIM
                              if self.jugador['moviendose'] else 0)
            self.t_frame = 0.0

        if not self.ataque_listo:
            self.t_ataque += dt
            if self.t_ataque >= 1.0 / ajustes.FPS_ATAQUE:
                self.ataque_idx += 1
                if self.ataque_idx >= ajustes.FRAMES_ANIM:
                    self.ataque_idx = 0
                    self.ataque_listo = True
                    self.jugador['atacando'] = False
                self.t_ataque = 0.0
    #endregion

    #region Dibujo
    def dibujar(self, pantalla):
        pantalla.fill(ajustes.BLANCO)
        rango = self.rango_visible()
        self.dibujar_terreno(pantalla, rango)
        self.dibujar_ordenados(pantalla, rango)
        self.dibujar_rejilla(pantalla, rango)
        self.dibujar_info(pantalla)

    def rango_visible(self):
        #Solo se dibuja lo que entra en pantalla
        c = self.camera
        tw, th = ajustes.TILE_W, ajustes.TILE_H
        return (int(max(0, c['x'] // tw)),
                int(min(self.nivel.cols - 1, (c['x'] + ajustes.ANCHO) // tw + 1)),
                int(max(0, c['y'] // th)),
                int(min(self.nivel.filas - 1, (c['y'] + ajustes.ALTO) // th + 1)))

    def dibujar_terreno(self, pantalla, rango):
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                px = col * ajustes.TILE_W - camara['x']
                py = fil * ajustes.TILE_H - camara['y']
                caracter = self.nivel.celda(col, fil)

                # Todo el fondo tiene pasto como base
                pantalla.blit(self.terreno.pasto[0], (px, py))

                tipo_tile = self.nivel.terrenos.get(caracter)
                if tipo_tile:
                    bitmask = self.terreno.bitmask(self.nivel.mapa, col, fil, caracter)
                    pantalla.blit(self.terreno.tile(tipo_tile, bitmask), (px, py))
                    if tipo_tile == 'agua':
                        for e in self.terreno.recodos(self.nivel.mapa, col, fil, caracter, bitmask):
                            pantalla.blit(self.terreno.agua_esq[e], (px, py))
                elif caracter in self.objeto_images and caracter != 'A':
                    #Los objetos planos van aca, el árbol va por profundidad
                    pantalla.blit(self.objeto_images[caracter], (px, py))

    def dibujar_ordenados(self, pantalla, rango):
        #Personajes y obstáculos altos, ordenados por la Y de sus pies
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        elementos = []

        if self.jugador['atacando']:
            frames = self.ataque_frames[self.jugador['direccion']]
            sprite = frames[min(self.ataque_idx, len(frames) - 1)]
        else:
            frames = self.jugador_frames[self.jugador['direccion']]
            sprite = frames[min(self.frame_idx, len(frames) - 1)]

        elementos.append({
            'tipo': 'jugador',
            'y_sort': self.jugador['y'] + ajustes.JUG_H,
            'x': self.jugador['x'] - camara['x'],
            'y': self.jugador['y'] - camara['y'],
            'sprite': sprite,
        })

        for npc in self.npcs:
            elementos.append({
                'tipo': 'npc',
                'y_sort': npc['y'] + ajustes.JUG_H,
                'x': npc['x'] - camara['x'],
                'y': npc['y'] - camara['y'],
                'sprite': npc['sprite'],
                'ref': npc,
            })

        # arboles miden 96 y el tile 64 entonces se ancla la base al borde inferior del tile y las hojas se salen arriba
        if 'A' in self.objeto_images:
            for fil in range(fil_ini, fil_fin + 1):
                for col in range(col_ini, col_fin + 1):
                    if self.nivel.celda(col, fil) == 'A':
                        elementos.append({
                            'tipo': 'tile',
                            'y_sort': (fil + 1) * ajustes.TILE_H,
                            'x': col * ajustes.TILE_W + ajustes.TILE_W // 2 - ajustes.ARBOL_W // 2 - camara['x'],
                            'y': (fil + 1) * ajustes.TILE_H - ajustes.ARBOL_H - camara['y'],
                            'sprite': self.objeto_images['A'],
                            'caracter': 'A',
                            'celda': (col, fil),
                        })

        elementos.sort(key=lambda e: e['y_sort'])

        #dibujamos todo
        for e in elementos:
            pantalla.blit(e['sprite'], (e['x'], e['y']))
            if ajustes.MOSTRAR_DEPURACION:
                self.dibujar_hitbox(pantalla, e)

    def dibujar_hitbox(self, pantalla, elemento):
        #Dibuja lo de depuracion si esta activa
        if not ajustes.MOSTRAR_DEPURACION:
            return
        camara = self.camera
        if elemento['tipo'] == 'jugador':
            hb = self.hitbox_pies(elemento['x'] + camara['x'], elemento['y'] + camara['y'])
            pygame.draw.rect(pantalla, ajustes.HITBOX_JUGADOR,
                             (hb.x - camara['x'], hb.y - camara['y'], hb.width, hb.height), 1)
        elif elemento['tipo'] == 'npc':
            if elemento['ref'].get('solido', False):
                ancho = int(ajustes.JUG_W * ajustes.HITBOX_ANCHO)
                alto = int(ajustes.JUG_H * ajustes.HITBOX_ALTO)
                pygame.draw.rect(pantalla, ajustes.HITBOX_NPC,
                                 (elemento['x'] + (ajustes.JUG_W - ancho) // 2,
                                  elemento['y'] + ajustes.JUG_H - alto - 2, ancho, alto), 1)
        elif elemento['tipo'] == 'tile':
            col, fil = elemento['celda']
            hb = self.hitbox_tile(elemento['caracter'], col, fil)
            pygame.draw.rect(pantalla, ajustes.HITBOX_TILE,
                             (hb.x - camara['x'], hb.y - camara['y'], hb.width, hb.height), 1)

    def dibujar_rejilla(self, pantalla, rango):
        #Dibuja (columna, fila) sobre cada tile para identificarlos facil
        if not (ajustes.MOSTRAR_DEPURACION and self.estado.mostrar_rejilla):
            return
        col_ini, col_fin, fil_ini, fil_fin = rango
        camara = self.camera
        for fil in range(fil_ini, fil_fin + 1):
            for col in range(col_ini, col_fin + 1):
                px = col * ajustes.TILE_W - camara['x']
                py = fil * ajustes.TILE_H - camara['y']
                pygame.draw.rect(pantalla, ajustes.COLOR_REJILLA,
                                 (px, py, ajustes.TILE_W, ajustes.TILE_H), 1)
                if (col, fil) not in self._cache_rejilla:
                    txt = self.font_rejilla.render('%d,%d' % (col, fil), True, (25, 25, 25))
                    fondo = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2),
                                           pygame.SRCALPHA)
                    fondo.fill((255, 255, 255, 195))
                    fondo.blit(txt, (2, 1))
                    self._cache_rejilla[(col, fil)] = fondo
                pantalla.blit(self._cache_rejilla[(col, fil)], (px + 2, py + 2))

    def dibujar_info(self, pantalla):
        #Dibuja la info si esta activa la depuracion
        if not ajustes.MOSTRAR_DEPURACION:
            return
        jugador = self.jugador
        estado = ('ATACANDO' if jugador['atacando']
                  else ('MOVIENDOSE' if jugador['moviendose'] else 'QUIETO'))
        col, fil = self.tile_del_jugador()
        texto = ('%s  Tile: %d,%d | %s | Mapa: %dx%d | ESPACIO=atacar  G=rejilla'
                 % (self.nivel.titulo, col, fil, estado,
                    self.nivel.cols, self.nivel.filas))
        info = self.font.render(texto, True, ajustes.NEGRO)
        pygame.draw.rect(pantalla, ajustes.BLANCO,
                         (0, ajustes.ALTO - 22, ajustes.ANCHO, 22))
        pantalla.blit(info, (5, ajustes.ALTO - 18))
    #endregion
