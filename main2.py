#!/usr/bin/env python3

import pygame, sys, random, math, collections
from collections import deque

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Hacker")
clock = pygame.time.Clock()
state = "MENU"
INFO_BAR_HEIGHT = 40

# Colors (cyberpunk palette)
BLACK = (10, 10, 10)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)
NEON_YELLOW = (255, 255, 0)
NEON_PURPLE = (138, 43, 226)
glitch_mode = False
glitch_duration = 1.0  # seconds the glitch lasts
glitch_timer = 0       # counts down when glitch is active
glitch_cooldown = 5.0  # seconds before next glitch
cooldown_timer = 0     # counts down while waiting

# --- UI Functions ---
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

def draw_info_bar():
    # Draw info bar at the top
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Level: {level} | Enemy Speed: {enemy_speed} | Score: {score}", True, NEON_BLUE)
    screen.blit(text, (10, 5))
    draw_glitch_bar()

def draw_glitch_bar():
    # Draw glitch cooldown bar
    bar_width = 100
    bar_height = 10
    bar_x = WIDTH - bar_width - 10
    bar_y = 10

    if cooldown_timer > 0:
        fill_width = int(bar_width * (1 - cooldown_timer / glitch_cooldown))
    else:
        fill_width = bar_width

    # Bar background
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    # Bar fill
    pygame.draw.rect(screen, NEON_YELLOW, (bar_x, bar_y, fill_width, bar_height))

    # Indicate active glitch mode
    if glitch_mode:
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Label
    font = pygame.font.SysFont(None, 20)
    label = font.render("GLITCH (G)", True, NEON_YELLOW)
    screen.blit(label, (bar_x, bar_y + bar_height + 5))

# --- Maze Generation ---
def make_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    def carve(r, c):
        directions = [(0,2),(0,-2),(2,0),(-2,0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[r + dr//2][c + dc//2] = 0
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

# --- Entities ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = 4
        self.base_speed = 4
        self.glitch_used = False  # Track if glitch was used

    def move(self, dx, dy, maze):
        new_rect = self.rect.move(dx, dy)
        if not self.collide(new_rect, maze):
            self.rect = new_rect
            
        elif glitch_mode and not self.glitch_used:
            # Allow moving through one wall during glitch mode
            self.rect = new_rect
            self.glitch_used = True  # Mark glitch as used
            self.move_to_nearest_empty_space(maze) # Recalculate position
        
        # Keep player within screen bounds
        self.rect.clamp_ip(pygame.Rect(0, INFO_BAR_HEIGHT, WIDTH, HEIGHT - INFO_BAR_HEIGHT))

    def collide(self, new_rect, maze):
        if glitch_mode and not self.glitch_used:
            return False  # Ignore walls if glitch is active and unused
        
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False
        
    def draw(self):
        color = NEON_YELLOW if glitch_mode else NEON_BLUE
        rect_draw = self.rect.copy()
        pygame.draw.rect(screen, color, rect_draw)

    def move_to_nearest_empty_space(self, maze):
        """Move the player to the nearest empty space if inside a wall."""
        row, col = (self.rect.y - INFO_BAR_HEIGHT) // TILE, self.rect.x // TILE
        # Check if out of bounds due to glitch
        if not (0 <= row < len(maze) and 0 <= col < len(maze[0])):
            self.rect.x = TILE
            self.rect.y = TILE + INFO_BAR_HEIGHT
            return
            
        if maze[row][col] == 0:
            return  # Already in an empty space

        visited = set()
        queue = deque([(row, col, 0)])

        while queue:
            r, c, dist = queue.popleft()
            if maze[r][c] == 0:
                self.rect.x = c * TILE
                self.rect.y = r * TILE + INFO_BAR_HEIGHT
                return
            
            visited.add((r, c))
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and
                    (nr, nc) not in visited):
                    queue.append((nr, nc, dist + 1))
        
        # Fallback
        self.rect.x = TILE
        self.rect.y = TILE + INFO_BAR_HEIGHT

class Enemy:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = speed
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def update(self, maze):
        dx, dy = self.direction[0]*self.speed, self.direction[1]*self.speed
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        
        if not self.collide(new_x, new_y, maze):
            self.rect.x = new_x
            self.rect.y = new_y
        else:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def collide(self, new_x, new_y, maze):
        new_rect = pygame.Rect(new_x, new_y, TILE, TILE)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        rect_draw = self.rect.copy()
        pygame.draw.rect(screen, NEON_PINK, rect_draw)

class SpeedBoost:
    def __init__(self, x, y, tile_size, duration=300):
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.duration = duration
        self.active = False
        self.timer = 0
        self.color = (255, 255, 0)  # neon yellow

    def apply(self, player):
        self.active = True
        self.timer = self.duration
        player.speed = player.base_speed * 2
        self.rect.x = -100
        self.rect.y = -100

    def update(self, player):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.remove(player)
                self.active = False

    def remove(self, player):
        player.speed = player.base_speed

    def draw(self, screen):
        if not self.active:
            rect_draw = self.rect.copy()
            pygame.draw.rect(screen, self.color, rect_draw)

# --- Goal & Maze Drawing ---
def find_farthest_free_tile(maze, player_pos):
    rows, cols = len(maze), len(maze[0])
    free_tiles = []
    py, px = player_pos
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0 and (r, c) != player_pos:
                free_tiles.append((r, c))
    # sort by Manhattan distance
    free_tiles.sort(key=lambda t: abs(t[0]-py) + abs(t[1]-px), reverse=True)
    return free_tiles[0] if free_tiles else (1,2)

def draw_maze():
    global glow_timer
    for r in range(len(maze)):
        for c in range(len(maze[r])):
            x, y = c * TILE, r * TILE + INFO_BAR_HEIGHT
            if maze[r][c] == 1:
                pygame.draw.rect(screen, NEON_GREEN, (x, y, TILE, TILE), 2)
            elif maze[r][c] == 9:
                pygame.draw.rect(screen, NEON_PURPLE, (x, y, TILE, TILE))
                glow_size = int(3 + 2 * abs(math.sin(glow_timer)))
                pygame.draw.rect(screen, NEON_PINK, (x, y, TILE, TILE), glow_size)

# --- Reset & Game State ---
def reset_maze(num_enemies=1):
    global maze, player, enemies, goal_rect, goal_row, goal_col, speed_boost, glitch_timer, cooldown_timer, glitch_mode
    
    # Generate new maze
    maze = make_maze(rows, cols)
    add_loops(maze, extra_paths=10)

    # Ensure player start is always free and border walls are in place
    maze[1][1] = 0
    for r in range(rows):
        maze[r][0] = maze[r][cols-1] = 1
    for c in range(cols):
        maze[0][c] = maze[rows-1][c] = 1

    # Clear any existing goals first
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 9:
                maze[r][c] = 0

    # Place goal
    reachable = get_reachable_tiles(maze, (1, 1))
    valid_tiles = [pos for pos in reachable if pos != (1, 1)]
    if valid_tiles:
        goal_row, goal_col = random.choice(valid_tiles)
    else:
        goal_row, goal_col = 1, 2
        if maze[goal_row][goal_col] == 1: maze[goal_row][goal_col] = 0
    
    maze[goal_row][goal_col] = 9
    goal_rect.x = goal_col * TILE
    goal_rect.y = goal_row * TILE

    # Reset player speed to base speed and position
    player.speed = player.base_speed
    player.rect.x = TILE
    player.rect.y = TILE + INFO_BAR_HEIGHT

    # Reset glitch timers
    glitch_timer = 0
    glitch_mode = False
    cooldown_timer = 0

    # Reset enemies
    enemies.clear()
    for _ in range(num_enemies):
        free_tiles = [(r, c) for r in range(1, rows-1) for c in range(1, cols-1)
                      if maze[r][c] == 0 and (r, c) != (1, 1) and (r, c) != (goal_row, goal_col)]
        if free_tiles:
            er, ec = random.choice(free_tiles)
        else:
            er, ec = 3, 3
            if maze[er][ec] != 0: maze[er][ec] = 0
        enemies.append(Enemy(ec * TILE, er * TILE + INFO_BAR_HEIGHT, enemy_speed))

    # Place speed boost
    boost_tiles = [pos for pos in free_tiles if abs(pos[0]-(goal_row)) + abs(pos[1]-(goal_col)) > 5]
    if boost_tiles:
        br, bc = random.choice(boost_tiles)
        speed_boost = SpeedBoost(bc * TILE, br * TILE + INFO_BAR_HEIGHT, TILE)
    else:
        speed_boost = None

# --- Initialization ---
rows, cols = (HEIGHT - INFO_BAR_HEIGHT) // TILE, WIDTH // TILE
enemy_speed = 2
player = Player(TILE, TILE + INFO_BAR_HEIGHT)
enemies = []
goal_rect = pygame.Rect(0, 0, TILE, TILE)
goal_row, goal_col = 0, 0
speed_boost = None
level = 1
score = 0
glow_timer = 0
reset_maze(1)

# --- Main Loop ---
running = True
while running:
    dt = clock.tick(30) / 1000.0  # Time since last frame in seconds
    
    # Handle events for all states
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif state == 'PLAYING' and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state = 'PAUSED'
            elif event.key == pygame.K_g and glitch_timer <= 0 and cooldown_timer <= 0:
                glitch_mode = True
                glitch_timer = glitch_duration
                cooldown_timer = glitch_cooldown
                player.glitch_used = False
        elif state == 'PAUSED' and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = 'PLAYING'
            elif event.key == pygame.K_ESCAPE:
                state = 'MENU'
    
    if state == "MENU":
        draw_menu()
        state = "PLAYING"
        reset_maze(1)

    if state == "PLAYING":
        # --- Game Logic ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-player.speed, 0, maze)
        if keys[pygame.K_RIGHT]: player.move(player.speed, 0, maze)
        if keys[pygame.K_UP]: player.move(0, -player.speed, maze)
        if keys[pygame.K_DOWN]: player.move(0, player.speed, maze)

        for enemy in enemies:
            enemy.update(maze)

        if speed_boost and player.rect.colliderect(speed_boost.rect):
            speed_boost.apply(player)

        if speed_boost:
            speed_boost.update(player)

        # Handle glitch mode timing
        if glitch_mode:
            glitch_timer -= dt
            if glitch_timer <= 0:
                glitch_mode = False
                glitch_timer = 0
                player.move_to_nearest_empty_space(maze)

        if cooldown_timer > 0:
            cooldown_timer -= dt
            if cooldown_timer < 0:
                cooldown_timer = 0
        
        # Check goal collision
        player_row, player_col = (player.rect.y - INFO_BAR_HEIGHT) // TILE, player.rect.x // TILE
        if (0 <= player_row < len(maze) and 0 <= player_col < len(maze[0]) and
            maze[player_row][player_col] == 9):
            level += 1
            enemy_speed += 1
            num_enemies = 1 + (level // 3)
            score += 1
            reset_maze(num_enemies)
            
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                level = 1
                enemy_speed = 2
                score = 0
                player.speed = player.base_speed
                reset_maze(1)
                break
        
        # --- Drawing ---
        screen.fill(BLACK)
        draw_info_bar()
        draw_maze()
        player.draw()
        for enemy in enemies:
            enemy.draw()
        if speed_boost:
            speed_boost.draw(screen)

    elif state == "PAUSED":
        draw_pause()

    pygame.display.flip()
    glow_timer += 0.1

pygame.quit()
sys.exit()
