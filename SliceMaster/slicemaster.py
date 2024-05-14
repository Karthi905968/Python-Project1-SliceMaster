import pygame
import os
import random
import asyncio

player_lives = 3                                                # Keep track of lives
score = 0                                                       # Keeps track of score
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb']    # Entities in the game

# Initialize pygame and create window
WIDTH = 800
HEIGHT = 500
FPS = 12                                                 # Controls how often the gameDisplay should refresh. In our case, it will refresh every 1/12th second
pygame.init()
pygame.display.set_caption('SliceMaster')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))   # Setting game display size
clock = pygame.time.Clock()

# Define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

background = pygame.image.load('images/background.png')                                  # Game background
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))    # Score display
lives_icon = pygame.image.load('images/white_lives.png')                    # Images that shows remaining lives

#load sounds
pygame.mixer.music.load('images/game-music-loop.mp3')
pygame.mixer.music.play(-1,0.0,5000)

slice_sound = pygame.mixer.Sound('images/fruit-cut.mp3')
explosion_sound = pygame.mixer.Sound('images/bomb-blast.mp3')
game_over_sound = pygame.mixer.Sound('images/game-over.wav')


# Generalized structure of the fruit Dictionary
def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x' : random.randint(100,500),          # Where the fruit should be positioned on x-coordinate
        'y' : 800,
        'speed_x': random.randint(-10,10),      # How fast the fruit should move in x direction. Controls the diagonal movement of fruits
        'speed_y': random.randint(-80, -60),    # Control the speed of fruits in y-directionn ( UP )
        'throw': False,                         # Determines if the generated coordinate of the fruits is outside the gameDisplay or not. If outside, then it will be discarded
        't': 0,                                 # Manages the
        'hit': False,
    }

    if random.random() >= 0.75:     # Return the next random floating point number in the range [0.0, 1.0) to keep the fruits inside the gameDisplay
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False

# Dictionary to hold the data the random fruit generation
data = {}
for fruit in fruits:
    generate_random_fruits(fruit)

def hide_cross_lives(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))

# Generic method to draw fonts on the screen
font_name = pygame.font.match_font('comic.ttf')
def draw_text(display, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)

# Draw players lives
def draw_lives(display, x, y, lives, image) :
    for i in range(lives) :
        img = pygame.image.load(image)
        img_rect = img.get_rect()       # Gets the (x,y) coordinates of the cross icons (lives on the the top rightmost side)
        img_rect.x = int(x + 35 * i)    # Sets the next cross icon 35pixels awt from the previous one
        img_rect.y = y                  # Takes care of how many pixels the cross icon should be positioned from top of the screen
        display.blit(img, img_rect)

# Show game over display & front display
def show_gameover_screen():
    gameDisplay.blit(background, (0,0))
    draw_text(gameDisplay, "SLICE MASTER!", 90, WIDTH / 2, HEIGHT / 4)
    draw_text(gameDisplay, "Score : " + str(score), 50, WIDTH / 2, HEIGHT / 2)
    draw_text(gameDisplay, "Press a key to begin!", 64, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Game Loop
first_round = True
game_over = True        # Terminates the game While loop if more than 3-Bombs are cut
game_running = True     # Used to manage the game loop

async def main():
    global first_round,game_over,game_running,score_text,score
    
    while game_running :
        if game_over :
            if first_round :
                show_gameover_screen()
                first_round = False
            game_over = False
            player_lives = 3
            score = 0
            draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

        for event in pygame.event.get():
            # Checking for closing window
            if event.type == pygame.QUIT:
                game_running = False

        gameDisplay.blit(background, (0, 0))
        score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
        gameDisplay.blit(score_text, (0, 0))
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

        for key, value in data.items():
            if value['throw']:
                value['x'] += value['speed_x']          # Moving the fruits in x-coordinates
                value['y'] += value['speed_y']          # Moving the fruits in y-coordinate
                value['speed_y'] += (1 * value['t'])    # Increasing y-corrdinate
                value['t'] += 1                         # Increasing speed_y for next loop

                if value['y'] <= 800:
                    gameDisplay.blit(value['img'], (value['x'], value['y']))    # Displaying the fruit inside screen dynamically
                else:
                    generate_random_fruits(key)

                current_position = pygame.mouse.get_pos()   # Gets the current coordinate (x, y) in pixels of the mouse

                if not value['hit'] and current_position[0] > value['x'] and current_position[0] < value['x']+60 \
                        and current_position[1] > value['y'] and current_position[1] < value['y']+60:
                    if key == 'bomb':
                        player_lives -= 1
                        if player_lives == 0:
                            hide_cross_lives(690, 15)
                        elif player_lives == 1 :
                            hide_cross_lives(725, 15)
                        elif player_lives == 2 :
                            hide_cross_lives(760, 15)
                        # If the user clicks bombs for three times, GAME OVER message should be displayed and the window should be reset
                        if player_lives < 0 :
                            game_over_sound.play()
                            show_gameover_screen()
                            game_over = True

                        half_fruit_path = "images/explosion.png"
                        explosion_sound.play()
                    else:
                        half_fruit_path = "images/" + "half_" + key + ".png"
                        slice_sound.play()

                    value['img'] = pygame.image.load(half_fruit_path)
                    value['speed_x'] += 10
                    if key != 'bomb' :
                        score += 1
                    value['hit'] = True
            else:
                generate_random_fruits(key)

        pygame.display.update()
        clock.tick(FPS)      # Keep loop running at the right speed (manages the frame/second. The loop should update after every 1/12th pf the sec
        await asyncio.sleep(0)

asyncio.run(main())

