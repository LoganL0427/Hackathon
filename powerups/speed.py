import pygame

class SpeedBoost:
    def __init__(self, x, y, tile_size, duration=300):
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.duration = duration
        self.active = False
        self.timer = 0
        self.color = (255, 255, 0)  # neon yellow

    def apply(self, player, enemies):
        self.active = True
        self.timer = self.duration
        player.speed *= 2
        # hide power-up
        self.rect.x = -100
        self.rect.y = -100

    def update(self, player, enemies):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.remove(player, enemies)
                self.active = False

    def remove(self, player, enemies):
        player.speed //= 2

    def draw(self, screen):
        if not self.active:
            pygame.draw.rect(screen, self.color, self.rect)
