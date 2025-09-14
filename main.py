
import pygame, sys, random, math, collections, time
from powerups.speed import SpeedBoost
from powerups.slow import EnemySlow


# --- Setup ---
pygame.init()
pygame.mixer.init()  
WIDTH, HEIGHT = 800, 600
TILE = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Hacker")
clock = pygame.time.Clock()
state = "MENU"
INFO_BAR_HEIGHT = 40

# --- Load background music ---
try:
    pygame.mixer.music.load("media/background.mp3")  # adjust path as needed
    pygame.mixer.music.set_volume(0.3)  # optional: lower volume so it's not too loud
except pygame.error as e:
    print(f"Could not load music: {e}")


# --- Load Images ---
# Load and scale power-up images once
try:
    speed_boost_image = pygame.image.load('media/lightning2.png').convert_alpha()
    speed_boost_image = pygame.transform.scale(speed_boost_image, (TILE, TILE))
    enemy_slow_image = pygame.image.load('media/snowflake3.png').convert_alpha()
    enemy_slow_image = pygame.transform.scale(enemy_slow_image, (TILE, TILE))
    enemy_image = pygame.image.load('media/drone.png').convert_alpha()
    enemy_image = pygame.transform.scale(enemy_image, (TILE, TILE))
    player_image = pygame.image.load('media/player.png').convert_alpha()
    player_image = pygame.transform.scale(player_image, (TILE, TILE))
except pygame.error as e:
    print(f"Error loading image: {e}")
    speed_boost_image = None # or a default surface
    enemy_slow_image = None
    enemy_image = None
    player_image = None

# --- Load Fonts ---
TITLE_FONT = pygame.font.Font("media/PressStart2P-Regular.ttf", 60)
SUBTITLE_FONT = pygame.font.Font("media/PressStart2P-Regular.ttf", 21)
HELP_FONT = pygame.font.Font("media/PressStart2P-Regular.ttf", 18)
MENU_FONT = pygame.font.Font("media/PressStart2P-Regular.ttf", 39)


# Colors
BLACK = (37, 10, 54)
NEON_BLUE = (253, 245, 0)
NEON_PINK = (254, 63, 179)
NEON_GREEN = (19, 235, 221)
NEON_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# --- Draw Menus
def draw_scrolling_grid(offset):
    """Draw a scrolling neon grid background."""
    grid_color = (0, 255, 200)  # teal-ish neon
    spacing = 40  # grid spacing
    # Dark background
    screen.fill(BLACK)

    # Vertical lines
    for x in range(0, WIDTH, spacing):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)

    # Horizontal lines (scrolling)
    for y in range(-spacing, HEIGHT, spacing):
        pygame.draw.line(screen, grid_color, (0, y + offset), (WIDTH, y + offset), 1)

    # Overlay to dim so text pops
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)  # adjust transparency: 0 clear → 255 opaque
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

def draw_blur_glow_text(text, font, color, glow_color, pos):
    """Draws text with a soft blurred neon glow."""
    x, y = pos
    t = time.time()
    pulse_alpha = int(80 + 40 * math.sin(t * 1))  # 10-150 for glow intensity
    
    # Render the glow layers with increasing blur radius
    for radius in range(1, 8, 2):  # 1,3,5,7
        glow_surf = font.render(text, True, glow_color)
        glow_surf.set_alpha(pulse_alpha // radius)  # further layers are fainter
        # Draw at 8 directions around center
        for dx in (-radius, 0, radius):
            for dy in (-radius, 0, radius):
                if dx != 0 or dy != 0:
                    screen.blit(glow_surf, (x + dx, y + dy))
    
    # Draw main text on top
    screen.blit(font.render(text, True, color), pos)


def draw_menu():
    """Display Title Screen"""
    font = TITLE_FONT
    subtitle_font = SUBTITLE_FONT
    help_font = HELP_FONT
    
    offset = 0
    subtitle = subtitle_font.render("Press ENTER to Start", True, NEON_PINK)
    help_text = help_font.render("Press H for How to Play", True, WHITE)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_h:
                    draw_instructions()  # show how to play

        # Animate scrolling background
        offset = (offset + 0.35) % 40
        draw_scrolling_grid(offset)

        # Draw blurred glowing title
        draw_blur_glow_text("NEON HACKER", font, NEON_BLUE, NEON_BLUE,
                            ((WIDTH - font.size("NEON HACKER")[0]) // 2, HEIGHT // 3))

        # Draw subtitles
        screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 2))
        screen.blit(help_text, ((WIDTH - help_text.get_width()) // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(60)


def draw_instructions():
    """Display How to Play Menu"""
    screen.fill(BLACK)
    font_title = MENU_FONT
    font_text = HELP_FONT
    font_controls = SUBTITLE_FONT
    font_footer = HELP_FONT
    offset = 0

    # Title
    title = font_title.render("How to Play", True, NEON_BLUE)
 
    # Controls section
    controls_title = font_controls.render("Controls", True, NEON_PINK)

    controls = [
        "Arrow keys / WASD to move",
        "Avoid enemy drones",
        "Reach the purple portal to win",
        "Collect power-ups for boosts",
        "Press SPACE to glitch through walls",
        "Press ESC to return to Menu",
    ]

    # Footer
    footer = font_footer.render("Press ESC to return to Menu", True, NEON_BLUE)

    # Wait loop
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False

        # Animate offset
        offset = (offset + 0.35) % 40  # scrolling speed

        # Background
        draw_scrolling_grid(offset)

        # Text
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 80))
        y_offset = 120
        screen.blit(controls_title, ((WIDTH - controls_title.get_width()) // 2, y_offset + 60))
        y_offset += 100

        for line in controls:
            control_surface = font_text.render(line, True, WHITE)
            screen.blit(control_surface, ((WIDTH - control_surface.get_width()) // 2, y_offset))
            y_offset += 30

        
        screen.blit(footer, ((WIDTH - footer.get_width()) // 2, HEIGHT - 40))

        pygame.display.flip()


        clock.tick(60)



def draw_pause():
    """Display Pause Menu"""
    font = MENU_FONT
    pause_text = font.render("Paused", True, NEON_PINK)
    subtitle = SUBTITLE_FONT.render("ENTER to Resume, ESC for Menu", True, NEON_BLUE)
    screen.fill(BLACK)
    screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 2))
    pygame.display.flip()

def draw_lose(score):
    """Display Game Over Screen"""
    font = TITLE_FONT
    lose_text = font.render("GAME OVER", True, NEON_PINK)
    subtitle = SUBTITLE_FONT.render("ESC for Menu, ENTER to Restart", True, NEON_BLUE)
    score_text = MENU_FONT.render(f"Score: {score}", True, NEON_YELLOW)
    screen.fill(BLACK)
    screen.blit(lose_text, ((WIDTH - lose_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, HEIGHT // 2))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 2 + 80))  
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

# Glitch settings
glitch_mode = False
glitch_duration = 1.0    # seconds the glitch lasts
glitch_timer = 0         # counts down when glitch is active
glitch_cooldown = 5.0    # seconds before next glitch
cooldown_timer = 0       # counts down while waiting


# --- Entities ---
class Player:
    def __init__(self, x, y, image=None):
        self.rect = pygame.Rect(x, y + INFO_BAR_HEIGHT, TILE - 5, TILE - 5)
        self.speed = 4
        self.color = NEON_BLUE
        self.image = image
        self.glitch_used = False
        self.last_valid_position = (x, y)

    def move(self, dx, dy):
        moved = False
        # Standard pixel-by-pixel motion (needed for powerups like speed boost)
        if dx != 0:
            step = 1 if dx > 0 else -1
            for _ in range(abs(dx)):
                if not self.collide(step, 0):
                    self.rect.x += step
                    moved = True
                elif glitch_mode and not self.glitch_used:
                    # Glitch through one tile horizontally
                    self.last_valid_position = (self.rect.x, self.rect.y)
                    self.rect.x += step * 2 *TILE
                    self.glitch_used = True
                    moved = True
                    break
                else:
                    break

        if dy != 0:
            step = 1 if dy > 0 else -1
            for _ in range(abs(dy)):
                if not self.collide(0, step):
                    self.rect.y += step
                    moved = True
                elif glitch_mode and not self.glitch_used:
                    # Glitch through one tile vertically
                    self.last_valid_position = (self.rect.x, self.rect.y)
                    self.rect.y += step * 2 * TILE
                    self.glitch_used = True
                    moved = True
                    break
                else:
                    break

        # Correct invalid movement to prevent getting stuck in a wall
        if self.glitch_used:
            self.move_to_nearest_empty_space()

        return moved
    

    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False
        
    def move_to_nearest_empty_space(self):
        """Snap player back to last valid position if inside a wall tile."""
        # Get all corners of the player's rect
        corners = [
            (self.rect.left,  self.rect.top),
            (self.rect.right - 1, self.rect.top),
            (self.rect.left,  self.rect.bottom - 1),
            (self.rect.right - 1, self.rect.bottom - 1),
        ]

        stuck = False
        for (px, py) in corners:
            row = (py - INFO_BAR_HEIGHT) // TILE
            col = px // TILE
            if not (0 <= row < len(maze) and 0 <= col < len(maze[0])) or maze[row][col] == 1:
                    stuck = True
                    break

        if stuck and hasattr(self, "last_valid_position"):
            self.rect.x, self.rect.y = self.last_valid_position


    def draw(self):
        screen.blit(self.image, self.rect.topleft)



class Enemy:
    def __init__(self, x, y, speed, image=None):
        self.rect = pygame.Rect(x, y + INFO_BAR_HEIGHT, TILE, TILE)
        self.speed = int(speed)
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.image = image

    def update(self):
        dx, dy = self.direction[0], self.direction[1]  # just 1 step in a direction
        moved = False

        # Try moving one pixel at a time, up to self.speed
        for _ in range(self.speed):
            new_x = self.rect.x + dx
            new_y = self.rect.y + dy

            # Fix bottom boundary to account for info bar
            if 0 <= new_x <= WIDTH - TILE and 0 <= new_y <= HEIGHT - TILE - INFO_BAR_HEIGHT:
                if not self.collide(dx, dy):
                    self.rect.x = new_x
                    self.rect.y = new_y
                    moved = True
                else:
                    break  # stop if collision
            else:
                break  # stop if out of bounds

        # If enemy couldn’t move, pick a new direction
        if not moved:
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def collide(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                if maze[r][c] == 1:
                    wall_rect = pygame.Rect(c*TILE, r*TILE + INFO_BAR_HEIGHT, TILE, TILE)
                    if new_rect.colliderect(wall_rect):
                        return True
        return False

    
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

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
                pygame.draw.rect(screen, NEON_GREEN, (x, y, TILE, TILE), 3)
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
# In spawn_speed_boost function
def spawn_speed_boost():
    free_tiles = list(get_reachable_tiles(maze, (1, 1)))
    valid_tiles = [pos for pos in free_tiles if pos != (1, 1)]

    if valid_tiles:
        r, c = random.choice(valid_tiles)
    else:
        r, c = (1, 2)

    # Add INFO_BAR_HEIGHT to the y-coordinate when spawning
    return SpeedBoost(c * TILE, r * TILE + INFO_BAR_HEIGHT, TILE, image=speed_boost_image)

# In spawn_enemy_slow function
def spawn_enemy_slow():
    free_tiles = list(get_reachable_tiles(maze, (1, 1)))
    valid_tiles = [pos for pos in free_tiles if pos != (1, 1)]

    if valid_tiles:
        r, c = random.choice(valid_tiles)
    else:
        r, c = (1, 2)

    # Add INFO_BAR_HEIGHT to the y-coordinate when spawning
    return EnemySlow(c * TILE, r * TILE + INFO_BAR_HEIGHT, TILE, image=enemy_slow_image)



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
        # Set goal_rect position to match player coordinate system (*WITH* INFO_BAR_HEIGHT)
        goal_rect.x = goal_col * TILE
        goal_rect.y = goal_row * TILE + INFO_BAR_HEIGHT
    else:
        # Fallback - this should rarely happen
        goal_row, goal_col = 1, 2
        if maze[goal_row][goal_col] == 0:
            maze[goal_row][goal_col] = 9
        goal_rect.x = goal_col * TILE
        goal_rect.y = goal_row * TILE + INFO_BAR_HEIGHT

    # Reset player position
    player.rect.x = TILE
    player.rect.y = TILE + INFO_BAR_HEIGHT

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
        enemies.append(Enemy(ec*TILE, er*TILE, enemy_speed, image=enemy_image))  

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
rows, cols = (HEIGHT - INFO_BAR_HEIGHT)//TILE, WIDTH//TILE
enemy_speed = 2
player = Player(TILE, TILE, image=player_image)
enemies = []
goal_rect = pygame.Rect(0, 0, TILE, TILE)
goal_row, goal_col = 0, 0
level = 1
score = 0
final_score = 0
glow_timer = 0
powerups = []
reset_maze(1)

# Start playing music (loop indefinitely)
if not pygame.mixer.music.get_busy():  # avoids restarting if already playing
    pygame.mixer.music.play(-1)

# --- Main Loop ---
running = True
while running:
    if state == "MENU":
        draw_menu()
        state = "PLAYING"
        reset_maze(1)
    dt = 1/30
    events = list(pygame.event.get())

# ---- Check exit condition


    # Handle menu/escape logic using the same event list
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            pygame.mixer.music.stop()
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
        elif state=="LOSE" and event.type==pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state = "MENU"
            elif event.key == pygame.K_RETURN:
                state = "PLAYING"
                level, enemy_speed, score = 1, 2, 0
                reset_maze(1)

    if state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move(-player.speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move(player.speed, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move(0, -player.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move(0, player.speed)
        for enemy in enemies:
            enemy.update()
        
        # Check goal collision
        if player.rect.colliderect(goal_rect):
            level += 1
            enemy_speed += 1
            num_enemies = 1 + (level // 3)
            reset_maze(num_enemies)
            score += 1
            
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                enemies.clear()
                state = "LOSE"
                level = 1
                enemy_speed = 2
                final_score = score
                score = 0
                reset_maze(1)
                break

        # --- Power-Up Collision & Update ---
        for pu in powerups:
            if player.rect.colliderect(pu.rect) and not pu.active:
                pu.apply(player, enemies)
            pu.update(player, enemies)

        # Handle glitch input
        if keys[pygame.K_SPACE] and cooldown_timer <= 0 and not glitch_mode:
            glitch_mode = True
            glitch_timer = glitch_duration
            cooldown_timer = glitch_cooldown
            player.glitch_used = False

        # Update glitch timers
        if glitch_mode:
            glitch_timer -= dt
            if glitch_timer <= 0:
                glitch_mode = False
        else:
            if cooldown_timer > 0:
                cooldown_timer -= dt

        # --- Draw Game Elements --- 
        screen.fill(BLACK)
        # Draw info bar at the top
        font = HELP_FONT
        text = font.render(f"Level: {level}   Enemy Speed: {enemy_speed}   Score: {score}", True, NEON_BLUE)
        screen.blit(text, (10, 5))

        # Draw glitch cooldown bar
        bar_width, bar_height = 100, 10
        bar_x, bar_y = 10, 25

        if cooldown_timer > 0:
            fill_width = int(bar_width * (1 - cooldown_timer / glitch_cooldown))
        else:
            fill_width = bar_width

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))  # background
        pygame.draw.rect(screen, (255, 255, 0), (bar_x, bar_y, fill_width, bar_height))  # fill
        if glitch_mode:
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width, bar_height), 2)


        draw_maze()
        player.draw()
        for enemy in enemies:
            enemy.draw(screen)
        for pu in powerups:    
            pu.draw(screen)

    
    elif state == "PAUSED":
        draw_pause()
    elif state == "LOSE":
        draw_lose(final_score)



    pygame.display.flip()
    clock.tick(30)
    glow_timer += 0.1
