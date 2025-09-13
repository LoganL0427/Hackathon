import pygame, sys, random, math
# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 640, 480
TILE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Hacker")
clock = pygame.time.Clock()

# Colors (cyberpunk palette)
BLACK = (10, 10, 10)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)
glitch_mode = False

# --- Maze Layout ---
# 1 = wall, 0 = empty space
def make_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def carve(r, c):
        directions = [(0,2),(0,-2),(2,0),(-2,0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows and 0 < nc < cols and maze[nr][nc] == 1:
                maze[nr-dr//2][nc-dc//2] = 0  # remove wall between
                maze[nr][nc] = 0  # make new cell
                carve(nr, nc)
    
    # Start at 1,1
    maze[1][1] = 0
    carve(1, 1)
    
    # Make goal
    maze[rows-2][cols-2] = 9  # goal marker
    return maze

# Example
rows, cols = (HEIGHT // TILE) + 2, (WIDTH // TILE) + 2  # odd numbers work best
maze = make_maze(rows, cols)

def add_loops(maze, extra_paths=8):
    rows, cols = len(maze), len(maze[0])
    for _ in range(extra_paths):
        r = random.randrange(1, rows-1, 2)  # only cell rows
        c = random.randrange(1, cols-1, 2)  # only cell cols
        neighbors = []
        if maze[r-1][c] == 1: neighbors.append((r-1,c))
        if maze[r+1][c] == 1: neighbors.append((r+1,c))
        if maze[r][c-1] == 1: neighbors.append((r,c-1))
        if maze[r][c+1] == 1: neighbors.append((r,c+1))
        if neighbors:
            nr, nc = random.choice(neighbors)
            maze[nr][nc] = 0  # remove wall to create a loop

glitch_mode = False
glitch_duration = 2.0    # seconds the glitch lasts
glitch_timer = 0         # counts down when glitch is active
glitch_cooldown = 5.0    # seconds before next glitch
cooldown_timer = 0       # counts down while waiting

# --- Entities ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = 4

    def move(self, dx, dy):
        if not self.collide(dx, dy):
            self.rect.x += dx
            self.rect.y += dy

    def collide(self, dx, dy):
        if glitch_mode:
            return False  # ignore walls
        new_rect = self.rect.move(dx, dy)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                if maze[row][col] == 1:
                    wall_rect = pygame.Rect(col*TILE, row*TILE, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False

    def draw(self):
        # <-- Color changes dynamically based on glitch mode
        color = (255, 255, 0) if glitch_mode else NEON_BLUE
        pygame.draw.rect(screen, color, self.rect)
    

class Enemy:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.speed = speed
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    def update(self):
        if not self.collide(self.direction[0]*self.speed, self.direction[1]*self.speed):
            self.rect.x += self.direction[0]*self.speed
            self.rect.y += self.direction[1]*self.speed
        else:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                if maze[row][col] == 1:
                    wall_rect = pygame.Rect(col*TILE, row*TILE, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False
    def draw(self):
        pygame.draw.rect(screen, NEON_PINK, self.rect)



# --- Functions ---
def draw_maze():
    for row in range(0, len(maze)-1):
        for col in range(1, len(maze[row])-1):
            if maze[row][col] == 1:
                pygame.draw.rect(screen, NEON_GREEN, (col*TILE, row*TILE, TILE, TILE), 2)
            elif maze[row][col] == 9:  # Goal
                # Inner fill (deep neon purple)
                pygame.draw.rect(screen, (138, 43, 226), (col*TILE, row*TILE, TILE, TILE))  
    
                # Pulsing glow thickness using sine wave
                glow_size = int(3 + 2 * abs(math.sin(glow_timer)))
                pygame.draw.rect(screen, (255, 0, 255), (col*TILE, row*TILE, TILE, TILE), glow_size)

# Draw glitch cooldown bar
bar_width = 100
bar_height = 10
bar_x = 10
bar_y = 40

if cooldown_timer > 0:
    fill_width = int(bar_width * (1 - cooldown_timer / glitch_cooldown))
else:
    fill_width = bar_width

# Bar background
pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
# Bar fill
pygame.draw.rect(screen, (255, 255, 0), (bar_x, bar_y, fill_width, bar_height))

def reset_maze():
    global maze, player, enemies, goal_rect
    # 1. Generate a new random maze
    maze = make_maze(rows, cols)
    add_loops(maze, extra_paths=10)  # optional: multiple paths

    # Ensure outer border is walls
    for r in range(rows):
        maze[r][0] = 1
        maze[r][cols-1] = 1
    for c in range(cols):
        maze[0][c] = 1
        maze[rows-1][c] = 1

    # 2. Reset player to start
    player.rect.x = 1 * TILE
    player.rect.y = 1 * TILE

    # 3. Reset enemies
    enemies.clear()  # if you have a list of enemies
    enemies.append(Enemy(5*TILE, 5*TILE, enemy_speed))  # spawn new enemy
    
    # 4. Place goal
    player_pos = (player.rect.y // TILE, player.rect.x // TILE)
    goal_row, goal_col = find_farthest_free_tile(maze, player_pos)
    goal_rect.x = goal_col * TILE
    goal_rect.y = goal_row * TILE

def find_farthest_free_tile(maze, player_pos):
    rows, cols = len(maze), len(maze[0])
    free_tiles = []

    # Collect all free tiles
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0:  # empty space
                free_tiles.append((r, c))
    
    # Sort free tiles by distance from player, farthest first
    free_tiles.sort(key=lambda tile: abs(tile[0]-TILE) + abs(tile[1]-TILE), reverse=True)
    
    # Return the first tile (farthest)
    return free_tiles[0] if free_tiles else (1,1)



# --- Game State ---
enemy_speed = 2
player = Player(TILE, TILE)
enemies = []
goal_rect = pygame.Rect(0, 0, TILE, TILE)
reset_maze()
level = 1
score = 0

def quit_game():
    pygame.quit()
    sys.exit(0)

# --- Main Loop ---
running = True
glow_timer = 0

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g and glitch_timer <= 0 and cooldown_timer <= 0:
                glitch_timer = glitch_duration
                cooldown_timer = glitch_cooldown
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.move(-player.speed, 0)
    if keys[pygame.K_RIGHT]: player.move(player.speed, 0)
    if keys[pygame.K_UP]: player.move(0, -player.speed)
    if keys[pygame.K_DOWN]: player.move(0, player.speed)

    for enemy in enemies:
        enemy.update()

    # --- Check Win ---
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == 9:
                goal_rect = pygame.Rect(col*TILE, row*TILE, TILE, TILE)

    for enemy in enemies:
        if player.rect.colliderect(goal_rect):
            # handle losing
            enemies.clear()
            level += 1
            enemy_speed += 1  # <-- Adaptive AI difficulty
            reset_maze()
            score += 1
            player = Player(TILE, TILE)

    # --- Check Lose ---
    if player.rect.colliderect(enemy.rect):
        enemies.clear()
        level = 1
        enemy_speed = 2
        reset_maze()
        score = 0
        enemy = Enemy(TILE*5, TILE*5, enemy_speed)
        enemies.append(enemy)
        player = Player(TILE, TILE)

    # --- Draw ---
    screen.fill(BLACK)
    draw_maze()
    player.draw()
    for enemy in enemies:
        enemy.draw()

    # Display level
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Level: {level} | Enemy Speed: {enemy_speed} | Score: {score}", True, NEON_BLUE)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(30)
    glow_timer += 0.1  # controls the pulsing speed

    dt = 1 / 30

    if glitch_timer > 0:
        glitch_timer -= dt
        if glitch_timer < 0:
            glitch_timer = 0

    if cooldown_timer > 0:
        cooldown_timer -= dt
        if cooldown_timer < 0:
            cooldown_timer = 0

# Clean exit after loop ends
pygame.quit()
sys.exit()
