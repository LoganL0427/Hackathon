import pygame

class EnemySlow:
    def __init__(self, x, y, tile_size, duration=200, slow_factor=0.5, image=None):
        self.rect = pygame.Rect(x, y, tile_size - 2, tile_size - 2)
        self.duration = duration
        self.timer = 0
        self.active = False
        self.slow_factor = slow_factor
        self.color = (61, 46, 232) # blue
        self.original_speeds = []  # store speeds when applied
        self.image = image

    def apply(self, player, enemies):
        self.active = True
        self.timer = self.duration
        # Save original speeds
        self.original_speeds = [enemy.speed for enemy in enemies]
        # Slow enemies
        for enemy in enemies:
            enemy.speed = 1 # int(enemy.speed * self.slow_factor)
        # hide power-up
        self.rect.x = -100
        self.rect.y = -100

    def update(self, player, enemies):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.remove(enemies)
                self.active = False

    def remove(self, enemies):
        # Restore speeds, but only for enemies that still exist
        # and whose original speed was stored.
        if enemies:
            for i, enemy in enumerate(enemies):
                if i < len(self.original_speeds):
                    enemy.speed = self.original_speeds[i]

    def reset(self, player):
        self.active = False
        self.timer = 0
        self.original_speeds = []


    # def draw(self, screen):
    #     if not self.active:
    #         pygame.draw.rect(screen, self.color, self.rect, border_radius=22)

    
    def draw(self, screen):
        if not self.active:
            screen.blit(self.image, self.rect.topleft)