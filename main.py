from curses import KEY_DOWN, KEY_LEFT
import pygame
import random

pygame.font.init()

# global variables
window_width = 800
window_height = 700
grid_width = 300
grid_height = 600
block_size = 30

title_font_size = 45
text_font_size = 20
default_font = 'courier'

rows = 20
columns = 10

top_left_x = (window_width - grid_width) // 2
top_left_y = (window_height - grid_height) // 1.25

# shapes
S = [['.....', 
      '.....', 
      '..00.',
      '.00..',
      '.....'],
     ['.....', 
      '.0...', 
      '.00..',
      '..0..',
      '.....']]

Z = [['.....', 
      '.....', 
      '.00..',
      '..00.',
      '.....'],
     ['.....', 
      '...0.', 
      '..00.',
      '..0..',
      '.....']]

I = [['..0..', 
      '..0..', 
      '..0..',
      '..0..',
      '.....'],
     ['.....', 
      '0000.', 
      '.....',
      '.....',
      '.....']]

O = [['.....', 
      '.....', 
      '.00..',
      '.00..',
      '.....']]

J = [['.....', 
      '..0..', 
      '..0..',
      '.00..',
      '.....'],
     ['.....', 
      '.0...', 
      '.000.',
      '.....',
      '.....'],
     ['.....', 
      '..00.', 
      '..0..',
      '..0..',
      '.....'],
     ['.....', 
      '.....', 
      '.000.',
      '...0.',
      '.....']]

L = [['.....', 
      '..0..', 
      '..0..',
      '..00.',
      '.....'],
     ['.....', 
      '.....', 
      '.000.',
      '.0...',
      '.....'],
     ['.....', 
      '.00..', 
      '..0..',
      '..0..',
      '.....'],
     ['.....', 
      '...0.', 
      '.000.',
      '.....',
      '.....']]

T = [['.....', 
      '.....', 
      '.000.',
      '..0..',
      '.....'],
     ['.....', 
      '..0..', 
      '.00..',
      '..0..',
      '.....'],
     ['.....', 
      '..0..', 
      '.000.',
      '.....',
      '.....'],
     ['.....', 
      '..0..', 
      '..00.',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0 , 0), (102, 241, 255), (255, 255, 102), (55, 116, 255), (255, 189, 60), (175, 53, 255)]

class Piece(object):
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0 #number from 0 to 3

# creates tuple (r,g,b) for each grid space in the column x row grid space
def create_grid(locked_pos = {}):
    grid = [[(0,0,0) for _ in range(columns)] for _ in range(rows)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos: 
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
        
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    
    return positions

def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(columns) if grid[i][j] == (0, 0, 0)] for i in range(rows)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

# check if shapes surpassed top of grid
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

# generates a random shape at top middle of grid space
def get_shape():
    return Piece(5, 0, random.choice(shapes))

# helper function for text
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont(default_font, size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + grid_width/2 - 
    (label.get_width()/2), top_left_y + grid_height/2 - (label.get_height()/2) - 100))

def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i*block_size), (sx + grid_width, sy + i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy), (sx + j*block_size, sy + grid_height))

# clears rows by moving entire grid down and added new rows
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i] 
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except: 
                    continue
    
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    
    return inc

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont(default_font, text_font_size)
    label = font.render('next:', 1, (255, 255, 255))

    sx = top_left_x + grid_width + 30
    sy = top_left_y + grid_height/2 - 250
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0) 
    surface.blit(label, (sx, sy - 27))

def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()
    return score

# draws out the main game ui
def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont(default_font, title_font_size)
    label = font.render('t e t r i s', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + grid_width / 2 - (label.get_width() / 2), 15))

    # current score
    font = pygame.font.SysFont(default_font, text_font_size)
    label = font.render('score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + grid_width + 30
    sy = top_left_y + grid_height/2 - 100

    surface.blit(label, (sx, sy + 160))

    # last score 
    label = font.render('high score: ' + last_score, 1, (255, 255, 255))

    sx = top_left_x - 180

    surface.blit(label, (sx, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)
    
    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y, grid_width, grid_height), 3)
    draw_grid(surface, grid)

# helper to completely clear window when lost
def clear_window(surface):
    surface.fill((0, 0, 0))

def main(window):
    global grid

    last_score = max_score()
    locked_positions = {} 
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.2
    level_time = 0
    score = 0

    while run: 
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time/1000 > 5: 
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # *** please find a better way to do this lol
        if score == 10:
            fall_speed = 0.16
        elif score == 20:
            fall_speed = 0.12
        elif score == 30: 
            fall_speed = 0.08

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                
            if event.type == pygame.KEYDOWN:
                # move left one block
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                # move right one block
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                # rotate
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                # slow drop
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                # *** hard drop - need to fix 
                elif event.key == pygame.K_SPACE:
                    current_piece.y = 20
                    while not valid_space(current_piece, grid):
                        current_piece.y -= 1
    
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            # change if moving grid
            if y > -1:
                grid[y][x] = current_piece.color
    
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions)

            clear_rows(grid, locked_positions)

        draw_window(window, grid, score, last_score)

        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            clear_window(window)
            draw_text_middle(window, "you lost :(", text_font_size, (255, 255, 255))

            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)

# first window that shows, leads to main game upon keydown event 
def main_menu(window): 
    run = True
    while run: 
        window.fill((0, 0, 0))
        draw_text_middle(window, "press any key to play", text_font_size, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(window)
    
    pygame.display.quit()

window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Tetris')

main_menu(window)