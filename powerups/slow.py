import pygame

class EnemySlow:
    def __init__(self, x, y, tile_size, duration=300, slow_factor=0.5):
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.duration = duration
        self.timer = 0
        self.active = False
        self.slow_factor = slow_factor
        self.color = (0, 255, 255)
        self.original_speeds = []  # store speeds when applied

    def apply(self, player, enemies):
        self.active = True
        self.timer = self.duration
        # Save original speeds
        self.original_speeds = [enemy.speed for enemy in enemies]
        # Slow enemies
        for enemy in enemies:
            enemy.speed *= self.slow_factor
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


    def draw(self, screen):
        if not self.active:
            pygame.draw.rect(screen, self.color, self.rect)