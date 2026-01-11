# pong.py
# Copyright 2025 Havoc Crenshaw
# Licensed under the MIT License (See LICENSE)

# Something important about the architecture of this app is the lack of
# extensibility regarding the game objects. Yes, you have to pass the players
# and ball everywhere. But, by golly, does it save a lot of unnecessary typing
# for what is only Pong, and has nothing more than two players and a ball.

from enum import Enum
import os
import random

import pygame
import pygame.freetype

# TODO: Clean up (one day.) (never)

# Constants
WINDOW_TITLE = 'PYPONG'

# Change to whatever reasonable. 4:3 is the recommended experience.
# 16:9 is acceptable. 10:1 is not.
SCREEN_WIDTH, SCREEN_HEIGHT = 1024,768
DIMENSIONS = (SCREEN_WIDTH, SCREEN_HEIGHT)

BIG_FONT_SIZE = SCREEN_HEIGHT * 1/10
SMALL_FONT_SIZE = SCREEN_HEIGHT * 1/27

ELEMENT_WIDTH = SCREEN_WIDTH * 1/75 # Just looks good
PADDLE_WIDTH = ELEMENT_WIDTH
PADDLE_HEIGHT = SCREEN_HEIGHT * 1/10
BALL_RADIUS = ELEMENT_WIDTH
BORDER_WIDTH = ELEMENT_WIDTH * 2

NUM_CENTER_DOTS = 15
CENTER_DOT_PADDING = SCREEN_HEIGHT * 1/40
CENTER_DOT_WIDTH = ELEMENT_WIDTH * 3/4

MOV_INC = SCREEN_HEIGHT * 7/10
BALL_SPEED = SCREEN_WIDTH * 7/10

OPENING_PLAY = 1 # In seconds

COLOR_WHITE = (230, 230, 230) # Not true white, makes the palette better on light mode

# Variables
text_size_cache = {}
sound_cache = {}

class GameState(Enum):
    START = 0
    RUNNING = 1
    END = 2

class Input(Enum):
    P1_UP = 0
    P1_DOWN = 1
    P2_UP = 2
    P2_DOWN = 3

class Game(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Game, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'running'):
            self.running = True
        if not hasattr(self, 'state'):
            self.state = GameState.START
        if not hasattr(self, 'timer'):
            self.timer = 0.0
        if not hasattr(self, 'dt'):
            self.dt = 0.0
        if not hasattr(self, 'winner'):
            self.winner = 0

class Player(object):
    def __init__(self):
        self.y = (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2)
        self.score = 0

class Ball(object):
    def __init__(self):
        self.init()

    # Not to be confused with the preeminent __init__. Sets the `x` and `y` to
    # zero and randomly sets the starting direction.
    def init(self):
        self.x = (SCREEN_WIDTH / 2) - (BALL_RADIUS / 2)
        self.y = (SCREEN_HEIGHT / 2) - (BALL_RADIUS / 2)

        left = random.randint(0, 1)
        if left:
            self.vel_x = -(BALL_SPEED * 3/4)
        else:
            self.vel_x = (BALL_SPEED * 3/4)

        up = random.randint(0, 1)
        if up:
            self.vel_y = -(BALL_SPEED * 1/4)
        else:
            self.vel_y = (BALL_SPEED * 1/4)

        self.in_play = False

def init():
    game = Game()

    random.seed()

    root_dir = os.path.dirname(__file__)
    icon = pygame.image.load(os.path.join(root_dir, 'icon.png'))
    pygame.display.init()
    pygame.freetype.init()
    pygame.mixer.init()
    pygame.display.set_caption(WINDOW_TITLE)
    pygame.display.set_icon(icon)
    game.window = pygame.display.set_mode(DIMENSIONS)
    game.clock = pygame.time.Clock()

def get_sound(sound_name: str) -> pygame.mixer.Sound:
    if not sound_name in sound_cache:
        root_dir = os.path.dirname(__file__)
        sound = pygame.mixer.Sound(os.path.join(root_dir, f'{sound_name}.wav'))
        sound_cache[sound_name] = sound

    return sound_cache[sound_name]

def process_events(game: Game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        if event.type == pygame.KEYDOWN:
            if game.state == GameState.START:
                game.state = GameState.RUNNING
            if game.state == GameState.END:
                if event.key == pygame.K_SPACE:
                    game.state = GameState.START
                    sound = get_sound('start')
                    sound.play()

def collide_borders(ball: Ball):
    top_border_y = BORDER_WIDTH
    bottom_border_y = SCREEN_HEIGHT - (BALL_RADIUS + BORDER_WIDTH)
    if ball.y <= top_border_y or ball.y >= bottom_border_y:
        ball.vel_y = -ball.vel_y
        sound = get_sound('hit')
        sound.play()

    # Push the ball a little bit away from the border, prevents the ball from
    # being captured.
    if ball.y <= top_border_y:
        ball.y += ELEMENT_WIDTH
    if ball.y >= bottom_border_y:
        ball.y -= ELEMENT_WIDTH

def collide_goals(p1: Player, p2: Player, ball: Ball):
    if ball.x >= SCREEN_WIDTH:
        p1.score += 1
        game = Game()
        if (p1.score == 10):
            game.state = GameState.END
            sound = get_sound('end')
            sound.play()
            p1.__init__()
            p2.__init__()
            game.winner = 1
        else:
            sound = get_sound('goal')
            sound.play()
        ball.init()
        game.timer = 0.0
        return

    if ball.x <= 0:
        p2.score += 1
        game = Game()
        if (p2.score == 10):
            game.state = GameState.END    
            sound = get_sound('end')
            sound.play()
            p1.__init__()
            p2.__init__()
            game.winner = 2
        else:
            sound = get_sound('goal')
            sound.play()
        ball.init()
        game.timer = 0.0
        return

def collide_plr(plr: Player, ball: Ball):
    paddle_middle_point = plr.y + (PADDLE_HEIGHT / 2)
    ball_middle_point = ball.y + (BALL_RADIUS / 2)

    # Subtract the paddle from the ball middle point so if the paddle is
    # below the ball instead of getting a positive integer, you get
    # a negative integer (upwards being -y)
    difference = ball_middle_point - paddle_middle_point

    # Hack because if statements are slow, instead of multiple, just one
    desired_speed_increase = BALL_SPEED - abs(ball.vel_x)
    if -ball.vel_x < 0:
        desired_speed_increase = -desired_speed_increase
    ball.vel_x = -ball.vel_x + desired_speed_increase
    game = Game()

    # Push the ball a little bit away from the paddle, prevents the ball from
    # being captured.
    if plr.x < SCREEN_WIDTH / 2:
        ball.x = plr.x + (ELEMENT_WIDTH * 2)
    if plr.x > SCREEN_WIDTH / 2:
        ball.x = plr.x - (ELEMENT_WIDTH * 2)

    # Convert the difference to a percentage
    ball.vel_y = BALL_SPEED * (difference / PADDLE_HEIGHT)

    sound = get_sound('hit')
    sound.play()

def collisions(p1: Player, p2: Player, ball: Ball):
    p1_hit = pygame.Rect(p1.x, p1.y, PADDLE_WIDTH, PADDLE_HEIGHT)
    p2_hit = pygame.Rect(p2.x, p2.y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_hit = pygame.Rect(ball.x, ball.y, BALL_RADIUS, BALL_RADIUS)

    collide_borders(ball)
    collide_goals(p1, p2, ball)

    p1_collided = ball_hit.colliderect(p1_hit)
    if p1_collided:
        collide_plr(p1, ball)
        return

    p2_collided = ball_hit.colliderect(p2_hit)
    if p2_collided:
        collide_plr(p2, ball)
        return

def update(game: Game, p1: Player, p2: Player, ball: Ball):
    if game.state == GameState.RUNNING:
        game.timer += game.dt
        keys = pygame.key.get_pressed()

        margin = 1 # Remove x pixels to make the paddles sit on the bottom border
        max_y = SCREEN_HEIGHT - (PADDLE_HEIGHT + BORDER_WIDTH - margin)
        min_y = BORDER_WIDTH

        if keys[pygame.K_w]:
            if p1.y > min_y:
                p1.y -= MOV_INC * game.dt
        if keys[pygame.K_s]:
            if p1.y < max_y:
                p1.y += MOV_INC * game.dt
        if keys[pygame.K_UP]:
            if p2.y > min_y:
                p2.y -= MOV_INC * game.dt
        if keys[pygame.K_DOWN]:
            if p2.y < max_y:
                p2.y += MOV_INC * game.dt

        collisions(p1, p2, ball)

        if ball.in_play:
            ball.x += ball.vel_x * game.dt
            ball.y += ball.vel_y * game.dt
        else:
            if game.timer > OPENING_PLAY:
                ball.in_play = True

# Cannot handle multiple characters of white space or special characters
def get_total_text_width(font: pygame.freetype.Font, text: str) -> int:
    metrics = font.get_metrics(text)

    total_width = 0
    for char_metrics in metrics:
        total_width += char_metrics[4] # Add the `horizontal_advance_x` of a single character

    return total_width

def render_start(game: Game, big_font: pygame.freetype.Font,
                 small_font: pygame.freetype.Font):
        start_text = 'Press any key to start'
        guide1_text = 'P1: W / S'
        guide2_text = 'P2: Up / Down'
        guide3_text = 'First to ten wins!'

        # Calculate the sizes only once. Checking for each particular key
        # instead of just `not text_size_cache` to encourage further usage of
        # the cache.
        if not 'title' in text_size_cache:
            total_width = get_total_text_width(big_font, WINDOW_TITLE)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT / 10
            text_size_cache['title'] = (x, y)

        if not 'start' in text_size_cache:
            total_width = get_total_text_width(small_font, start_text)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT * 6/10
            text_size_cache['start'] = (x, y)

        if not 'guide1' in text_size_cache:
            x = SCREEN_WIDTH * 1/10
            y = SCREEN_HEIGHT * 7/10
            text_size_cache['guide1'] = (x, y)

        if not 'guide2' in text_size_cache:
            total_width = get_total_text_width(small_font, guide2_text)
            x = (SCREEN_WIDTH * 9/10) - total_width
            y = SCREEN_HEIGHT * 7/10
            text_size_cache['guide2'] = (x, y)

        if not 'guide3' in text_size_cache:
            total_width = get_total_text_width(small_font, guide3_text)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT * 8/10
            text_size_cache['guide3'] = (x, y)

        big_font.render_to(game.window, text_size_cache['title'],
                           WINDOW_TITLE, COLOR_WHITE)
        small_font.render_to(game.window, text_size_cache['start'],
                             start_text, COLOR_WHITE)
        small_font.render_to(game.window, text_size_cache['guide1'],
                             guide1_text, COLOR_WHITE)
        small_font.render_to(game.window, text_size_cache['guide2'],
                             guide2_text, COLOR_WHITE)
        small_font.render_to(game.window, text_size_cache['guide3'],
                             guide3_text, COLOR_WHITE)

def render_running(game: Game, big_font: pygame.freetype.Font, p1: Player,
                   p2: Player, ball: Ball):
    pygame.draw.rect(game.window, COLOR_WHITE,
                     (p1.x, p1.y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(game.window, COLOR_WHITE,
                     (p2.x, p2.y, PADDLE_WIDTH, PADDLE_HEIGHT))
    if ball.in_play:
        pygame.draw.rect(game.window, COLOR_WHITE,
                         (ball.x, ball.y, BALL_RADIUS, BALL_RADIUS))

    # Top/bottom borders
    pygame.draw.rect(game.window, COLOR_WHITE,
                     (0, 0, SCREEN_WIDTH, ELEMENT_WIDTH * 2))
    pygame.draw.rect(game.window, COLOR_WHITE,
                     (0, SCREEN_HEIGHT - ELEMENT_WIDTH * 2,
                      SCREEN_WIDTH, ELEMENT_WIDTH * 2))

    # Center line (AGH IT'S UGLY DON'T LOOK AT ME!)
    working_area = SCREEN_HEIGHT - (BORDER_WIDTH * 2) - (CENTER_DOT_PADDING)
    dot_len = (working_area / NUM_CENTER_DOTS) - CENTER_DOT_PADDING
    for i in range(NUM_CENTER_DOTS):
        y = i * (working_area / NUM_CENTER_DOTS) + BORDER_WIDTH + CENTER_DOT_PADDING
        pygame.draw.rect(game.window, COLOR_WHITE,
                         ((SCREEN_WIDTH / 2) - (CENTER_DOT_WIDTH / 2),
                          y, CENTER_DOT_WIDTH, dot_len))

    if not 'score1' in text_size_cache:
        padding = SCREEN_WIDTH * 1/10
        total_width = get_total_text_width(big_font, '0')
        x = (SCREEN_WIDTH / 2) - (total_width + padding)
        y = SCREEN_HEIGHT * 1/10
        text_size_cache['score1'] = (x, y)

    if not 'score2' in text_size_cache:
        padding = SCREEN_WIDTH * 1/10
        total_width = get_total_text_width(big_font, '0')
        x = (SCREEN_WIDTH / 2) + padding
        y = SCREEN_HEIGHT * 1/10
        text_size_cache['score2'] = (x, y)

    big_font.render_to(game.window, text_size_cache['score1'], str(p1.score),
                       COLOR_WHITE)
    big_font.render_to(game.window, text_size_cache['score2'], str(p2.score),
                       COLOR_WHITE)

def render_end(game: Game, big_font: pygame.freetype.Font,
               small_font: pygame.freetype.Font):
        end_text = 'Game Over'
        p1_won = 'Player 1 won!'
        p2_won = 'Player 2 won!'
        restart_text = 'Press space to restart'

        if not 'end_text' in text_size_cache:
            total_width = get_total_text_width(big_font, end_text)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT / 10
            text_size_cache['end_text'] = (x, y)

        if not 'p1_won' in text_size_cache:
            total_width = get_total_text_width(small_font, p1_won)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT / 2
            text_size_cache['p1_won'] = (x, y)

        if not 'p2_won' in text_size_cache:
            total_width = get_total_text_width(small_font, p2_won)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT / 2
            text_size_cache['p2_won'] = (x, y)

        if not 'restart' in text_size_cache:
            total_width = get_total_text_width(small_font, restart_text)
            x = (SCREEN_WIDTH / 2) - (total_width / 2)
            y = SCREEN_HEIGHT * 6/10
            text_size_cache['restart'] = (x, y)

        big_font.render_to(game.window, text_size_cache['end_text'],
                           end_text, COLOR_WHITE)
        if game.winner == 1:
            small_font.render_to(game.window, text_size_cache['p1_won'],
                                 p1_won, COLOR_WHITE)
        elif game.winner == 2:
            small_font.render_to(game.window, text_size_cache['p2_won'],
                                 p2_won, COLOR_WHITE)
        small_font.render_to(game.window, text_size_cache['restart'],
                             restart_text, COLOR_WHITE)

def render(game: Game, big_font: pygame.freetype.Font,
           small_font: pygame.freetype.Font, p1: Player, p2: Player,
           ball: Ball):
    game.window.fill('black')

    if game.state == GameState.START:
        render_start(game, big_font, small_font)
    elif game.state == GameState.RUNNING:
        render_running(game, big_font, p1, p2, ball)
    else:
        # Must be `GameState.END`.
        render_end(game, big_font, small_font)

def main() -> int:
    init()

    # Prevent instatiating these every frame.
    game = Game()
    big_font = pygame.freetype.Font('arcade.ttf', BIG_FONT_SIZE)
    small_font = pygame.freetype.Font('arcade.ttf', SMALL_FONT_SIZE)

    # Game objects
    p1 = Player()
    p1.x = ELEMENT_WIDTH * 5
    p2 = Player()
    p2.x = SCREEN_WIDTH - (PADDLE_WIDTH + (ELEMENT_WIDTH * 5))
    ball = Ball()

    sound = get_sound('start')
    sound.play()

    while game.running:
        process_events(game)
        update(game, p1, p2, ball)
        render(game, big_font, small_font, p1, p2, ball)
        pygame.display.flip()

        # Convert ms (return of `.tick()`) to seconds (16ms vs 0.016s)
        game.dt = game.clock.tick() / 1000

if __name__ == '__main__':
    main()
