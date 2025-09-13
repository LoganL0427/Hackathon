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
state = "MENU"
INFO_BAR_HEIGHT = 40

# Colors
BLACK = (10, 10, 10)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)

def draw_menu():
    font = pygame.font.SysFont(None, 74)
    title = font.render("Neon Hacker", True, NEON_BLUE)
    subtitle = pygame.font.SysFont(None, 36).render("Press SPACE to Start", True, NEON_PINK)
    screen.fill(BLACK)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 3))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(60)

def draw_pause():
    font = pygame.font.SysFont(None, 74)
    pause_text = font.render("Paused", True, NEON_PINK)
    subtitle = pygame.font.SysFont(None, 36).render("ENTER to Resume, ESC for Menu", True, NEON_BLUE)
    screen.fill(BLACK)
    screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 2))
    pygame.display.flip()

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
            new_x = self.rect.x + step_x
            if 0 <= new_x <= WIDTH - TILE and not self.collide(step_x, 0):
                self.rect.x = new_x
            else:
                break  # stop at wall

        # move along y axis
        for _ in range(abs(dy)):
            new_y = self.rect.y + step_y
            if 0 <= new_y <= HEIGHT - TILE - INFO_BAR_HEIGHT and not self.collide(0, step_y):
                self.rect.y = new_y
            else:
                break

    # def move(self, dx, dy):
    #     new_x = self.rect.x + dx
    #     new_y = self.rect.y + dy
    #     # Fix bottom boundary to account for info bar
    #     if 0 <= new_x <= WIDTH - TILE and 0 <= new_y <= HEIGHT - TILE - INFO_BAR_HEIGHT:
    #         if not self.collide(dx, dy):
    #             self.rect.x = new_x
    #             self.rect.y = new_y

    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.move(0, INFO_BAR_HEIGHT).colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        color = NEON_BLUE
        rect_draw = self.rect.copy()
        rect_draw.y += INFO_BAR_HEIGHT
        pygame.draw.rect(screen, color, rect_draw)

class Enemy:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = speed
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def update(self):
        dx, dy = self.direction[0]*self.speed, self.direction[1]*self.speed
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        # Fix bottom boundary to account for info bar
        if 0 <= new_x <= WIDTH - TILE and 0 <= new_y <= HEIGHT - TILE - INFO_BAR_HEIGHT:
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
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.move(0, INFO_BAR_HEIGHT).colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        rect_draw = self.rect.copy()
        rect_draw.y += INFO_BAR_HEIGHT
        pygame.draw.rect(screen, NEON_PINK, rect_draw)

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
            x, y = c*TILE, r*TILE + INFO_BAR_HEIGHT
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
    visited.add(start)
    
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if (0 <= nr < rows and 0 <= nc < cols and 
                maze[nr][nc] == 0 and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return visited
# --- Add Power-ups Functions -----

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
def reset_maze(num_enemies=1):
    global maze, player, enemies, goal_rect, goal_row, goal_col, powerups
    
    # Generate new maze
    maze = make_maze(rows, cols)
    add_loops(maze, extra_paths=10)

    # Ensure player start is always free
    maze[1][1] = 0

    # Enforce borders
    for r in range(rows):
        maze[r][0] = maze[r][cols-1] = 1
    for c in range(cols):
        maze[0][c] = maze[rows-1][c] = 1

    # Clear any existing goals first
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 9:
                maze[r][c] = 0

    # Find reachable tiles and place goal
    reachable = get_reachable_tiles(maze, (1, 1))
    valid_tiles = [pos for pos in reachable if pos != (1, 1)]
    
    if valid_tiles:
        goal_row, goal_col = random.choice(valid_tiles)
        maze[goal_row][goal_col] = 9
        # Set goal_rect position to match player coordinate system (without INFO_BAR_HEIGHT)
        goal_rect.x = goal_col * TILE
        goal_rect.y = goal_row * TILE
        print(f"Goal placed at maze[{goal_row}][{goal_col}], rect at ({goal_rect.x}, {goal_rect.y})")
    else:
        # Fallback - this should rarely happen
        goal_row, goal_col = 1, 2
        if maze[goal_row][goal_col] == 0:
            maze[goal_row][goal_col] = 9
        goal_rect.x = goal_col * TILE
        goal_rect.y = goal_row * TILE
        print(f"Fallback goal placed at maze[{goal_row}][{goal_col}], rect at ({goal_rect.x}, {goal_rect.y})")

    # Reset player position
    player.rect.x = TILE
    player.rect.y = TILE

    # Reset enemies
    enemies.clear()
    for _ in range(num_enemies):
        # Find free tiles that aren't the player start or goal
        free_tiles = [(r, c) for r in range(1, rows-1) for c in range(1, cols-1)
                      if maze[r][c] == 0 and (r, c) != (1, 1) and (r, c) != (goal_row, goal_col)]
        if free_tiles:
            er, ec = random.choice(free_tiles)
        else:
            # Fallback enemy position
            er, ec = 3, 3
            if maze[er][ec] != 0:
                maze[er][ec] = 0  # Force it to be walkable
        enemies.append(Enemy(ec*TILE, er*TILE, enemy_speed))  

    # --- Power-Up Cleanup ---
    for pu in powerups:
        # Check if the power-up has a reset method
        if hasattr(pu, 'reset'):
            pu.reset()

    # --- Power-Ups ---
    powerups.clear()  # clear old power-ups

    # future fix: maybe we choose a certain power-up to appear at random
    powerups.append(spawn_speed_boost())  # spawn one new speed boost
    powerups.append(spawn_enemy_slow())  # spawn slow-down power-up


# --- Initialization ---
rows, cols = (HEIGHT - INFO_BAR_HEIGHT)//TILE, WIDTH//TILE
enemy_speed = 2
player = Player(TILE, TILE)
enemies = []
goal_rect = pygame.Rect(0, 0, TILE, TILE)
goal_row, goal_col = 0, 0
level = 1
score = 0
glow_timer = 0
powerups = []
reset_maze(1)

# --- Main Loop ---
running = True
while running:
    if state == "MENU":
        draw_menu()
        state = "PLAYING"
        reset_maze(1)
    dt = 1/30
    events = list(pygame.event.get())
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    if state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-player.speed,0)
        if keys[pygame.K_RIGHT]: player.move(player.speed,0)
        if keys[pygame.K_UP]: player.move(0,-player.speed)
        if keys[pygame.K_DOWN]: player.move(0,player.speed)
        for enemy in enemies:
            enemy.update()
        
        # Check goal collision
        if player.rect.colliderect(goal_rect):
            print(f"Goal reached! Player at ({player.rect.x}, {player.rect.y}), Goal at ({goal_rect.x}, {goal_rect.y})")
            level += 1
            enemy_speed += 1
            num_enemies = 1 + (level // 3)
            reset_maze(num_enemies)
            score += 1
            
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                enemies.clear()
                level = 1
                enemy_speed = 2
                score = 0
                reset_maze(1)
                player = Player(TILE, TILE)
                break

        # --- Power-Up Collision & Update ---
        for pu in powerups:
            if player.rect.colliderect(pu.rect) and not pu.active:
                pu.apply(player, enemies)
            pu.update(player, enemies)

        screen.fill(BLACK)
        # Draw info bar at the top
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Level: {level} | Enemy Speed: {enemy_speed} | Score: {score}", True, NEON_BLUE)
        screen.blit(text, (10, 5))

        draw_maze()
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for pu in powerups:    
            pu.draw(screen)



    elif state == "PAUSED":
        draw_pause()
    # Handle menu/escape logic using the same event list
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif state == 'PLAYING' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = 'PAUSED'
        elif state == 'PAUSED' and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            state = 'PLAYING'
        elif state == 'PAUSED' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = 'MENU'
            draw_menu()
            reset_maze(1)
    pygame.display.flip()
    clock.tick(30)
    glow_timer += 0.1
