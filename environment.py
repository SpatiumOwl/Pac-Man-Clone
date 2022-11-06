import pygame
import os

from map_graph import MapGraph

# Basic information about the map
class Map:
    SCALING = 3
    FIELD_OFFSET = 8
    MAP_WIDTH = 224
    MAP_HEIGHT = 248 + FIELD_OFFSET
    MAP_TEXTURE = pygame.image.load(os.path.join("Assets/Map", "BG.png"))
    TILE_SIZE = 8

    # Font info
    pygame.font.init()
    MAIN_FONT = pygame.font.Font(os.path.join("Assets", "C64_Pro_Mono-STYLE.ttf"), 8*SCALING)

    MAP_GRAPH = MapGraph.FromMapString("""XXXXXXXXXXXXXXXXXXXXXXXXXXXX
XOOOOOOOOOOOOXXOOOOOOOOOOOOX
XOXXXXOXXXXXOXXOXXXXXOXXXXOX
XOXXXXOXXXXXOXXOXXXXXOXXXXOX
XOXXXXOXXXXXOXXOXXXXXOXXXXOX
XOOOOOOOOOOOOOOOOOOOOOOOOOOX
XOXXXXOXXOXXXXXXXXOXXOXXXXOX
XOXXXXOXXOXXXXXXXXOXXOXXXXOX
XOOOOOOXXOOOOXXOOOOXXOOOOOOX
XXXXXXOXXXXXOXXOXXXXXOXXXXXX
XXXXXXOXXXXXOXXOXXXXXOXXXXXX
XXXXXXOXXOOOOOOOOOOXXOXXXXXX
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
OOOOOOOOOOXXXXXXXXOOOOOOOOOO
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
XXXXXXOXXOOOOOOOOOOXXOXXXXXX
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
XXXXXXOXXOXXXXXXXXOXXOXXXXXX
XOOOOOOOOOOOOXXOOOOOOOOOOOOX
XOXXXXOXXXXXOXXOXXXXXOXXXXOX
XOXXXXOXXXXXOXXOXXXXXOXXXXOX
XOOOXXOOOOOOOOOOOOOOOOXXOOOX
XXXOXXOXXOXXXXXXXXOXXOXXOXXX
XXXOXXOXXOXXXXXXXXOXXOXXOXXX
XOOOOOOXXOOOOXXOOOOXXOOOOOOX
XOXXXXXXXXXXOXXOXXXXXXXXXXOX
XOXXXXXXXXXXOXXOXXXXXXXXXXOX
XOOOOOOOOOOOOOOOOOOOOOOOOOOX
XXXXXXXXXXXXXXXXXXXXXXXXXXXX""")
    GHOST_SPAWN_POINT = (13, 11)
    GHOST_SPAWN = pygame.Rect(GHOST_SPAWN_POINT[0]*TILE_SIZE*SCALING, 
        (GHOST_SPAWN_POINT[1]*TILE_SIZE + FIELD_OFFSET)*SCALING,
        TILE_SIZE*SCALING, TILE_SIZE*SCALING)

# Abstract class for pellets
class Pellet:
    def __init__(self, window, position):
        self.x = position[0] * Map.SCALING
        self.y = position[1] * Map.SCALING
        self.window = window
        
        self.load_sprite()

        self.collider = pygame.Rect(position[0]*Map.SCALING, position[1]*Map.SCALING, self.sprite.get_width(), self.sprite.get_height())

    def load_sprite(self):
        self.sprite = pygame.transform.scale(self.SPRITE_TEXTURE, 
            (self.SPRITE_TEXTURE.get_width()*Map.SCALING, self.SPRITE_TEXTURE.get_height()*Map.SCALING))

    def draw(self):
        self.window.blit(self.sprite, (self.collider.x, self.collider.y))
class RegularPellet(Pellet):
    SPRITE_TEXTURE = pygame.image.load(os.path.join("Assets/Map", "SmallPellet.png"))
class SuperPellet(Pellet):
    SPRITE_TEXTURE = pygame.image.load(os.path.join("Assets/Map", "BigPellet.png"))

# Contains invisible rectangle collider objects that correspond to the walls drawn on the map
class Walls:
    wall_colliders = []

    def __init__(self, vert_offset):
        scaling = Map.SCALING
        #Outer walls
            #Top part
        self.wall_colliders.append(pygame.Rect(0, scaling*vert_offset, 
        scaling*4, scaling*76))
        self.wall_colliders.append(pygame.Rect(0, scaling*vert_offset, 
        scaling*224, scaling*4))
        self.wall_colliders.append(pygame.Rect(scaling*108, scaling*vert_offset, 
        scaling*8, scaling*36))
        self.wall_colliders.append(pygame.Rect(scaling*220, scaling*vert_offset, 
        scaling*4, scaling*76))
        self.wall_colliders.append(pygame.Rect(0, scaling*(vert_offset + 76), 
        scaling*44, scaling*32))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 76), 
        scaling*44, scaling*32))

            #Bottom part
        self.wall_colliders.append(pygame.Rect(0, scaling*(248 + vert_offset - 92), 
        scaling*4, scaling*92))
        self.wall_colliders.append(pygame.Rect(0, scaling*(248 + vert_offset - 4), 
        scaling*224, scaling*4))
        self.wall_colliders.append(pygame.Rect(scaling*220, scaling*(248 + vert_offset - 92), 
        scaling*4, scaling*92))
        self.wall_colliders.append(pygame.Rect(0, scaling*(vert_offset + 124), 
        scaling*44, scaling*32))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 124), 
        scaling*44, scaling*32))
        self.wall_colliders.append(pygame.Rect(scaling*4, scaling*(vert_offset + 196), 
        scaling*16, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*(224 - 16 - 4), scaling*(vert_offset + 196), 
        scaling*16, scaling*8))

        #Top blocks
            
        self.wall_colliders.append(pygame.Rect(scaling*20, scaling*(vert_offset + 20), 
        scaling*24, scaling*16))
        self.wall_colliders.append(pygame.Rect(scaling*60, scaling*(vert_offset + 20), 
        scaling*32, scaling*16))
        self.wall_colliders.append(pygame.Rect(scaling*132, scaling*(vert_offset + 20), 
        scaling*32, scaling*16))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 20), 
        scaling*24, scaling*16))
        self.wall_colliders.append(pygame.Rect(scaling*20, scaling*(vert_offset + 52), 
        scaling*24, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 52), 
        scaling*24, scaling*8))

        #Top Ts
        self.wall_colliders.append(pygame.Rect(scaling*60, scaling*(vert_offset + 52), 
        scaling*8, scaling*56))
        self.wall_colliders.append(pygame.Rect(scaling*68, scaling*(vert_offset + 76), 
        scaling*24, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*156, scaling*(vert_offset + 52), 
        scaling*8, scaling*56))
        self.wall_colliders.append(pygame.Rect(scaling*132, scaling*(vert_offset + 76), 
        scaling*24, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*84, scaling*(vert_offset + 52), 
        scaling*56, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*108, scaling*(vert_offset + 60), 
        scaling*8, scaling*24))

        #Bottom blocks
        self.wall_colliders.append(pygame.Rect(scaling*60, scaling*(vert_offset + 124), 
        scaling*8, scaling*32))
        self.wall_colliders.append(pygame.Rect(scaling*156, scaling*(vert_offset + 124), 
        scaling*8, scaling*32))
        self.wall_colliders.append(pygame.Rect(scaling*60, scaling*(vert_offset + 172), 
        scaling*32, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*132, scaling*(vert_offset + 172), 
        scaling*32, scaling*8))

        #Bottom turns
        self.wall_colliders.append(pygame.Rect(scaling*20, scaling*(vert_offset + 172), 
        scaling*24, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*36, scaling*(vert_offset + 180), 
        scaling*8, scaling*24))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 172), 
        scaling*24, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*180, scaling*(vert_offset + 180), 
        scaling*8, scaling*24))

        #Bottom Ts
        self.wall_colliders.append(pygame.Rect(scaling*84, scaling*(vert_offset + 148), 
        scaling*56, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*108, scaling*(vert_offset + 156), 
        scaling*8, scaling*24))
        self.wall_colliders.append(pygame.Rect(scaling*84, scaling*(vert_offset + 196), 
        scaling*56, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*108, scaling*(vert_offset + 204), 
        scaling*8, scaling*24))
        self.wall_colliders.append(pygame.Rect(scaling*60, scaling*(vert_offset + 196), 
        scaling*8, scaling*24))
        self.wall_colliders.append(pygame.Rect(scaling*20, scaling*(vert_offset + 220), 
        scaling*72, scaling*8))
        self.wall_colliders.append(pygame.Rect(scaling*156, scaling*(vert_offset + 196), 
        scaling*8, scaling*24))
        self.wall_colliders.append(pygame.Rect(scaling*132, scaling*(vert_offset + 220), 
        scaling*72, scaling*8))

        #Center block
        self.wall_colliders.append(pygame.Rect(scaling*84, scaling*(vert_offset + 100), 
        scaling*56, scaling*32))

# Contains positions of all the pellets on the map
class Pellets:
    
    def __init__(self, window, vert_offset):
        self.add_regular_pellets(window, vert_offset)
        self.add_super_pellets(window, vert_offset)

    def add_regular_pellets(self, window, vert_offset):
        self.regular_pellets = []
        for i in range (12):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 11 + vert_offset]))
        for i in range (12):
            self.regular_pellets.append(RegularPellet(window, [123 + 8*i, 11 + vert_offset]))

        for i in range (25):
            self.regular_pellets.append(RegularPellet(window, [51, 19 + vert_offset + 8*i]))
        for i in range (25):
            self.regular_pellets.append(RegularPellet(window, [171, 19 + vert_offset + 8*i]))

        for i in range (26):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 235 + vert_offset]))

        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 43 + vert_offset]))
        for i in range (14):
            self.regular_pellets.append(RegularPellet(window, [59 + 8*i, 43 + vert_offset]))
        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [179 + 8*i, 43 + vert_offset]))

        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 67 + vert_offset]))
        for i in range (4):
            self.regular_pellets.append(RegularPellet(window, [75 + 8*i, 67 + vert_offset]))
        for i in range (4):
            self.regular_pellets.append(RegularPellet(window, [123 + 8*i, 67 + vert_offset]))
        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [179 + 8*i, 67 + vert_offset]))

        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 163 + vert_offset]))
        for i in range (6):
            self.regular_pellets.append(RegularPellet(window, [59 + 8*i, 163 + vert_offset]))
        for i in range (6):
            self.regular_pellets.append(RegularPellet(window, [123 + 8*i, 163 + vert_offset]))
        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [179 + 8*i, 163 + vert_offset]))
        
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [19 + 8*i, 187 + vert_offset]))
        for i in range (7):
            self.regular_pellets.append(RegularPellet(window, [51 + 8*i, 187 + vert_offset]))
        for i in range (7):
            self.regular_pellets.append(RegularPellet(window, [123 + 8*i, 187 + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [195 + 8*i, 187 + vert_offset]))

        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [11 + 8*i, 211 + vert_offset]))
        for i in range (4):
            self.regular_pellets.append(RegularPellet(window, [75 + 8*i, 211 + vert_offset]))
        for i in range (4):
            self.regular_pellets.append(RegularPellet(window, [123 + 8*i, 211 + vert_offset]))
        for i in range (5):
            self.regular_pellets.append(RegularPellet(window, [179 + 8*i, 211 + vert_offset]))

        self.regular_pellets.append(RegularPellet(window, [11, 19 + vert_offset]))
        self.regular_pellets.append(RegularPellet(window, [11, 35 + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [11, 51 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [11, 171 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [11, 219 + 8*i + vert_offset]))
        
        self.regular_pellets.append(RegularPellet(window, [211, 19 + vert_offset]))
        self.regular_pellets.append(RegularPellet(window, [211, 35 + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [211, 51 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [211, 171 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [211, 219 + 8*i + vert_offset]))

        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [27, 195 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [195, 195 + 8*i + vert_offset]))

        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [75, 51 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [75, 195 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [147, 51 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [147, 195 + 8*i + vert_offset]))

        for i in range (3):
            self.regular_pellets.append(RegularPellet(window, [99, 19 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [99, 171 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [99, 219 + 8*i + vert_offset]))
        
        for i in range (3):
            self.regular_pellets.append(RegularPellet(window, [123, 19 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [123, 171 + 8*i + vert_offset]))
        for i in range (2):
            self.regular_pellets.append(RegularPellet(window, [123, 219 + 8*i + vert_offset]))
    def add_super_pellets(self, window, vert_offset):
        self.super_pellets = []

        self.super_pellets.append(SuperPellet(window, [8, 24 + vert_offset]))
        self.super_pellets.append(SuperPellet(window, [208, 24 + vert_offset]))
        self.super_pellets.append(SuperPellet(window, [8, 184 + vert_offset]))
        self.super_pellets.append(SuperPellet(window, [208, 184 + vert_offset]))
    def draw_all(self):
        for pellet in self.regular_pellets:
            pellet.draw()
        for pellet in self.super_pellets:
            pellet.draw()

# Contains all the music and sound effects
class SFX:
    pygame.mixer.init()

    GAME_START = pygame.mixer.Sound(os.path.join("Assets/Sound", "game_start.wav"))
    GAME_START.set_volume(0.5)
    
    MUNCH_1 = pygame.mixer.Sound(os.path.join("Assets/Sound", "munch_1.wav"))
    MUNCH_1.set_volume(0.5)
    MUNCH_2 = pygame.mixer.Sound(os.path.join("Assets/Sound", "munch_2.wav"))
    MUNCH_2.set_volume(0.5)
    current_munch = 1

    SIREN_1 = pygame.mixer.Sound(os.path.join("Assets/Sound", "siren_1.wav"))
    SIREN_1.set_volume(0.3)

    SUPER_PELLET = pygame.mixer.Sound(os.path.join("Assets/Sound", "power_pellet.wav"))
    SUPER_PELLET.set_volume(0.5)

    EAT_GHOST = pygame.mixer.Sound(os.path.join("Assets/Sound", "eat_ghost.wav"))
    EAT_GHOST.set_volume(0.5)

    DEATH_1 = pygame.mixer.Sound(os.path.join("Assets/Sound", "death_1.wav"))
    DEATH_1.set_volume(0.3)
