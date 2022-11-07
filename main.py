from threading import Thread
import pygame
import time
import characters as char
import environment as env
import userevents as ue

# Basic pygame information
TARGET_FPS = 24
SCREEN_WIDTH, SCREEN_HEIGHT = (env.Map.MAP_WIDTH * env.Map.SCALING, env.Map.MAP_HEIGHT * env.Map.SCALING)
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Clone")

# Time durations for different actions
POWER_PELLET_DURATION = 5
GAME_OVER_DURATION = 5

# Resources

BG = pygame.transform.scale(
    env.Map.MAP_TEXTURE, (SCREEN_WIDTH, SCREEN_HEIGHT - env.Map.FIELD_OFFSET * env.Map.SCALING)
)

def main():
    
    clock = pygame.time.Clock()

    score = 0

    pac_man = char.PacMan(WIN, (13, 17))
    walls = env.Walls(env.Map.FIELD_OFFSET)
    pellets = env.Pellets(WIN, env.Map.FIELD_OFFSET)
    ghosts = [
        char.Ghost(WIN, (1, 1), char.GhostColor.RED, [(1, 1), (12, 1), (12, 11), (6, 11)]),
        char.Ghost(WIN, (1, 29), char.GhostColor.RED, [(1, 29), (7, 23), (12, 29)]),
        char.Ghost(WIN, (26, 1), char.GhostColor.RED, [(27-1, 29), (27-12, 1), (27-12, 11), (27-6, 11)]),
        char.Ghost(WIN, (26, 29), char.GhostColor.RED, [(27-1, 29), (27-7, 23), (27-12, 29)])
    ]
    # Function to be executed in a separate thread to make ghosts vulnerable for a short amount of time
    def make_ghosts_vulnerable():
        env.SFX.SUPER_PELLET.stop()
        env.SFX.SUPER_PELLET.play(loops=-1, maxtime = int(POWER_PELLET_DURATION * 1000))
        for ghost in ghosts:
            ghost.put_on_vulnerability()
        
        time.sleep(POWER_PELLET_DURATION)

        for ghost in ghosts:
            ghost.take_off_vulnerability()

    play_intro(pellets, walls, ghosts, pac_man)

    run = True
    
    # This sound plays constantly throughout the game 
    env.SFX.SIREN_1.play(-1)

    while run:
        clock.tick(TARGET_FPS)

        keys_pressed = pygame.key.get_pressed()

        #React to different events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == ue.UserEvents.ATE_REGULAR_PELLET:
                score += 100
            if event.type == ue.UserEvents.ATE_SUPER_PELLET:
                score += 500
                thread = Thread(target = make_ghosts_vulnerable)
                thread.start()
            if event.type == ue.UserEvents.ATE_GHOST:
                score += 1000
            if event.type == ue.UserEvents.GAME_OVER:
                env.SFX.SIREN_1.stop()
                env.SFX.DEATH_1.play()
                display_game_over()
                run = False
        
        # Drawing and character updates

        draw_window()
        pellets.draw_all()
        pac_man.update(keys_pressed, walls, pellets, ghosts)
        for ghost in ghosts:
            ghost.update(walls, pac_man)
        draw_score(score)

        pygame.display.update()

    pygame.quit()

# Debug function used to draw invisible colliders
def debug_draw_rectangles(rectangles):
    for rectangle in rectangles:
        pygame.draw.rect(WIN, (0, 255, 0), rectangle)

def play_intro(pellets, walls, ghosts, pac_man):
    draw_first_frame(pellets, walls, ghosts, pac_man)

    display_ready_message()

    env.SFX.GAME_START.play()
    time.sleep(env.SFX.GAME_START.get_length())

# Draws the first frame for the intro sequence
def draw_first_frame(pellets, walls, ghosts, pac_man):
    draw_window()
    pellets.draw_all()
    pac_man.update(pygame.key.get_pressed(), walls, pellets, ghosts)
    for ghost in ghosts:
        ghost.update(walls, pac_man)
    draw_score(0)

    pygame.display.update()

def display_ready_message():
    ready_text = env.Map.MAIN_FONT.render("READY!", 0, (255, 255, 255))
    WIN.blit(ready_text, ((SCREEN_WIDTH - ready_text.get_width())//2, (SCREEN_HEIGHT - ready_text.get_height())//2))
    pygame.display.update()

def draw_window():
    pygame.draw.rect(WIN, (0, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    WIN.blit(BG, (0, env.Map.FIELD_OFFSET*env.Map.SCALING))

def draw_score(score):
    score_text = env.Map.MAIN_FONT.render("SCORE: " + str(score), 0, (255, 255, 255))
    WIN.blit(score_text, (0, 0))

def display_game_over():
    game_over_text = env.Map.MAIN_FONT.render("GAME OVER", 0, (255, 255, 255))
    WIN.blit(game_over_text, ((SCREEN_WIDTH - game_over_text.get_width())//2, (SCREEN_HEIGHT - game_over_text.get_height())//2))
    pygame.display.update()
    time.sleep(GAME_OVER_DURATION)

if __name__ == "__main__":
    main()