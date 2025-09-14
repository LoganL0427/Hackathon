#!/usr/bin/env python3

import pygame, sys, random, math, collections
from powerups.speed import SpeedBoost
from powerups.slow import EnemySlow


# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Hacker")
clock = pygame.time.Clock()

# Colors
BLACK = (10, 10, 10)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)

# --- Maze Generation ---
def make_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve(r, c):
        directions = [(0,2),(0,-2),(2,0),(-2,0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[r + dr//2][c + dc//2] = 0  # remove wall in between
                maze[nr][nc] = 0
                carve(nr, nc)

    maze[1][1] = 0
    carve(1, 1)

    return maze

def add_loops(maze, extra_paths=8):
    rows, cols = len(maze), len(maze[0])
    for _ in range(extra_paths):
        r = random.randrange(1, rows-1, 2)
        c = random.randrange(1, cols-1, 2)
        neighbors = []
        if maze[r-1][c] == 1: neighbors.append((r-1,c))
        if maze[r+1][c] == 1: neighbors.append((r+1,c))
        if maze[r][c-1] == 1: neighbors.append((r,c-1))
        if maze[r][c+1] == 1: neighbors.append((r,c+1))
        if neighbors:
            nr, nc = random.choice(neighbors)
            maze[nr][nc] = 0

# --- Entities ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = 4

    def move(self, dx, dy):
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        # move along x axis
        for _ in range(abs(dx)):
            if not self.collide(step_x, 0):
                self.rect.x += step_x
            else:
                break  # stop at wall

        # move along y axis
        for _ in range(abs(dy)):
            if not self.collide(0, step_y):
                self.rect.y += step_y
            else:
                break

    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        color = NEON_BLUE
        pygame.draw.rect(screen, color, self.rect)

class Enemy:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = speed
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def update(self):
        dx, dy = self.direction[0]*self.speed, self.direction[1]*self.speed
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        # Allow movement up to the last tile
        if 0 <= new_x <= WIDTH - TILE and 0 <= new_y <= HEIGHT - TILE:
            if not self.collide(dx, dy):
                self.rect.x = new_x
                self.rect.y = new_y
            else:
                self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        else:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        pygame.draw.rect(screen, NEON_PINK, self.rect)

# --- Goal & Maze Drawing ---
def find_farthest_free_tile(maze, player_pos):
    rows, cols = len(maze), len(maze[0])
    free_tiles = []
    py, px = player_pos
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0 and (r, c) != player_pos:  # Exclude player start
                free_tiles.append((r, c))
    # sort by Manhattan distance
    free_tiles.sort(key=lambda t: abs(t[0]-py) + abs(t[1]-px), reverse=True)
    return free_tiles[0] if free_tiles else (1,2)  # fallback to a nearby tile

def draw_maze():
    for r in range(len(maze)):
        for c in range(len(maze[r])):
            x, y = c*TILE, r*TILE
            if maze[r][c] == 1:
                pygame.draw.rect(screen, NEON_GREEN, (x, y, TILE, TILE), 2)
            elif maze[r][c] == 9:
                pygame.draw.rect(screen, (138, 43, 226), (x, y, TILE, TILE))
                glow_size = int(3 + 2 * abs(math.sin(glow_timer)))
                pygame.draw.rect(screen, (255,0,255), (x, y, TILE, TILE), glow_size)

def get_reachable_tiles(maze, start):
    rows, cols = len(maze), len(maze[0])
    visited = set()
    queue = collections.deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                queue.append((nr, nc))
    return visited


def spawn_speed_boost():
    # Collect all empty tiles in the maze
    free_tiles = [(r, c) for r in range(len(maze)) for c in range(len(maze[0])) if maze[r][c] == 0]
    
    # Pick a random free tile
    r, c = random.choice(free_tiles)
    
    # Return a new SpeedBoost object at that tile
    return SpeedBoost(c * TILE, r * TILE, TILE)

def spawn_enemy_slow():
    free_tiles = [(r, c) for r in range(len(maze)) for c in range(len(maze[0])) if maze[r][c] == 0]
    r, c = random.choice(free_tiles)
    return EnemySlow(c * TILE, r * TILE, TILE)


# --- Reset & Game State ---
def reset_maze():
    global maze, player, enemies, goal_rect, powerups
    maze = make_maze(rows, cols)
    add_loops(maze, extra_paths=10)

    # ensure player start is always free
    maze[1][1] = 0

    # enforce borders
    for r in range(rows):
        maze[r][0] = maze[r][cols-1] = 1
    for c in range(cols):
        maze[0][c] = maze[rows-1][c] = 1

    # reset player
    player.rect.x = TILE
    player.rect.y = TILE

    # reset enemies
    enemies.clear()
    enemies.append(Enemy(5*TILE, 5*TILE, enemy_speed))

    # place goal at a random reachable free tile away from player spawn
    reachable = get_reachable_tiles(maze, (1, 1))
    reachable = [pos for pos in reachable if pos != (1, 1)]
    if reachable:
        goal_row, goal_col = random.choice(list(reachable))
    else:
        goal_row, goal_col = 2, 2  # fallback
    maze[goal_row][goal_col] = 9
    goal_rect.x = goal_col*TILE
    goal_rect.y = goal_row*TILE
    
    # --- Power-Up Cleanup ---
    for pu in powerups:
        # Check if the power-up has a reset method
        if hasattr(pu, 'reset'):
            pu.reset(player)

    # --- Power-Ups ---
    powerups.clear()  # clear old power-ups

    # future fix: maybe we choose a certain power-up to appear at random
    powerups.append(spawn_speed_boost())  # spawn one new speed boost
    powerups.append(spawn_enemy_slow())  # spawn slow-down power-up


# --- Initialization ---
rows, cols = (HEIGHT//TILE)+2, (WIDTH//TILE)+2
enemy_speed = 2
player = Player(TILE, TILE)
enemies = []
goal_rect = pygame.Rect(0, 0, TILE, TILE)
level = 1
score = 0
glow_timer = 0
# --- Power-Up State ---
powerups = []  # list to hold active power-ups
reset_maze()


# --- Main Loop ---
running = True
while running:
    dt = 1/30
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.move(-player.speed,0)
    if keys[pygame.K_RIGHT]: player.move(player.speed,0)
    if keys[pygame.K_UP]: player.move(0,-player.speed)
    if keys[pygame.K_DOWN]: player.move(0,player.speed)

    # update enemies
    for enemy in enemies:
        enemy.update()

    # check win
    if player.rect.colliderect(goal_rect):
        enemies.clear()
        level += 1
        enemy_speed += 1
        reset_maze()
        score += 1
        # enemy = Enemy(TILE*5, TILE*5, enemy_speed)
        # enemies.append(enemy)
        player = Player(TILE, TILE)

    # check lose
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            enemies.clear()
            level = 1
            enemy_speed = 2
            reset_maze()
            score = 0
            player = Player(TILE, TILE)

    # --- Power-Up Collision & Update ---
    for pu in powerups:
        if player.rect.colliderect(pu.rect) and not pu.active:
            pu.apply(player, enemies)
        pu.update(player, enemies)

    # --- Draw ---
    screen.fill(BLACK)
    draw_maze()
    player.draw()
    for enemy in enemies:
        enemy.draw()
    for pu in powerups:    
        pu.draw(screen)

    # Display info
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Level: {level} | Enemy Speed: {enemy_speed} | Score: {score}", True, NEON_BLUE)
    screen.blit(text, (10,10))

    pygame.display.flip()
    clock.tick(30)
    glow_timer += 0.1
