import pygame
import os
import environment as env
import userevents as ue
from enum import Enum

# Enum for direction for different characters
class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

# Abstract class for the game characters
class GameCharacter:    
    # All the characters are made of 4 tiles (2x2)
    CHARACTER_SPRITE_SIZE = [env.Map.TILE_SIZE * 2, env.Map.TILE_SIZE * 2]
    
    # Makes sure that simply touching an object with the side of the character doesn't make them eat the object
    EAT_COLLIDER_INNER_MARGIN = 3

    def __init__(self, window, spawn_pos):
        self.window = window
        self.direction = Direction.RIGHT

        # Set up the animation
        self.load_animation_frames()
        self.current_frame = 0

        # Create and place all the colliders on the map
        self.body_collider = pygame.Rect(spawn_pos[0]*env.Map.SCALING, spawn_pos[1]*env.Map.SCALING, 
            self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)
        self.eat_collider = pygame.Rect(self.body_collider.x + self.EAT_COLLIDER_INNER_MARGIN*env.Map.SCALING, 
            self.body_collider.y + self.EAT_COLLIDER_INNER_MARGIN*env.Map.SCALING, 
            self.body_collider.width - 2*self.EAT_COLLIDER_INNER_MARGIN*env.Map.SCALING, 
            self.body_collider.height - 2*self.EAT_COLLIDER_INNER_MARGIN*env.Map.SCALING)
    
    def load_animation_frames(self):
        pass

    def animate(self):
        self.draw_next_frame()    
    
    def draw_next_frame(self):
        self.set_spriteset()
        
        current_sprite = self.get_current_sprite()

        # Draw the sprite on the screen 
        self.window.blit(current_sprite, (self.body_collider.x, self.body_collider.y))

        self.advance_the_counter()       
    
    def set_spriteset(self):
        pass

    def get_current_sprite(self):
        pass
    
    def advance_the_counter(self):
        self.current_frame += 1
        
        if (self.current_frame >= len(self.current_spriteset)):
            self.current_frame = 0

    # Tries to move a character in chosen direction
    # If not possible, proceeds in the previous direction
    # If that is also not possible, the character stops
    def move(self, direction, walls):
        turned_succesfully = self.try_turn_and_report_success(direction, walls)

        if (not turned_succesfully):
            self.try_to_proceed_forward(walls)

        self.update_eat_collider()
        self.wrap_around_if_outside_map()
    
    def try_turn_and_report_success(self, direction, walls):
        next_move = pygame.Rect(self.body_collider)
        
        self.move_collider(next_move, direction)
                
        if (self.can_freely_move_to(next_move, walls.wall_colliders)):
            self.body_collider.x = next_move.x
            self.body_collider.y = next_move.y
            self.direction = direction

            return True
        else:
            return False

    def try_to_proceed_forward(self, walls):
        next_direction = self.direction
        next_move = pygame.Rect(self.body_collider)

        self.move_collider(next_move, next_direction)

        if (self.can_freely_move_to(next_move, walls.wall_colliders)):
            self.body_collider.x = next_move.x
            self.body_collider.y = next_move.y
            self.direction = next_direction
    
    def move_collider(self, collider, direction):
        if (direction == Direction.RIGHT):
            collider.x += self.speed
        elif (direction == Direction.UP):
            collider.y -= self.speed
        elif (direction == Direction.LEFT):
            collider.x -= self.speed
        elif (direction == Direction.DOWN):
            collider.y += self.speed
    
    def can_freely_move_to(self, next_move, colliders):
        for collider in colliders:
            if (next_move.colliderect(collider)):
                return False
        return True

    def update_eat_collider(self):
        self.eat_collider.x = self.body_collider.x + self.EAT_COLLIDER_INNER_MARGIN
        self.eat_collider.y = self.body_collider.y + self.EAT_COLLIDER_INNER_MARGIN

    def wrap_around_if_outside_map(self):
        if self.body_collider.x > env.Map.MAP_WIDTH * env.Map.SCALING:
            self.body_collider.x = -self.body_collider.width
        elif self.body_collider.x < -self.body_collider.width:
            self.body_collider.x = env.Map.MAP_WIDTH * env.Map.SCALING

class PacMan(GameCharacter):    
    SPEED_IN_UNITS = 2

    def __init__(self, window, spawn_pos):
        self.speed = self.SPEED_IN_UNITS * env.Map.SCALING
        super().__init__(window, spawn_pos)
        self.current_spriteset = self.IDLE_SPRITESET
    
    # Pac-Man has only one spriteset, with last two frames being identical to the first two ones (but in reversed order)
    def load_animation_frames(self):
        self.IDLE_SPRITESET = []

        self.IDLE_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join("Assets/Pac-Man", "Idle_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join("Assets/Pac-Man", "Idle_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join("Assets/Pac-Man", "Idle_2.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_SPRITESET.append(self.IDLE_SPRITESET[1])
        self.IDLE_SPRITESET.append(self.IDLE_SPRITESET[0])
    
    # To point Pac-Man in correct direction, we just have to rotate the sprite
    def get_current_sprite(self):
        rotation_angle = self.find_rotation_angle()
        return pygame.transform.rotate(
            self.current_spriteset[self.current_frame], rotation_angle
        )
    
    def update(self, keys, walls, pellets, ghosts):
        self.move(self.find_new_direction(keys), walls)
        self.eat_pellets(pellets)
        self.eat_ghosts(ghosts)
        self.animate()

    def find_rotation_angle(self):
        if (self.direction == Direction.RIGHT):
            return 0
        elif (self.direction == Direction.UP):
            return 90
        elif (self.direction == Direction.LEFT):
            return 180
        elif (self.direction == Direction.DOWN):
            return 270
    
    def find_new_direction(self, keys):
        if keys[pygame.K_w]:
            return Direction.UP
        if keys[pygame.K_d]:
            return Direction.RIGHT
        if keys[pygame.K_s]:
            return Direction.DOWN
        if keys[pygame.K_a]:
            return Direction.LEFT  
        return self.direction
    
    def eat_pellets(self, pellets):
        for pellet in pellets.regular_pellets:
            if self.eat_collider.colliderect(pellet.collider):
                pellets.regular_pellets.remove(pellet)
                pygame.event.post(pygame.event.Event(ue.UserEvents.ATE_REGULAR_PELLET))
                self.play_munch_sound()
                
        for pellet in pellets.super_pellets:
            if self.eat_collider.colliderect(pellet.collider):
                pellets.super_pellets.remove(pellet)
                pygame.event.post(pygame.event.Event(ue.UserEvents.ATE_SUPER_PELLET))
    
    # Pac-Man has two munch sounds for pellets that switch between one and the other
    def play_munch_sound(self):
        if (env.SFX.current_munch == 1):
            env.SFX.MUNCH_1.play()
            env.SFX.current_munch = 2
        else:
            env.SFX.MUNCH_2.play()
            env.SFX.current_munch = 1

    def eat_ghosts(self, ghosts):
        for ghost in ghosts:
            if (ghost.current_state == GhostState.VULNERABLE):
                if (self.eat_collider.colliderect(ghost.body_collider)):
                    ghosts.remove(ghost)
                    pygame.event.post(pygame.event.Event(ue.UserEvents.ATE_GHOST))
                    env.SFX.EAT_GHOST.play()

class Ghost(GameCharacter):
    # Ghosts have two different speeds for regular and vulnerable mode
    DEFAULT_SPEED = 2
    SLOW_SPEED = 1
    
    # Walk patterns are temporary placeholders for AI
    # Only red color has been created so far
    def __init__(self, window, spawn_pos, color, walk_pattern):
        self.WALK_PATTERN = walk_pattern
        self.color = color

        # Ghost can be in three different states (see below). Defeated state isn't implemented yet
        self.current_state = GhostState.DEFAULT
        super().__init__(window, spawn_pos)
        self.current_spriteset = self.IDLE_RIGHT_SPRITESET

        # Anchor is a point around which the ghost goes in its walk pattern
        self.anchor = [self.body_collider.x, self.body_collider.y]

        if (walk_pattern == WalkPattern.HORIZONTAL_8):
            self.direction = Direction.RIGHT
        elif (walk_pattern == WalkPattern.VERTICAL_8):
            self.direction = Direction.UP
    
    def load_animation_frames(self):
        path = self.get_ghost_animation_frames_path()
        self.load_idle_animation_frames(path)
        self.load_vulnerable_animation_frames(path)
    
    # Theoretically all the colors are usable now, but only red sprites are done at the moment
    def get_ghost_animation_frames_path(self):
        path = ""
        if (self.color == GhostColor.RED):
            path = "Assets/Ghosts/Red"
        elif (self.color == GhostColor.PINK):
            path = "Assets/Ghosts/Pink"
        elif (self.color == GhostColor.CYAN):
            path = "Assets/Ghosts/Cyan"
        elif (self.color == GhostColor.ORANGE):
            path = "Assets/Ghosts/Orange"
        
        return path

    # Idle corresponds to ghost's regular state. Additionale, all the directions have different spritesheets 
    def load_idle_animation_frames(self, path):
        self.IDLE_RIGHT_SPRITESET = []
        self.IDLE_RIGHT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_right_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_RIGHT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_right_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.IDLE_LEFT_SPRITESET = []
        self.IDLE_LEFT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_left_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_LEFT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_left_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.IDLE_UP_SPRITESET = []
        self.IDLE_UP_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_up_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_UP_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_up_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.IDLE_DOWN_SPRITESET = []
        self.IDLE_DOWN_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_down_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.IDLE_DOWN_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Idle_down_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

    def load_vulnerable_animation_frames(self, path):
        self.VULNERABLE_SPRITESET = []

        self.VULNERABLE_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Vulnerable_0.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))
        self.VULNERABLE_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Vulnerable_1.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

    def update(self, walls, pac_man):
        self.set_speed()
        self.execute_walk_pattern(walls)
        self.animate()
        self.eat_pac_man(pac_man)

    # Ghosts are slow only in vulnerable state
    def set_speed(self):
        if (self.current_state == GhostState.VULNERABLE):
            self.speed = self.SLOW_SPEED * env.Map.SCALING
        else:
            self.speed = self.DEFAULT_SPEED * env.Map.SCALING

    def execute_walk_pattern(self, walls):
        if (self.WALK_PATTERN == WalkPattern.HORIZONTAL_8):
            self.execute_horizontal_8_walk_pattern(walls)
        elif (self.WALK_PATTERN == WalkPattern.VERTICAL_8):
            self.execute_vertical_8_walk_pattern(walls)

    # Back and forth horizontally within 8 tiles
    def execute_horizontal_8_walk_pattern(self, walls):
        if (self.body_collider.x <= self.anchor[0] - 4 * env.Map.TILE_SIZE * env.Map.SCALING):
            self.move(Direction.RIGHT, walls)
        elif (self.body_collider.x >= self.anchor[0] + 4 * env.Map.TILE_SIZE * env.Map.SCALING):
            self.move(Direction.LEFT, walls)
        else:
            self.move(self.direction, walls)
    
    # Back and forth vertically within 8 tiles
    def execute_vertical_8_walk_pattern(self, walls):
        if (self.body_collider.y <= self.anchor[1] - 4 * env.Map.TILE_SIZE * env.Map.SCALING):
            self.move(Direction.DOWN, walls)
        elif (self.body_collider.y >= self.anchor[1] + 4 * env.Map.TILE_SIZE * env.Map.SCALING):
            self.move(Direction.UP, walls)
        else:
            self.move(self.direction, walls)

    # Choose the current spriteset depending on state and direction
    def set_spriteset(self):
        new_spriteset = []
        if (self.current_state == GhostState.VULNERABLE):
            new_spriteset = self.VULNERABLE_SPRITESET
        elif (self.current_state == GhostState.DEFEATED):
            new_spriteset = self.DEFEATED_SPRITESET
        elif (self.current_state == GhostState.DEFAULT):
            if (self.direction == Direction.RIGHT):
                new_spriteset = self.IDLE_RIGHT_SPRITESET
            elif (self.direction == Direction.LEFT):
                new_spriteset = self.IDLE_LEFT_SPRITESET
            elif (self.direction == Direction.UP):
                new_spriteset = self.IDLE_UP_SPRITESET
            elif (self.direction == Direction.DOWN):
                new_spriteset = self.IDLE_DOWN_SPRITESET
        
        if (self.current_spriteset != new_spriteset):
            self.current_spriteset = new_spriteset
            self.current_frame = 0

    def get_current_sprite(self):
        return self.current_spriteset[self.current_frame]

    def eat_pac_man(self, pac_man):
        if (self.current_state == GhostState.DEFAULT):
            if self.eat_collider.colliderect(pac_man.body_collider):
                pygame.event.post(pygame.event.Event(ue.UserEvents.GAME_OVER))
        
class GhostState(Enum):
    DEFAULT = 0
    VULNERABLE = 1
    DEFEATED = 2

class GhostColor(Enum):
    RED = 0
    PINK = 1
    CYAN = 2
    ORANGE = 3

class WalkPattern(Enum):
    HORIZONTAL_8 = 0
    VERTICAL_8 = 1
