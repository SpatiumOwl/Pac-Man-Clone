from math import floor
import pygame
import os
from enum import Enum
from queue import SimpleQueue

import environment as env
import userevents as ue


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

        spawn_pos_px = ((spawn_pos[0]*env.Map.TILE_SIZE - GameCharacter.CHARACTER_SPRITE_SIZE[0]//2 + env.Map.TILE_SIZE//2)*env.Map.SCALING, 
            (spawn_pos[1]*env.Map.TILE_SIZE + env.Map.FIELD_OFFSET - GameCharacter.CHARACTER_SPRITE_SIZE[1]//2 + env.Map.TILE_SIZE//2)*env.Map.SCALING)

        # Create and place all the colliders on the map
        self.body_collider = pygame.Rect(spawn_pos_px[0], spawn_pos_px[1], 
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
    
    def get_current_tile(self):
        pos = [self.body_collider.centerx, self.body_collider.centery]
        pos[1] -= env.Map.FIELD_OFFSET * env.Map.SCALING

        pos[0] /= (env.Map.TILE_SIZE * env.Map.SCALING)
        pos[1] /= (env.Map.TILE_SIZE * env.Map.SCALING)
        
        pos[0] = floor(pos[0])
        pos[1] = floor(pos[1])
        
        return (pos[0], pos[1])

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
                    ghost.defeat()
                    pygame.event.post(pygame.event.Event(ue.UserEvents.ATE_GHOST))
                    env.SFX.EAT_GHOST.play()

class Ghost(GameCharacter):
    # Ghosts have two different speeds for regular and vulnerable mode
    DEFAULT_SPEED = 2
    SLOW_SPEED = 1
    RUN_TO_RESPAWN_SPEED = 2

    PAC_MAN_CHASE_DISTANCE = 10
    
    # Only red color has been created so far
    def __init__(self, window, spawn_pos, color, patrol_points):
        self.color = color

        # Ghost can be in three different states (see below). Defeated state isn't implemented yet
        self.current_state = GhostState.PATROL
        super().__init__(window, spawn_pos)
        self.current_spriteset = self.IDLE_RIGHT_SPRITESET

        # Initialise patrol
        self.patrol_queue = SimpleQueue()
        for patrol_point in patrol_points:
            self.patrol_queue.put(patrol_point)
        
        self.current_patrol_point = self.patrol_queue.get()

        # Vulnerability effect stack
        self.vulnerability_effect_count = 0

        # Initialize plan
        self.plan = SimpleQueue()
        self.next_plan_point = self.get_current_tile()
    
    def load_animation_frames(self):
        path = self.get_ghost_animation_frames_path()
        self.load_idle_animation_frames(path)
        self.load_vulnerable_animation_frames(path)
        self.load_defeated_animation_frames(path)
    
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

    def load_defeated_animation_frames(self, path):
        self.DEFEATED_RIGHT_SPRITESET = []
        self.DEFEATED_RIGHT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Defeated_right.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.DEFEATED_LEFT_SPRITESET = []
        self.DEFEATED_LEFT_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Defeated_left.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.DEFEATED_UP_SPRITESET = []
        self.DEFEATED_UP_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Defeated_up.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

        self.DEFEATED_DOWN_SPRITESET = []
        self.DEFEATED_DOWN_SPRITESET.append(pygame.transform.scale(
            pygame.image.load(
                os.path.join(path, "Defeated_down.png")
            ), (self.CHARACTER_SPRITE_SIZE[0]*env.Map.SCALING, self.CHARACTER_SPRITE_SIZE[1]*env.Map.SCALING)))

    def update(self, walls, pac_man):
        self.change_state(pac_man)
        self.execute_states(walls, pac_man)
        self.animate()
        self.eat_pac_man(pac_man)

    # State machine change state commands
    def change_state(self, pac_man):
        self.patrol_chase_interchange(pac_man)
        self.respawn_if_defeated()

    def put_on_vulnerability(self):
        if (self.current_state != GhostState.DEFEATED):
            self.vulnerability_effect_count += 1
            self.current_state = GhostState.VULNERABLE
    
    def take_off_vulnerability(self):
        if (self.current_state == GhostState.VULNERABLE):
            self.vulnerability_effect_count -= 1

            if (self.vulnerability_effect_count == 0):
                self.current_state = GhostState.PATROL   
    
    def patrol_chase_interchange(self, pac_man):
        if (self.current_state in [GhostState.PATROL, GhostState.CHASE]):
            if (env.MapGraph.manhattan_distance(self.get_current_tile(), pac_man.get_current_tile())
                > Ghost.PAC_MAN_CHASE_DISTANCE):
                self.current_state = GhostState.PATROL
            else:
                self.current_state = GhostState.CHASE
    
    def defeat(self):
        self.current_state = GhostState.DEFEATED
        self.vulnerability_effect_count = 0

    def respawn_if_defeated(self):
        if (self.current_state == GhostState.DEFEATED):
            if (self.body_collider.colliderect(env.Map.GHOST_SPAWN)):
                self.current_state = GhostState.PATROL

    # State machine execution commands
    def execute_states(self, walls, pac_man):
        self.set_speed()

        current_pos = self.get_current_tile()

        # Update the plan
        if (self.current_state == GhostState.CHASE):
            self.chase_pac_man(pac_man, current_pos, walls)
        elif (self.current_state == GhostState.PATROL):
            self.patrol(current_pos, walls)
        elif (self.current_state == GhostState.VULNERABLE):
            self.run_away(pac_man, current_pos, walls)
        elif (self.current_state == GhostState.DEFEATED):
            self.go_to_spawn(current_pos, walls)

    def chase_pac_man(self, pac_man, current_pos, walls):
        path = env.Map.MAP_GRAPH.get_shortest_path(current_pos, pac_man.get_current_tile())
        self.move_along_the_path(walls, path)
    
    def patrol(self, current_pos, walls):
        if (current_pos == self.current_patrol_point):
            self.patrol_queue.put(self.current_patrol_point)
            self.current_patrol_point = self.patrol_queue.get()
        else:
            path = env.Map.MAP_GRAPH.get_shortest_path(current_pos, self.current_patrol_point)
            self.move_along_the_path(walls, path)

    def run_away(self, pac_man, current_pos, walls):
        path_to_pac_man = env.Map.MAP_GRAPH.get_shortest_path(current_pos, pac_man.get_current_tile())

        if (len(path_to_pac_man) > 1):
            away_from_move = path_to_pac_man[1]

            next_move = Ghost.get_runaway_move(away_from_move, current_pos)
            self.move_along_the_path(walls, [current_pos, next_move])

    def get_runaway_move(away_from_move, current_pos):
        possible_moves = env.Map.MAP_GRAPH.neighbors(current_pos)
        safe_moves = [move for move in possible_moves if move != away_from_move]
        
        vec = (current_pos[0] - away_from_move[0], current_pos[1] - away_from_move[1])
        opposite_move = (current_pos[0] + vec[0], current_pos[1] + vec[1])
        if (opposite_move in safe_moves):
            return opposite_move
        else:
            # Any other safe move
            return safe_moves[0]

    def go_to_spawn(self, current_pos, walls):
        if (current_pos != env.Map.GHOST_SPAWN_POINT):
            path = env.Map.MAP_GRAPH.get_shortest_path(current_pos, env.Map.GHOST_SPAWN_POINT)
            self.move_along_the_path(walls, path)

    # Ghosts are slow only in vulnerable state
    def set_speed(self):
        if (self.current_state == GhostState.VULNERABLE):
            self.speed = self.SLOW_SPEED * env.Map.SCALING
        elif (self.current_state == GhostState.DEFEATED):
            self.speed = self.RUN_TO_RESPAWN_SPEED * env.Map.SCALING
        else:
            self.speed = self.DEFAULT_SPEED * env.Map.SCALING

    def move_along_the_path(self, walls, path):
        current_tile = self.get_current_tile()
        if (len(path) > 1):
            next_tile = path[1]
        else:
            next_tile = current_tile
            
        if (next_tile[0] < current_tile[0]):
            self.move(Direction.LEFT, walls)
        elif (next_tile[0] > current_tile[0]):
            self.move(Direction.RIGHT, walls)
        elif (next_tile[1] < current_tile[1]):
            self.move(Direction.UP, walls)
        elif (next_tile[1] > current_tile[1]):
            self.move(Direction.DOWN, walls)
    
    # Choose the current spriteset depending on state and direction
    def set_spriteset(self):
        new_spriteset = []
        if (self.current_state == GhostState.VULNERABLE):
            new_spriteset = self.VULNERABLE_SPRITESET
        elif (self.current_state == GhostState.DEFEATED):
            if (self.direction == Direction.RIGHT):
                new_spriteset = self.DEFEATED_RIGHT_SPRITESET
            elif (self.direction == Direction.LEFT):
                new_spriteset = self.DEFEATED_LEFT_SPRITESET
            elif (self.direction == Direction.UP):
                new_spriteset = self.DEFEATED_UP_SPRITESET
            elif (self.direction == Direction.DOWN):
                new_spriteset = self.DEFEATED_DOWN_SPRITESET
        elif (self.current_state in [GhostState.PATROL, GhostState.CHASE]):
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
        if (self.current_state == GhostState.CHASE):
            if self.eat_collider.colliderect(pac_man.body_collider):
                pygame.event.post(pygame.event.Event(ue.UserEvents.GAME_OVER))
        
class GhostState(Enum):
    PATROL = 0
    VULNERABLE = 1
    DEFEATED = 2
    CHASE = 3

class GhostColor(Enum):
    RED = 0
    PINK = 1
    CYAN = 2
    ORANGE = 3
